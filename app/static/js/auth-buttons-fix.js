/**
 * Fix for authentication buttons visibility
 * This ensures the login and register buttons are always visible
 */
document.addEventListener('DOMContentLoaded', function() {
  // Force auth buttons visibility
  const authButtons = document.querySelectorAll('.nav-link[href*="login"], .nav-link[href*="register"]');
  authButtons.forEach(button => {
    button.style.opacity = '1';
    button.style.visibility = 'visible';
    
    if (button.getAttribute('href').includes('register')) {
      button.style.backgroundColor = 'white';
      button.style.color = '#7AAE9F';
      button.style.display = 'inline-block';
    }
  });
});