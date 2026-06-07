/* ==========================================
   TechMantra JS Script - Interactive Behaviors
   ========================================== */

document.addEventListener('DOMContentLoaded', () => {
  // --- Preloader Fade Out ---
  const loader = document.getElementById('premium-loader-overlay');
  if (loader) {
    setTimeout(() => {
      loader.classList.add('fade-out');
      setTimeout(() => {
        loader.remove();
      }, 400);
    }, 600);
  }

  // --- Navigation & Scroll Effects ---
  const navbar = document.querySelector('.navbar-wrapper');
  const navLinks = document.querySelectorAll('.nav-link');

  window.addEventListener('scroll', () => {
    // Add scroll class to navbar
    if (window.scrollY > 50) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  });

  // Highlight active link based on current page URL path
  const currentPath = window.location.pathname;
  navLinks.forEach(link => {
    link.classList.remove('active');
    const href = link.getAttribute('href');
    if (href) {
      if ((currentPath === '/' || currentPath === '/file/') && (href === '/' || href === '/file/')) {
        link.classList.add('active');
      } else if (href !== '/' && href !== '/file/' && currentPath.includes(href)) {
        link.classList.add('active');
      }
    }
  });


  // Mobile Hamburger Menu
  const menuToggle = document.querySelector('.menu-toggle');
  const navMenu = document.querySelector('.nav-links');

  if (menuToggle && navMenu) {
    menuToggle.addEventListener('click', () => {
      navMenu.classList.toggle('active');
      // Hamburger animation
      const spans = menuToggle.querySelectorAll('span');
      spans[0].style.transform = navMenu.classList.contains('active') ? 'rotate(45deg) translate(6px, 6px)' : 'none';
      spans[1].style.opacity = navMenu.classList.contains('active') ? '0' : '1';
      spans[2].style.transform = navMenu.classList.contains('active') ? 'rotate(-45deg) translate(6px, -6px)' : 'none';
    });

    // Close menu when a link is clicked
    navLinks.forEach(link => {
      link.addEventListener('click', () => {
        navMenu.classList.remove('active');
        const spans = menuToggle.querySelectorAll('span');
        spans.forEach(span => span.removeAttribute('style'));
      });
    });
  }

  // --- Login Modal Controls (Removed in favor of dedicated authentication pages) ---


  // --- Gallery Filtering ---
  const filterBtns = document.querySelectorAll('.gallery-filter-btn');
  const galleryItems = document.querySelectorAll('.gallery-item');

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      // Remove active from other buttons
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const filterValue = btn.getAttribute('data-filter');

      galleryItems.forEach(item => {
        const itemCategory = item.getAttribute('data-category');
        if (filterValue === 'all' || itemCategory === filterValue) {
          item.style.display = 'block';
          setTimeout(() => {
            item.style.opacity = '1';
            item.style.transform = 'scale(1)';
          }, 50);
        } else {
          item.style.opacity = '0';
          item.style.transform = 'scale(0.8)';
          setTimeout(() => {
            item.style.display = 'none';
          }, 300);
        }
      });
    });
  });

  // --- Form Submission Handling (AJAX) ---
  const forms = document.querySelectorAll('.ajax-form');

  forms.forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const submitBtn = form.querySelector('button[type="submit"]');
      const originalText = submitBtn ? submitBtn.innerHTML : '';
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Submitting...';
      }

      const formData = new FormData(form);
      formData.append('ajax', 'true');

      try {
        const response = await fetch(form.action || window.location.href, {
          method: 'POST',
          body: formData,
          headers: {
            'X-Requested-With': 'XMLHttpRequest'
          }
        });

        const data = await response.json();

        if (data.status === 'success') {
          showToast(data.message, 'success');
          if (data.redirect_url) {
            setTimeout(() => {
              window.location.href = data.redirect_url;
            }, 1200);
          } else {
            form.reset();
          }
        } else {
          showToast(data.message || 'An error occurred. Please try again.', 'error');
        }
      } catch (error) {
        console.error('Error submitting form:', error);
        showToast('Connection error. Please check your internet.', 'error');
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalText;
        }
      }
    });
  });

  // --- Custom Toast System ---
  function showToast(message, type = 'success') {
    let container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
    
    toast.innerHTML = `
      <i class="fas ${icon}"></i>
      <span class="toast-message">${message}</span>
    `;

    container.appendChild(toast);

    // Trigger reflow to enable CSS transition
    toast.offsetHeight;
    toast.classList.add('show');

    // Remove toast after 4 seconds
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => {
        toast.remove();
      }, 300);
    }, 4000);
  }
});
