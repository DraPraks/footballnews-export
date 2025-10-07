(function () {
  const CONTAINER_ID = 'toast-container';
  const ACTIVE_CLASS = 'is-visible';
  const DEFAULT_DURATION = 3600;
  const VALID_VARIANTS = new Set(['success', 'danger', 'warning', 'info']);
  const ESCAPER = document.createElement('textarea');

  function ensureContainer() {
    let container = document.getElementById(CONTAINER_ID);
    if (!container) {
      container = document.createElement('div');
      container.id = CONTAINER_ID;
      container.className = 'toast-stack';
      container.setAttribute('aria-live', 'polite');
      container.setAttribute('aria-atomic', 'true');
      document.body.appendChild(container);
    }
    return container;
  }

  function escapeHtml(value) {
    ESCAPER.textContent = value ?? '';
    return ESCAPER.innerHTML;
  }

  function hideToast(toast) {
    toast.classList.remove(ACTIVE_CLASS);
    toast.addEventListener(
      'transitionend',
      () => {
        toast.remove();
      },
      { once: true }
    );
  }

  function createToast(message, variant, options) {
    const container = ensureContainer();
    const toast = document.createElement('div');
    toast.className = `toast-card toast-${variant}`;
    toast.setAttribute('role', 'status');

    toast.innerHTML = `
      <span class="toast-indicator" aria-hidden="true"></span>
      <div class="toast-content">${escapeHtml(message)}</div>
      <button type="button" class="toast-close" aria-label="Dismiss notification">&times;</button>
    `;

    const closeBtn = toast.querySelector('.toast-close');
    let hideTimer = null;

    const scheduleHide = (delay) => {
      hideTimer = window.setTimeout(() => hideToast(toast), delay);
    };

    closeBtn.addEventListener('click', () => {
      window.clearTimeout(hideTimer);
      hideToast(toast);
    });

    toast.addEventListener('mouseenter', () => {
      window.clearTimeout(hideTimer);
    });

    toast.addEventListener('mouseleave', () => {
      scheduleHide(1200);
    });

    container.appendChild(toast);
    requestAnimationFrame(() => toast.classList.add(ACTIVE_CLASS));

    const duration = Math.max(1500, Number(options.duration) || DEFAULT_DURATION);
    scheduleHide(duration);
  }

  window.showToast = function showToast(message, variant = 'info', options = {}) {
    if (!message) return;
    const tone = VALID_VARIANTS.has(variant) ? variant : 'info';
    createToast(message, tone, options);
  };
})();
