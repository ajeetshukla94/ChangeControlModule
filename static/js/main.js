(function($) {
    "use strict";
    $('.navbar-sidenav [data-toggle="tooltip"]').tooltip({
        boundary: 'window',
        template: '<div class="tooltip navbar-sidenav-tooltip" role="tooltip"><div class="arrow"></div><div class="tooltip-inner"></div></div>'
    });

    $(".navbar-sidenav .nav-link-collapse").on('click', function(e) {
        e.preventDefault();
        $("body").removeClass("sidenav-toggled");
    });

    $('body.fixed-nav .navbar-sidenav, body.fixed-nav .sidenav-toggler, body.fixed-nav .navbar-collapse').on('mousewheel DOMMouseScroll', function(e) {
        var e0 = e.originalEvent,
            delta = e0.wheelDelta || -e0.detail;
        this.scrollTop += (delta < 0 ? 1 : -1) * 30;
        e.preventDefault();
    });
})(jQuery);