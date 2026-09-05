/* ==========================================
   TechMantra JS Script - Interactive Behaviors
   ========================================== */

document.addEventListener('DOMContentLoaded', () => {
  // --- Theme Toggle Engine (Dark / Light Mode) ---
  const themeToggleBtn = document.getElementById('themeToggleBtn');
  const mobileThemeToggleBtn = document.getElementById('mobileThemeToggleBtn');
  
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    try {
      localStorage.setItem('teachmantra_theme', theme);
    } catch(e) {}
    
    // Update mobile toggle text
    if (mobileThemeToggleBtn) {
      const themeText = mobileThemeToggleBtn.querySelector('.theme-text');
      if (themeText) {
        themeText.textContent = theme === 'light' ? 'Switch to Dark Mode' : 'Switch to Light Mode';
      }
    }
    
    if (themeToggleBtn) {
      themeToggleBtn.setAttribute('title', theme === 'light' ? 'Switch to Dark Mode' : 'Switch to Light Mode');
    }
  }

  // Get current active theme
  const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
  applyTheme(currentTheme);

  function toggleTheme() {
    const activeTheme = document.documentElement.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
    applyTheme(activeTheme);
  }

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', toggleTheme);
  }
  if (mobileThemeToggleBtn) {
    mobileThemeToggleBtn.addEventListener('click', toggleTheme);
  }

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
  // --- Gallery Lightbox Image Viewer ---
  const lightboxModal = document.getElementById('imageLightboxModal');
  const lightboxImage = document.getElementById('lightboxImage');
  const lightboxCaption = document.getElementById('lightboxCaption');
  const lightboxCloseBtn = document.getElementById('lightboxCloseBtn');

  function openLightbox(src, title) {
    if (!lightboxModal || !lightboxImage || !src) return;
    lightboxImage.src = src;
    if (title && lightboxCaption) {
      lightboxCaption.textContent = title;
      lightboxCaption.style.display = 'inline-block';
    } else if (lightboxCaption) {
      lightboxCaption.textContent = '';
      lightboxCaption.style.display = 'none';
    }
    lightboxModal.classList.add('active');
    lightboxModal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  }

  function closeLightbox() {
    if (!lightboxModal) return;
    lightboxModal.classList.remove('active');
    lightboxModal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    setTimeout(() => {
      if (lightboxImage) lightboxImage.src = '';
    }, 300);
  }

  // Attach click listener to all gallery items
  galleryItems.forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const img = item.querySelector('img');
      const src = item.getAttribute('data-src') || (img ? img.src : '');
      const title = item.getAttribute('data-title') || (img ? img.alt : '');
      openLightbox(src, title);
    });
  });

  // Attach click listener to topper avatar images as well
  const topperAvatars = document.querySelectorAll('.topper-avatar-wrapper');
  topperAvatars.forEach(wrapper => {
    wrapper.style.cursor = 'pointer';
    wrapper.setAttribute('title', 'Click to view photo');
    wrapper.addEventListener('click', () => {
      const img = wrapper.querySelector('img');
      const card = wrapper.closest('.topper-card');
      const name = card ? card.querySelector('h3')?.textContent : (img ? img.alt : '');
      if (img && img.src) {
        openLightbox(img.src, name ? `Topper: ${name}` : 'Student Photo');
      }
    });
  });

  // Close triggers
  if (lightboxCloseBtn) {
    lightboxCloseBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      closeLightbox();
    });
  }

  if (lightboxModal) {
    lightboxModal.addEventListener('click', (e) => {
      // Clicking anywhere on modal or image closes it as requested
      closeLightbox();
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && lightboxModal && lightboxModal.classList.contains('active')) {
      closeLightbox();
    }
  });
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
