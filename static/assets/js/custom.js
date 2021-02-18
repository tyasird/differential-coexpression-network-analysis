/***************************************************************************************************************
 ||||||||||||||||||||||||||||        CUSTOM SCRIPT FOR THE COV                      |||||||||||||||||||||||||||
 ****************************************************************************************************************
 ||||||||||||||||||||||||||||              TABLE OF CONTENT                  ||||||||||||||||||||||||||||||||||||
 ****************************************************************************************************************
 ****************************************************************************************************************

 01. Elements Animation
 02. prealoader
 03. Odometer JS
 04. selectdropdown
 05. LightBox
 06. searchpopuptoggler
 07. customcursoroverlay
 08. sidemenutoggler
 09. update clock
 10. isotope
 11. Portfolio Tabs
 12. scrolltotop
 13. cart product increasing
 14. pricefilter
 15. owl-carousel


 ****************************************************************************************************************
 ||||||||||||||||||||||||||||            End TABLE OF CONTENT                ||||||||||||||||||||||||||||||||||||
 ****************************************************************************************************************/


"use strict";

$(".start_network_analyze_button").click(function (e) {
    $('.preloader').show()

});


function updateRangeInput(val) {
    document.getElementById('rangeInput').value = val;
}


function doAjax() {
    let status_hash = $('#status_hash').val()
    $.ajax({
        type: 'GET',
        url: 'status/' + status_hash,
        dataType: 'text',
        success: function (data) {
            $('.wait').html(data);
        },
        complete: function (data) {
            setTimeout(doAjax, 1000);
        },
        error: function(jqXHR, textStatus, errorThrown) {
          console.log(textStatus, errorThrown);
        }
    });
}


$("#start_analyze_button").click(function (e) {

    var $myForm = $('#do_analyze');
    if ($myForm[0].checkValidity()) {

        setTimeout(doAjax, 1000);
        $('.preloader').show()
        $('#start_analyze_button').click();



    }


});

$('.about_tool_link').on('click', function (e) {
    $('.side-menu__block').addClass('active');
    e.preventDefault();
});


/*-----------------Elements Animation-----------------*/
if ($('.wow').length) {
    var wow = new WOW({
        boxClass: 'wow', // animated element css class (default is wow)
        animateClass: 'animated', // animation css class (default is animated)
        offset: 0, // distance to the element when triggering the animation (default is 0)
        mobile: false, // trigger animations on mobile devices (default is true)
        live: true // act on asynchronously loaded content (default is true)
    });
    wow.init();
}

/*-----------------Elements Animation-----------------*/

function prealoader() { // makes sure the whole site is loaded
    if ($('.preloader').length) {
        $('.preloader').delay(200).fadeOut(500);
    }
}

/*-----------------Odometer JS-----------------*/
function odometer() {
    $('.odometer').appear(function (e) {
        var odo = $(".odometer");
        odo.each(function () {
            var countNumber = $(this).attr("data-count");
            $(this).html(countNumber);
        });
    });
}

/*-----------------Odometer JS-----------------*/

/*-----------------selectdropdown-----------------*/
function selectdropdown() {
    $("#location").selectmenu();
    $("#age").selectmenu();
    $("#doctors").selectmenu();
    $("#topic").selectmenu();
    $("#time").selectmenu();
    $("#appointmentdate").datepicker();
}


/*-----------------LightBox-----------------*/
//LightBox / Fancybox
if ($('.lightbox-image').length) {
    $('.lightbox-image').fancybox({
        openEffect: 'fade',
        closeEffect: 'fade',
        helpers: {
            media: {}
        }
    });
}

/*-----------------scrollnav-----------------*/
function scrollnav() {
    //Add One Page nav
    if ($('.scroll-nav').length) {
        $('.scroll-nav ul').onePageNav();
    }
}


function dataTable1() {
    if ($('#outbreaks').length) {
        $('#outbreaks').dataTable({
            "pageLength": 25
        });
    }
}

function dataTable2() {
    if ($('#outbreakstwo').length) {
        $('#outbreakstwo').dataTable({
            "pageLength": 25
        });
    }
}

function dataTable3() {
    if ($('#outbreaksthree').length) {
        $('#outbreaksthree').dataTable({
            "pageLength": 25
        });
    }
}


$(function () {

    $(".progress").each(function () {

        var value = $(this).attr('data-value');
        var left = $(this).find('.progress-left .progress-bar');
        var right = $(this).find('.progress-right .progress-bar');

        if (value > 0) {
            if (value <= 50) {
                right.css('transform', 'rotate(' + percentageToDegrees(value) + 'deg)')
            } else {
                right.css('transform', 'rotate(180deg)')
                left.css('transform', 'rotate(' + percentageToDegrees(value - 50) + 'deg)')
            }
        }

    })

    function percentageToDegrees(percentage) {

        return percentage / 100 * 360

    }

});


