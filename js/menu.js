/* From: http://www.kriesi.at/archives/create-a-multilevel-dropdown-menu-with-css-and-improve-it-via-jquery */

function mainmenu(){
/*$("nav ul").css({display: "none"}); // Opera Fix*/
$("nav li").hover(function(){
		$(this).find('ul:first').css({visibility: "visible",display: "none"}).show(200);
		},function(){
		$(this).find('ul:first').css({visibility: "hidden"});
		});
}

/* From: http://www.codeography.com/2012/10/11/convert-timestamps-localtime-jquery.html */

(function() {
  (function($) {
    return $.fn.localtime = function() {
      var fmtDate, fmtZero;
      fmtZero = function(str) {
        return ('0' + str).slice(-2);
      };
      fmtDate = function(d) {
        var hour, meridiem;
        hour = d.getHours();
        if (hour < 12) {
          meridiem = "AM";
        } else {
          meridiem = "PM";
        }
        if (hour === 0) { hour = 12; }
        if (hour > 12) { hour = hour - 12; }
        return hour + ":" + fmtZero(d.getMinutes()) + " " + meridiem + " " + (d.getMonth() + 1) + "/" + d.getDate() + "/" + d.getFullYear();
      };
      return this.each(function() {
        var tagText;
        tagText = $(this).html();
        $(this).html(fmtDate(new Date(tagText)));
        return $(this).attr("title", tagText);
      });
    };
  })(jQuery);
}).call(this);

$(document).ready(function(){					
	mainmenu();
	$("span.localtime").localtime();
});

function updateNeed(field, val, idval) {
    newval = +val - +field.value;
    document.getElementById(idval).value = newval;
    if ( newval > 0 ) {
        document.getElementById(idval).setAttribute('data-need', 'more');
    }
    else {
        document.getElementById(idval).setAttribute('data-need', 'done');
    }
}

function updateBank(api_key) {
    var dict = {}
    var done = 2

    $(['materials', 'bank']).each(function() {
        var endpoint = this;
        $.getJSON('https://api.guildwars2.com/v2/account/' + endpoint + '?access_token=' + api_key, function(data) {
            //for item in data
            $.each(data, function(value) {
                if(data[value]) {
                    var exists = dict[data[value].id];
                    if(!exists) {
                        dict[data[value].id] = 0;
                    }
                    dict[data[value].id] += data[value].count
                }
            });
            done -= 1
            if (done == 0) {

                for (var key in dict) {
                    if (dict.hasOwnProperty(key)) {
                        //if item.id in page
                        idval = key + 'ih';
                        if (document.getElementById(idval)) {
                            //update element to item.count
                            document.getElementById(idval).value = dict[key];
                            document.getElementById(idval).oninput();
                        }
                    }
                }
            }
        });
    });
}