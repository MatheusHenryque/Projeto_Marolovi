document.addEventListener("DOMContentLoaded", () => {
  const counters = document.querySelectorAll('.metric-value');
  const speed = 500;

  counters.forEach(counter => {
    const target = +counter.getAttribute('data-target');
    const suffix = counter.getAttribute('data-suffix') || ""; 
    let count = 0;
    const increment = target / speed;

    const updateCount = () => {
      if (count < target) {
        count += increment;
        counter.innerText = Math.ceil(count) + suffix;
        setTimeout(updateCount, 10);
      } else {
        counter.innerText = target + suffix;
      }
    };

    updateCount();
  });
});
