document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".site-mobile-menu").forEach((menu) => {
        menu.querySelectorAll("a").forEach((link) => {
            link.addEventListener("click", () => {
                menu.open = false;
            });
        });
    });
});