/*-----------------customcursoroverlay-----------------*/
function customcursoroverlay() {

    if ($('.custom-cursor__overlay').length) {

        // / cursor /
        var cursor = $(".custom-cursor__overlay .cursor"),
            follower = $(".custom-cursor__overlay .cursor-follower");

        var posX = 0,
            posY = 0;

        var mouseX = 0,
            mouseY = 0;

        TweenMax.to({}, 0.016, {
            repeat: -1,
            onRepeat: function () {
                posX += (mouseX - posX) / 9;
                posY += (mouseY - posY) / 9;

                TweenMax.set(follower, {
                    css: {
                        left: posX - 22,
                        top: posY - 22
                    }
                });

                TweenMax.set(cursor, {
                    css: {
                        left: mouseX,
                        top: mouseY
                    }
                });

            }
        });

        $(document).on("mousemove", function (e) {
            var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            mouseX = e.pageX;
            mouseY = e.pageY - scrollTop;
        });
        $("button, a").on("mouseenter", function () {
            cursor.addClass("active");
            follower.addClass("active");
        });
        $("button, a").on("mouseleave", function () {
            cursor.removeClass("active");
            follower.removeClass("active");
        });
        $(".custom-cursor__overlay").on("mouseenter", function () {
            cursor.addClass("close-cursor");
            follower.addClass("close-cursor");
        });
        $(".custom-cursor__overlay").on("mouseleave", function () {
            cursor.removeClass("close-cursor");
            follower.removeClass("close-cursor");
        });
    }

}

/*-----------------sidemenutoggler-----------------*/
function sidemenutoggler() {
    if ($('.side-menu__toggler').length) {
        $('.side-menu__toggler').on('click', function (e) {
            $('.side-menu__block').addClass('active');
            e.preventDefault();
        });
    }
}

/*-----------------sidemenublockoverlay-----------------*/
function sidemenublockoverlay() {

    if ($('.side-menu__block-overlay').length) {
        $('.side-menu__block-overlay').on('click', function (e) {
            $('.side-menu__block').removeClass('active');
            e.preventDefault();
        });
    }
}

/*-----------------sidemenublockoverlay-----------------*/
function sidemenuclose() {

    if ($('.side_menu_close').length) {
        $('.side_menu_close').on('click', function (e) {
            $('.side-menu__block').removeClass('active');
            e.preventDefault();
        });
    }
}


//Update Header Style and Scroll to Top

function scrolltotop() {

    $(document).ready(function () {
        $(window).scroll(function () {
            if ($(this).scrollTop() > 100) {
                $('#scroll').fadeIn();
            } else {
                $('#scroll').fadeOut();
            }
        });
        $('#scroll').click(function () {
            $("html, body").animate({
                scrollTop: 0
            }, 600);
            return false;
        });
    });

}

scrolltotop();

$(document).ready(function () {

    var CurrentUrl = document.URL;
    var CurrentUrlEnd = CurrentUrl.split('/').filter(Boolean).pop();
    $("#navbarnav .nav_item a").each(function () {
        var ThisUrl = $(this).attr('href');
        var ThisUrlEnd = ThisUrl.split('/').filter(Boolean).pop();

        if (ThisUrlEnd == CurrentUrlEnd) {
            $(this).closest('.nav_item').addClass('active')
        }
    });

});


/*-----------------Portfolio Tabs-----------------*/
if ($('.faq_tabs').length) {
    $('.faq_tabs .faq_tabs_btn .f_tabs_btn').on('click', function (e) {
        e.preventDefault();
        var target = $($(this).attr('data-tab'));

        if ($(target).hasClass('actve-tab')) {
            return false;
        } else {
            $('.faq_tabs .faq_tabs_btn .f_tabs_btn').removeClass('active-btn');
            $(this).addClass('active-btn');
            $('.faq_tabs .f_tabs_content .f_tab').removeClass('active-tab');
            $(target).addClass('active-tab');
        }
    });
}

/*-----------------Portfolio Tabs-----------------*/
if ($('.latest_updates_tabs').length) {
    $('.latest_updates_tabs .upd_tabs_btn .u_tabs_btn').on('click', function (e) {
        e.preventDefault();
        var target = $($(this).attr('data-tab'));

        if ($(target).hasClass('actve-tab')) {
            return false;
        } else {
            $('.latest_updates_tabs .upd_tabs_btn .u_tabs_btn').removeClass('active-btn');
            $(this).addClass('active-btn');
            $('.latest_updates_tabs .upd_tabs_content .u_tab').removeClass('active-tab');
            $(target).addClass('active-tab');
        }
    });
}
/*-----------------Portfolio Tabs-----------------*/


/*--------------one_items------------------*/
function mainslider() {
    if ($('.main_slider').length) {
        $('.main_slider').owlCarousel({
            loop: true,
            margin: 0,
            nav: true,
            dots: true,
            center: false,
            autoplay: true,
            animateOut: 'fadeOut',
            animateIn: 'fadeIn',
            active: true,
            smartSpeed: 1000,
            autoplayTimeout: 7000,
            navText: ['<span class="clearfix prev flaticon-left"></span>', '<span class="clearfix flaticon-right"></span>'],

            responsive: {
                0: {
                    items: 1
                },
                800: {
                    items: 1
                },

                1000: {
                    items: 1
                },
                1200: {
                    items: 1
                }
            }
        });
    }
}

