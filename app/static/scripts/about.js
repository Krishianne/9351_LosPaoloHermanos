const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('slide-in');
      } else {
        entry.target.classList.remove('slide-in'); 
      }
    });
  }, {
    threshold: 0.3
  });

  const container = document.querySelector('.developer-container');
  observer.observe(container);