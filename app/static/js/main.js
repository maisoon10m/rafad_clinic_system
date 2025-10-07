/**
 * Main JavaScript for Rafad Clinic System
 * Enhanced UX and interaction patterns
 */

document.addEventListener('DOMContentLoaded', function() {
  // Add current year to footer
  const footerYear = document.querySelector('footer p');
  if (footerYear) {
    footerYear.innerHTML = footerYear.innerHTML.replace('{{ now.year }}', new Date().getFullYear());
  }
  
  // Enable tooltips everywhere with consistent styling
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl, {
      boundary: document.body,
      delay: { show: 300, hide: 100 }
    });
  });

  // Enable popovers everywhere with consistent styling
  const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
  popoverTriggerList.map(function (popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl, {
      trigger: 'focus',
      boundary: document.body
    });
  });
  
  // Auto-hide alerts after 5 seconds (except for danger alerts)
  const autoHideAlerts = document.querySelectorAll('.alert:not(.alert-danger):not(.no-auto-hide)');
  autoHideAlerts.forEach(alert => {
    const bsAlert = new bootstrap.Alert(alert);
    setTimeout(() => {
      bsAlert.close();
    }, 5000);
  });
  
  // Add smooth scrolling behavior to all anchor links
  document.querySelectorAll('a[href^="#"]:not([data-bs-toggle])').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        window.scrollTo({
          top: target.offsetTop - 70,
          behavior: 'smooth'
        });
      }
    });
  });
  
  // Add active state to nav links based on current page
  const currentPath = window.location.pathname;
  document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPath) {
      link.classList.add('active');
    }
  });
  
  // Add animation classes to elements with data-animate attribute when they come into view
  const animateElements = document.querySelectorAll('[data-animate]');
  if (animateElements.length > 0) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animated', entry.target.dataset.animate);
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });
    
    animateElements.forEach(element => {
      observer.observe(element);
    });
  }
  
  // Add form validation styles
  const forms = document.querySelectorAll('.needs-validation');
  if (forms.length > 0) {
    Array.from(forms).forEach(form => {
      form.addEventListener('submit', event => {
        if (!form.checkValidity()) {
          event.preventDefault();
          event.stopPropagation();
        }
        form.classList.add('was-validated');
      }, false);
    });
  }
  
  // Handle navbar scrolled state
  const handleNavbarScroll = () => {
    const navbar = document.querySelector('.navbar');
    if (navbar && window.scrollY > 50) {
      navbar.classList.add('navbar-scrolled');
    } else if (navbar) {
      navbar.classList.remove('navbar-scrolled');
    }
  };
  
  window.addEventListener('scroll', handleNavbarScroll);
  
  // Handle sidebar toggle
  const sidebarToggle = document.querySelector('.sidebar-toggle');
  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', () => {
      const sidebar = document.querySelector('.sidebar');
      const content = document.querySelector('.content-with-sidebar');
      
      sidebar.classList.toggle('sidebar-collapsed');
      if (content) {
        content.classList.toggle('content-with-sidebar-collapsed');
      }
    });
  }
  
  // Back to top button functionality
  const backToTopButton = document.querySelector('.back-to-top');
  if (backToTopButton) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 300) {
        backToTopButton.classList.add('visible');
      } else {
        backToTopButton.classList.remove('visible');
      }
    });
    
    backToTopButton.addEventListener('click', () => {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });
  }
  
  // Add a back to top button if not present
  if (!document.querySelector('.back-to-top')) {
    const backToTopBtn = document.createElement('div');
    backToTopBtn.className = 'back-to-top';
    backToTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    document.body.appendChild(backToTopBtn);
    
    window.addEventListener('scroll', () => {
      if (window.scrollY > 300) {
        backToTopBtn.classList.add('visible');
      } else {
        backToTopBtn.classList.remove('visible');
      }
    });
    
    backToTopBtn.addEventListener('click', () => {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });
  }
});