/*--------------four_items------------------*/
function fouritems() {
    if ($('.four_items').length) {
        $('.four_items').owlCarousel({
            loop: true,
            margin: 0,
            nav: true,
            dots: true,
            center: false,
            autoplay: true,
            smartSpeed: 3000,
            autoplayTimeout: 4000,
            navText: ['<span class="clearfix prev linearicons-chevron-left"></span>', '<span class="clearfix linearicons-chevron-right"></span>'],

            responsive: {
                0: {
                    items: 1
                },
                800: {
                    items: 2
                },

                1200: {
                    items: 3
                },
                1400: {
                    items: 4
                }
            }
        });
    }
}

/*--------------four_items------------------*/
function six_items() {
    if ($('.six_items').length) {
        $('.six_items').owlCarousel({
            loop: true,
            margin: 0,
            nav: true,
            dots: true,
            center: false,
            autoplay: true,
            smartSpeed: 3000,
            autoplayTimeout: 4000,
            navText: ['<span class="clearfix prev linearicons-chevron-left"></span>', '<span class="clearfix linearicons-chevron-right"></span>'],

            responsive: {
                0: {
                    items: 2
                },
                600: {
                    items: 2
                },
                800: {
                    items: 3
                },

                1200: {
                    items: 4
                },
                1400: {
                    items: 6
                }
            }
        });
    }
}


/*--------------three_items_center------------------*/
function threeitemscenter() {
    if ($('.three_items_center').length) {
        $('.three_items_center').owlCarousel({
            loop: true,
            margin: 0,
            nav: true,
            dots: true,
            center: true,
            autoplay: true,
            smartSpeed: 3000,
            autoplayTimeout: 4000,
            navText: ['<span class="clearfix prev linearicons-chevron-left"></span>', '<span class="clearfix linearicons-chevron-right"></span>'],

            responsive: {
                0: {
                    items: 1
                },
                800: {
                    items: 2
                },

                1000: {
                    items: 3
                },
                1200: {
                    items: 3,
                    margin: 0,
                }
            }
        });
    }
}

/*--------------three_items------------------*/
function threeitems() {
    if ($('.three_items').length) {
        $('.three_items').owlCarousel({
            loop: true,
            margin: 0,
            nav: true,
            dots: true,
            center: false,
            autoplay: true,
            smartSpeed: 3000,
            autoplayTimeout: 4000,
            navText: ['<span class="clearfix prev linearicons-chevron-left"></span>', '<span class="clearfix linearicons-chevron-right"></span>'],

            responsive: {
                0: {
                    items: 1
                },
                800: {
                    items: 2
                },

                1000: {
                    items: 3
                },
                1200: {
                    items: 3
                }
            }
        });
    }
}


/*--------------two_items------------------*/
function twoitems() {
    if ($('.two_items').length) {
        $('.two_items').owlCarousel({
            loop: true,
            margin: 0,
            nav: true,
            dots: true,
            center: false,
            autoplay: true,
            smartSpeed: 3000,
            autoplayTimeout: 4000,
            navText: ['<span class="clearfix prev linearicons-chevron-left"></span>', '<span class="clearfix linearicons-chevron-right"></span>'],

            responsive: {
                0: {
                    items: 1
                },
                800: {
                    items: 2
                },

                1000: {
                    items: 3
                },
                1200: {
                    items: 2
                }
            }
        });
    }
}

/*--------------one_items------------------*/
function oneitems() {
    if ($('.one_items').length) {
        $('.one_items').owlCarousel({
            loop: true,
            margin: 0,
            nav: true,
            dots: true,
            center: false,
            autoplay: true,
            smartSpeed: 3000,
            autoplayTimeout: 4000,
            navText: ['<span class="clearfix prev linearicons-chevron-left"></span>', '<span class="clearfix linearicons-chevron-right"></span>'],

            responsive: {
                0: {
                    items: 1
                },
                800: {
                    items: 1
                },

                1000: {
                    items: 1
                },
                1200: {
                    items: 1
                }
            }
        });
    }
}


// Dom Ready Function
jQuery(document).on('ready', function () {
    (function ($) {
        oneitems();
        scrollnav();
        twoitems();
        odometer();
        threeitems();
        threeitemscenter();
        fouritems();
        six_items();
        mainslider();
        selectdropdown();
        customcursoroverlay();
        sidemenutoggler();
        sidemenublockoverlay();
        sidemenuclose();
        dataTable1();
        dataTable2();
        dataTable3();
    })(jQuery);
});
/* ==========================================================================
   When document is Scrollig, do
   ========================================================================== */
// Instance Of Fuction while Window Load event
jQuery(window).on('load', function () {
    (function ($) {
        prealoader();
    })(jQuery);
});
