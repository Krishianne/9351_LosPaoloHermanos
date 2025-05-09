
// Animation: Slide up for Article texts and images when scrolling
document.addEventListener('DOMContentLoaded', function() {
    const articles = document.querySelectorAll('[class^="main-article"]');

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('show');
            } else {
                entry.target.classList.remove('show');
            }
        });
    }, {
        threshold: 0.2
    });

    articles.forEach(article => {
        observer.observe(article);
    });
});