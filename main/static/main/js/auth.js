document.addEventListener('DOMContentLoaded', () => {
  const LOGIN_ENDPOINT = '/api/login/';
  const REGISTER_ENDPOINT = '/api/register/';
  const LOGOUT_ENDPOINT = '/api/logout/';

  const loginForm = document.querySelector('[data-auth-form="login"]');
  const registerForm = document.querySelector('[data-auth-form="register"]');
  const logoutButtons = document.querySelectorAll('[data-logout-button]');

  function getCookie(name) {
    const cookies = document.cookie ? document.cookie.split('; ') : [];
    for (const cookie of cookies) {
      if (cookie.startsWith(`${name}=`)) {
        return decodeURIComponent(cookie.split('=').slice(1).join('='));
      }
    }
    return null;
  }

  function jsonHeaders() {
    const headers = {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
    };
    const csrf = getCookie('csrftoken');
    if (csrf) {
      headers['X-CSRFToken'] = csrf;
    }
    return headers;
  }

  function parseJsonSafe(text) {
    if (!text) return {};
    try {
      return JSON.parse(text);
    } catch {
      return {};
    }
  }

  function clearFormErrors(form) {
    form.querySelectorAll('.is-invalid').forEach((field) => field.classList.remove('is-invalid'));
    form.querySelectorAll('[data-field-error]').forEach((node) => {
      node.textContent = '';
      node.classList.add('d-none');
    });
    const general = form.querySelector('[data-form-error]');
    if (general) {
      general.textContent = '';
      general.classList.add('d-none');
    }
  }

  function applyFormErrors(form, errors) {
    if (!errors) return false;
    let hasErrors = false;
    Object.entries(errors).forEach(([fieldName, messages]) => {
      const field = form.elements[fieldName];
      if (!field) return;
      const feedback = form.querySelector(`[data-field-error="${fieldName}"]`);
      const text = Array.isArray(messages) ? messages.join(' ') : messages;
      if (feedback && text) {
        feedback.textContent = text;
        feedback.classList.remove('d-none');
      }
      field.classList.add('is-invalid');
      hasErrors = true;
    });
    return hasErrors;
  }

  function setFormError(form, message) {
    const target = form.querySelector('[data-form-error]');
    if (!target) return;
    if (message) {
      target.textContent = message;
      target.classList.remove('d-none');
    } else {
      target.textContent = '';
      target.classList.add('d-none');
    }
  }

  function buildPayload(form) {
    return Object.fromEntries(new FormData(form).entries());
  }

  async function handleAuthForm(form, endpoint, successMessage) {
    const submitBtn = form.querySelector('[data-submit-btn]') || form.querySelector('button[type="submit"]');
    clearFormErrors(form);
    setFormError(form, '');
    if (submitBtn) submitBtn.setAttribute('disabled', 'disabled');

    try {
      const payload = buildPayload(form);
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: jsonHeaders(),
        body: JSON.stringify(payload),
      });
      const data = parseJsonSafe(await response.text());
      if (!response.ok) {
        const handled = applyFormErrors(form, data.errors);
        if (!handled) {
          setFormError(form, data.error || data.detail || 'Request failed.');
        }
        throw new Error(data.error || data.detail || 'Authentication failed.');
      }

      if (typeof showToast === 'function') {
        showToast(successMessage, 'success');
      }
      const redirect = data.redirect || '/';
      window.location.href = redirect;
    } catch (error) {
      console.error(error);
      if (typeof showToast === 'function') {
        showToast(error.message || 'Something went wrong.', 'danger');
      }
    } finally {
      if (submitBtn) submitBtn.removeAttribute('disabled');
    }
  }

  async function handleLogout(event) {
    event.preventDefault();
    const button = event.currentTarget;
    button.disabled = true;
    try {
      const response = await fetch(LOGOUT_ENDPOINT, {
        method: 'POST',
        headers: jsonHeaders(),
      });
      const data = parseJsonSafe(await response.text());
      if (!response.ok) {
        throw new Error(data.error || data.detail || 'Unable to log out.');
      }
      if (typeof showToast === 'function') {
        showToast('Logged out successfully.', 'success');
      }
      const redirect = data.redirect || '/login/';
      window.location.href = redirect;
    } catch (error) {
      console.error(error);
      if (typeof showToast === 'function') {
        showToast(error.message || 'Unable to log out.', 'danger');
      }
      button.disabled = false;
    }
  }

  if (loginForm) {
    loginForm.addEventListener('submit', (event) => {
      event.preventDefault();
      handleAuthForm(loginForm, LOGIN_ENDPOINT, 'Logged in successfully!');
    });
  }

  if (registerForm) {
    registerForm.addEventListener('submit', (event) => {
      event.preventDefault();
      handleAuthForm(registerForm, REGISTER_ENDPOINT, 'Account created!');
    });
  }

  logoutButtons.forEach((button) => {
    button.addEventListener('click', handleLogout);
  });
});
