const hamburger = document.getElementById('hamburger');
const navLinks = document.getElementById('nav-links');

hamburger.addEventListener('click', () => {
    navLinks.classList.toggle('open'); // Toggle the "open" class
});
document.addEventListener('DOMContentLoaded', function () {
    const menuToggle = document.getElementById('menuToggle');
    const navMenu = document.getElementById('navMenu');

    // Toggle the visibility of the nav links
    menuToggle.addEventListener('click', function () {
        navMenu.classList.toggle('nav-active');
    });

    // Function for handling dropdown clicks (if needed)
    window.handleOption = function (option) {
        alert(option + " selected!");
    };
});
