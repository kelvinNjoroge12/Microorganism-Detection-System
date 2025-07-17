document.addEventListener('DOMContentLoaded', function() {
    // Configuration
    const images = [
        "{% static 'images/bg1.png' %}",
        "{% static 'images/bg2.png' %}",
        "{% static 'images/bg3.png' %}"
    ];

    const slides = document.querySelectorAll('.bg-slide');
    let currentIndex = 0;

    // Preload all images
    function preloadImages() {
        images.forEach(img => {
            new Image().src = img;
        });
    }

    // Rotate backgrounds
    function rotateBackground() {
        // Set next slide
        const nextIndex = (currentIndex + 1) % images.length;
        const nextSlide = slides[nextIndex % slides.length];

        // Update slide
        nextSlide.style.backgroundImage = `url(${images[nextIndex]})`;
        nextSlide.classList.add('active');

        // Hide current slide
        slides[currentIndex % slides.length].classList.remove('active');

        currentIndex = nextIndex;

        // Schedule next rotation
        setTimeout(rotateBackground, 8000);
    }

    // Initialize first two slides
    slides[0].style.backgroundImage = `url(${images[0]})`;
    slides[0].classList.add('active');
    slides[1].style.backgroundImage = `url(${images[1]})`;

    // Start rotation
    preloadImages();
    setTimeout(rotateBackground, 8000);
});