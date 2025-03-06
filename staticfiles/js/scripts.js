$(function () {

    "use strict";

    var team = new Swiper(".team-marq .team-swiper", {
        slidesPerView: 4,
        spaceBetween: 50,
        centeredSlides: true,
        speed: 8000,
        autoplay: {
            delay: 0,
        },
        loop: true,
        allowTouchMove: false,
        disableOnInteraction: true,
        breakpoints: {
            0: {
                slidesPerView: 2,
            },
            480: {
                slidesPerView: 2,
            },
            787: {
                slidesPerView: 3,
            },
            991: {
                slidesPerView: 4,
            },
            1200: {
                slidesPerView: 4,
            }
        }
    });

    $('.accordion .accordion-item').on('click', function () {
        $(this).addClass("active").siblings().removeClass("active");
    });

    // Services active

    $('.services-cst .item').on('mouseenter', function () {
        $('.services-cst .item').removeClass('active');
        $(this).addClass('active');

        if ($(this).hasClass('active')) {
            return false;
        }
    });

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
            var scale = 1 - (cards.length - index) * 0.025;
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

});