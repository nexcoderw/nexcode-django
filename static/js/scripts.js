"use strict";

// Keep navigation usable without loading animation and UI libraries on every page.
const menu = document.getElementById("mobile-navigation");
const trigger = document.querySelector(".menu-icon");
const closeButton = menu.querySelector(".close-menu");
const background = [document.querySelector(".navbar"), document.querySelector("main"), document.querySelector("footer")];

function closeMenu() {
    menu.hidden = true;
    menu.classList.remove("open");
    trigger.setAttribute("aria-expanded", "false");
    document.body.classList.remove("menu-open");
    background.forEach((element) => {
        element.inert = false;
    });
    trigger.focus();
}

trigger.addEventListener("click", () => {
    menu.hidden = false;
    menu.classList.add("open");
    trigger.setAttribute("aria-expanded", "true");
    document.body.classList.add("menu-open");
    background.forEach((element) => {
        element.inert = true;
    });
    closeButton.focus();
});
closeButton.addEventListener("click", closeMenu);
menu.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeMenu();
    if (event.key !== "Tab") return;
    const focusable = [...menu.querySelectorAll("button, a[href]")];
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
    }
});
