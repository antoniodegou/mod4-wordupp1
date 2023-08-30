// text effects

document.addEventListener("DOMContentLoaded", function() {
    const txtElements = document.querySelectorAll('.txt');
    const colors = ['var(--pink)', 'var(--red)', 'var(--yellow)'];
  
    const alterElement = (element) => {
      const randomDuration = (Math.random() * (3 - 1) + 1).toFixed(1); // Random duration between 3s and 5s
      const randomSize = Math.random() * (2 - 1) + 1; // Random size between 1 and 2
      const randomColor = colors[Math.floor(Math.random() * colors.length)]; // Random color
  
      element.style.transition = `all ${randomDuration}s ease-in-out`;
      element.style.fontSize = `${randomSize}em`;
      element.style.color = randomColor;
    };
  
    txtElements.forEach((txt) => {
      // Initially alter each element
      alterElement(txt);
  
      // Periodically alter each element
      setInterval(() => {
        alterElement(txt);
      }, 3000);  // Alters every 3 seconds, adjust as needed
    });
  });
  
  
  