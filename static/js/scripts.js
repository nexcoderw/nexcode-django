
$(function () {

    "use strict";

    if (window.innerWidth > 991) {
        const tl = gsap.timeline({
            scrollTrigger: {
                trigger: ".testimonials-ca .sec-head",
                start: "top",
                endTrigger: ".testimonials-ca .container",
                end: "bottom bottom",
                pin: true,
                pinSpacing: false
            }
        });
    }

    gsap.registerPlugin(ScrollTrigger);

    ScrollTrigger.create({
        trigger: ".work-ca .sec-lg-head",
        start: "center center",
        endTrigger: ".work-ca",
        end: "bottom bottom",
        pin: true,
    });

    // Services active

    $('.services-cst .item').on('mouseenter', function () {
        $('.services-cst .item').removeClass('active');
        $(this).addClass('active');

        if ($(this).hasClass('active')) {
            return false;
        }
    });

});


$(function () {
    var width = $(window).width();
    if (width > 991) {

        "use strict";

        $(function () {
            let cards = gsap.utils.toArray(".cards .card-item");

            let stickDistance = 0;

            let firstCardST = ScrollTrigger.create({
                trigger: cards[0],
                start: "center center"
            });

            let lastCardST = ScrollTrigger.create({
                trigger: cards[cards.length - 1],
                start: "bottom bottom"
            });

            cards.forEach((card, index) => {
                var scale = 1 - (cards.length - index) * 0;
                let scaleDown = gsap.to(card, { scale: scale, 'transform-origin': '"50% ' + (lastCardST.start + stickDistance) + '"' });

                ScrollTrigger.create({
                    trigger: card,
                    start: "center center",
                    end: () => lastCardST.start + stickDistance,
                    pin: true,
                    pinSpacing: false,
                    ease: "none",
                    animation: scaleDown,
                    toggleActions: "restart none none reverse"
                });
            });
        });

    }
});