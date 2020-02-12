$(document).ready(() => {

    // Sidebar
    // Sidebar Menu
    setTimeout(function () {
        $(".vertical-nav-menu").metisMenu();
    }, 100);

    // Search wrapper trigger

    $('.search-icon').click(function () {
        $(this).parent().parent().addClass('active');
    });

    $('.search-wrapper .close').click(function () {
        $(this).parent().removeClass('active');
    });

    // Stop Bootstrap 4 Dropdown for closing on click inside

    $('.dropdown-menu').on('click', function (event) {
        var events = $._data(document, 'events') || {};
        events = events.click || [];
        for (var i = 0; i < events.length; i++) {
            if (events[i].selector) {

                if ($(event.target).is(events[i].selector)) {
                    events[i].handler.call(event.target, event);
                }

                $(event.target).parents(events[i].selector).each(function () {
                    events[i].handler.call(this, event);
                });
            }
        }
        event.stopPropagation(); //Always stop propagation
    });

    $(function () {
        $('[data-toggle="popover"]').popover();
    });

    // BS4 Tooltips

    $(function () {
        $('[data-toggle="tooltip"]').tooltip();
    });

    $('.mobile-toggle-nav').click(function () {
        $(this).toggleClass('is-active');
        $('.app-container').toggleClass('sidebar-mobile-open');
    });

    $('.mobile-toggle-header-nav').click(function () {
        $(this).toggleClass('active');
        $('.app-header__content').toggleClass('header-mobile-open');
    });

    // Responsive

    var resizeClass = function () {
        var win = document.body.clientWidth;
        const app_container = $('.app-container');
        if (win < 1250) {
            app_container.addClass('closed-sidebar-mobile closed-sidebar');
        } else {
            app_container.removeClass('closed-sidebar-mobile closed-sidebar');
            app_container.addClass('closed-sidebar');
        }
    };


    $(window).on('resize', function () {
        resizeClass();
    });

    $(".close-sidebar-btn").click(() => $(".app-container").toggleClass("closed-sidebar"));
    resizeClass();

});