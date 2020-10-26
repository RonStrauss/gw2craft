#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: Jeremy Parks
Purpose: Get current price data
Note: Requires Python 3.7.x
'''

import json
import os
import sys
import time

from auto_gen import Items
# so we can set custom headers
from multiprocessing import Pool
import urllib.request, urllib.error, urllib.parse
from random import randint, choice
import socket


def gw2apilistworker(input_url):
	baseURL = input_url[0]
	ids = input_url[1]
	version = input_url[2]
	outdict = {}
	getdata = True
	temp = []
	while getdata:
		try:
			req = urllib.request.Request(baseURL + ",".join(str(i) for i in ids))
			req.add_header('User-agent', version)
			f = urllib.request.urlopen(req, timeout=socket.getdefaulttimeout())
			temp = json.load(f)
			getdata = False
		except Exception as err:
			print('ERROR: %s.' % str(err))
			time.sleep(randint(1, 10))
	for sitem in temp:
		item = sitem["id"]
		# set value to greater of buy and vendor.  If 0 set to minimum sell value
		w = Items.ilist[item]['vendor_value']
		sellMethod = 0
		if sitem['buys']['unit_price'] * .85 > w:
			w = int(sitem['buys']['unit_price'] * .85)
			sellMethod = 1
		if w == 0:
			w = int(sitem['sells']['unit_price'] * .85)
			sellMethod = 2

		# Save all the information we care about
		outdict[item] = {'w': w, 'cost': sitem['sells']['unit_price'], 'recipe': None,
						 'rarity': Items.ilist[item]['rarity'], 'type': Items.ilist[item]['type'],
						 'icon': Items.ilist[item]['img_url'],
						 'output_item_count': Items.ilist[item]['output_item_count'], 'sellMethod': sellMethod,
						 "discover": [], 'whitelist': sitem[u'whitelisted']}

		if outdict[item]['type'] == 'UpgradeComponent' and outdict[item]['rarity'] == 'Exotic':
			outdict[item]['rarity'] = 'Exotic UpgradeComponent'

		# if the item has a low supply, ignore it
		if sitem['sells']['quantity'] <= 50:
			outdict[item]['cost'] = sys.maxsize

	return outdict


def gw2api():
	socket.setdefaulttimeout(5)
	listingURL = "https://api.guildwars2.com/v2/commerce/listings"
	req = urllib.request.Request(listingURL)
	user_agents = [
		'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
		'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
		'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
		'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'
	]
	version = choice(user_agents)
	req.add_header('User-agent', version)
	f = urllib.request.urlopen(req, timeout=socket.getdefaulttimeout())
	temp = json.load(f)
	valid = []
	invalid = []
	for item in list(Items.ilist.keys()):
		if item in temp:
			valid.append(item)
		else:
			invalid.append(item)

	baseURL = "https://api.guildwars2.com/v2/commerce/prices?ids="

	p = Pool()
	procs = [p.map(gw2apilistworker, [(baseURL, valid[i:i + 200], version) for i in range(0, len(valid), 200)])]

	resultdict = {}
	for p in procs:
		for i in p:
			resultdict.update(i)

	for item in invalid:
		resultdict[item] = {'w': 0, 'cost': sys.maxsize, 'recipe': None, 'rarity': Items.ilist[item]['rarity'],
							'type': Items.ilist[item]['type'], 'icon': Items.ilist[item]['img_url'],
							'output_item_count': Items.ilist[item]['output_item_count'], 'sellMethod': 0,
							"discover": [], 'whitelist': False}
		if resultdict[item]['type'] == 'UpgradeComponent' and resultdict[item]['rarity'] == 'Exotic':
			resultdict[item]['rarity'] = 'Exotic UpgradeComponent'

	return resultdict


# add some costs data to gcList
def appendCosts():
	cList = {}
	getprices = True  # loop variable to loop until we get a return

	count = 10  # loop variable to terminate loop after x attempts
	while getprices and count:
		try:
			cList = gw2api()
			getprices = False
		except Exception as err:
			print('ERROR: %s.' % str(err))
			time.sleep(randint(1, 10))
			count -= 1

	# if loop exited because of this variable we didn't get any data, terminate
	if not count:
		sys.exit(0)

	cList[19792]['cost'] = 8  # Spool of Jute Thread
	cList[19789]['cost'] = 16  # Spool of Wool Thread
	cList[19794]['cost'] = 24  # Spool of Cotton Thread
	cList[19793]['cost'] = 32  # Spool of Linen Thread
	cList[19791]['cost'] = 48  # Spool of Silk Thread
	cList[19790]['cost'] = 64  # Spool of Gossamer Thread
	cList[19704]['cost'] = 8  # Lump of Tin
	cList[19750]['cost'] = 16  # Lump of Coal
	cList[19924]['cost'] = 48  # Lump of Primordium
	cList[12157]['cost'] = 8  # Jar of Vinegar
	cList[12151]['cost'] = 8  # Packet of Baking Powder
	cList[12158]['cost'] = 8  # Jar of Vegetable Oil
	cList[12153]['cost'] = 8  # Packet of Salt
	cList[12155]['cost'] = 8  # Bag of Sugar
	cList[12156]['cost'] = 8  # Jug of Water
	cList[12324]['cost'] = 8  # Bag of Starch
	cList[12136]['cost'] = 8  # Bag of Flour
	cList[8576]['cost'] = 16  # Bottle of Rice Wine
	cList[12271]['cost'] = 8  # Bottle of Soy Sauce
	cList[13010]['cost'] = 496  # "Minor Rune of Holding"
	cList[13006]['cost'] = 1480  # "Rune of Holding"
	cList[13007]['cost'] = 5000  # "Major Rune of Holding"
	cList[13008]['cost'] = 20000  # "Greater Rune of Holding"
	cList[70647]['cost'] = 32  # "Crystalline Bottle"
	cList[75762]['cost'] = 104  # "Bag of Mortar"
	cList[1000352]['cost'] = 2400  # Basic Flagpole Purchased from the commendation vendor.
	cList[1000589]['cost'] = 2400  # Basic Boulder Purchased from the basic decoration vendor.
	cList[1000574]['cost'] = 2400  # Basic Column Purchased from the basic decoration vendor.
	cList[1000601]['cost'] = 2400  # Basic Basket Purchased from the basic decoration vendor.
	cList[1000403]['cost'] = 2400  # White Balloon Purchased from the basic decoration vendor.
#	cList[1000376][u'cost'] = 2400  # Basic Fountain Purchased from the basic decoration vendor.
	cList[1000223]['cost'] = 2400  # Basic Planter Purchased from the basic decoration vendor.
	cList[1000548]['cost'] = 2400  # Basic Pedestal Purchased from the basic decoration vendor.
	cList[1000209]['cost'] = 2400  # Basic Shrub Purchased from the basic decoration vendor.
	cList[1000516]['cost'] = 2400  # Basic Crate Purchased from the basic decoration vendor.
	cList[1000620]['cost'] = 2400  # Basic Tree Purchased from the basic decoration vendor.
	cList[1000202]['cost'] = 2400  # Basic Table
	cList[1000582]['cost'] = 2400  # Basic Torch Purchased from the basic decoration vendor.
	cList[1000437]['cost'] = 2400  # Basic Candle Purchased from the basic decoration vendor.
	cList[1000413]['cost'] = 2400  # Basic Chair Purchased from the basic decoration vendor.
	cList[1000224]['cost'] = 2400  # Basic Bookshelf Purchased from the basic decoration vendor.
	cList[46747]['cost'] = 150  # Thermocatalytic Reagent.
	if 62942 in cList:
		cList[62942]['cost'] = 8  # Crafter's Backpack Frame
	# [u'Bell Pepper',u'Basil Leaf',u'Ginger Root',u'Tomato',u'Bowl of Sour Cream',u'Rice Ball',u'Packet of Yeast',u'Glass of Buttermilk',u'Cheese Wedge',u"Almond",u"Apple",u"Avocado",u"Banana",u"Black Bean",u"Celery Stalk",u"Cherry",u"Chickpea",u"Coconut",u"Cumin",u"Eggplant",u"Green Bean",u"Horseradish Root",u"Kidney Bean",u"Lemon",u"Lime",u"Mango",u"Nutmeg Seed",u"Peach",u"Pear",u"Pinenut",u"Shallot"]
	karma = [12235, 12245, 12328, 12141, 12325, 12145, 12152, 12137, 12159, 12337, 12165, 12340, 12251, 12237, 12240,
			 12338, 12515, 12350, 12256, 12502, 12232, 12518, 12239, 12252, 12339, 12543, 12249, 12503, 12514, 12516,
			 12517]
	for item in karma:
		cList[item]['cost'] = 0
	cList[12132]['cost'] = 99999999  # Loaf of Bread is soulbound, cheat to make it not purchased

	if os.isatty(sys.stdin.fileno()):
		print(len(list(cList.keys())))  # print number of items used by the guides

	return cList
