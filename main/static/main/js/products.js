document.addEventListener('DOMContentLoaded', () => {
  const PRODUCTS_ENDPOINT = '/api/products/';

  const productGrid = document.getElementById('product-grid');
  if (!productGrid) {
    return;
  }

  const stateLoading = document.getElementById('product-state-loading');
  const stateEmpty = document.getElementById('product-state-empty');
  const stateError = document.getElementById('product-state-error');
  const refreshBtn = document.getElementById('refresh-products-btn');

  const createModalEl = document.getElementById('productCreateModal');
  const editModalEl = document.getElementById('productEditModal');
  const deleteModalEl = document.getElementById('productDeleteModal');

  const createForm = document.getElementById('product-create-form');
  const editForm = document.getElementById('product-edit-form');
  const deleteConfirmBtn = document.getElementById('confirm-delete-btn');
  const deleteProductName = document.getElementById('delete-product-name');

  const escaper = document.createElement('textarea');

  let productsCache = [];
  let activeProductId = null;

  function escapeHtml(value) {
    escaper.textContent = value ?? '';
    return escaper.innerHTML;
  }

  function getCookie(name) {
    const cookies = document.cookie ? document.cookie.split('; ') : [];
    for (const cookie of cookies) {
      if (cookie.startsWith(`${name}=`)) {
        return decodeURIComponent(cookie.split('=').slice(1).join('='));
      }
    }
    return null;
  }

  function jsonHeaders(method = 'GET') {
    const headers = { 'X-Requested-With': 'XMLHttpRequest' };
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method.toUpperCase())) {
      headers['Content-Type'] = 'application/json';
      const csrf = getCookie('csrftoken');
      if (csrf) {
        headers['X-CSRFToken'] = csrf;
      }
    }
    return headers;
  }

  function toggleState(state, message) {
    [stateLoading, stateEmpty, stateError].forEach((el) => {
      if (el) {
        el.classList.add('d-none');
      }
    });
    productGrid.classList.add('d-none');

    if (refreshBtn) {
      refreshBtn.disabled = state === 'loading';
    }

    if (state === 'loading' && stateLoading) {
      stateLoading.classList.remove('d-none');
    } else if (state === 'empty' && stateEmpty) {
      stateEmpty.classList.remove('d-none');
    } else if (state === 'error' && stateError) {
      if (message) {
        stateError.textContent = message;
      }
      stateError.classList.remove('d-none');
    } else if (state === 'ready') {
      productGrid.classList.remove('d-none');
    }
  }

  function showErrorState(message) {
    toggleState('error', message);
    if (typeof showToast === 'function') {
      showToast(message, 'danger');
    }
  }

  function parseJsonSafe(text) {
    if (!text) return {};
    try {
      return JSON.parse(text);
    } catch {
      return {};
    }
  }

  function setFormError(form, message = '') {
    if (!form) return;
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

  function clearFormErrors(form) {
    if (!form) return;
    setFormError(form, '');
    form.querySelectorAll('.is-invalid').forEach((field) => field.classList.remove('is-invalid'));
    form.querySelectorAll('[data-field-error]').forEach((node) => {
      node.textContent = '';
      node.classList.add('d-none');
    });
  }

  function applyFormErrors(form, errors) {
    if (!form || !errors) return false;
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

  function formToPayload(form) {
    const payload = Object.fromEntries(new FormData(form).entries());
    if (form.elements['is_featured']) {
      payload.is_featured = form.elements['is_featured'].checked;
    }
    if (payload.price !== undefined) {
      payload.price = payload.price.toString().trim();
    }
    return payload;
  }

  function renderProducts(products) {
    productGrid.innerHTML = '';
    if (!Array.isArray(products) || !products.length) {
      toggleState('empty');
      return;
    }

    const currency = new Intl.NumberFormat('id-ID');
    const fragment = document.createDocumentFragment();

    products.forEach((product) => {
      const productId = Number(product.id);
      const formattedPrice = currency.format(Number(product.price) || 0);
      const categoryLabel = product.category_display || product.category || 'Uncategorized';

      const col = document.createElement('div');
      col.className = 'col-lg-4 col-md-6';
      col.innerHTML = `
        <div class="card h-100 ${product.is_featured ? 'featured-card' : ''}">
          <img src="${escapeHtml(product.thumbnail || 'https://via.placeholder.com/300x200?text=No+Image')}"
               class="card-img-top product-img"
               alt="${escapeHtml(product.name || 'Product image')}"
               onerror="this.src='https://via.placeholder.com/300x200?text=No+Image';">
          <div class="card-body d-flex flex-column">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <h5 class="card-title mb-0">${escapeHtml(product.name || 'Untitled Product')}</h5>
              ${product.is_featured ? '<span class="badge bg-warning text-dark">Featured</span>' : ''}
            </div>
            <h6 class="card-subtitle mb-2 text-success">IDR ${formattedPrice}</h6>
            <p class="card-text flex-grow-1">${escapeHtml(product.description || '')}</p>
            <p class="card-text"><small class="text-muted">Category: ${escapeHtml(categoryLabel)}</small></p>
            <div class="mt-auto">
              <a href="/product/${productId}/" class="btn btn-primary btn-sm me-2">View Details</a>
              ${product.can_edit ? `
                <button type="button" class="btn btn-warning btn-sm me-2" data-product-id="${productId}" data-action="edit">Edit</button>
                <button type="button" class="btn btn-danger btn-sm" data-product-id="${productId}" data-action="delete">Delete</button>
              ` : ''}
            </div>
          </div>
        </div>`;
      fragment.appendChild(col);
    });

    productGrid.appendChild(fragment);
    toggleState('ready');
    attachCardListeners();
  }

  function attachCardListeners() {
    productGrid.querySelectorAll('button[data-action="edit"]').forEach((button) => {
      button.addEventListener('click', (event) => {
        event.preventDefault();
        const id = Number(button.dataset.productId);
        const product = productsCache.find((item) => Number(item.id) === id);
        if (!product || !editForm || !editModalEl) {
          if (typeof showToast === 'function') {
            showToast('Unable to load product for editing.', 'danger');
          }
          return;
        }
        activeProductId = id;
        populateEditForm(product);
        const modal = bootstrap.Modal.getOrCreateInstance(editModalEl);
        modal.show();
      });
    });

    productGrid.querySelectorAll('button[data-action="delete"]').forEach((button) => {
      button.addEventListener('click', (event) => {
        event.preventDefault();
        const id = Number(button.dataset.productId);
        const product = productsCache.find((item) => Number(item.id) === id);
        if (!product || !deleteModalEl) {
          if (typeof showToast === 'function') {
            showToast('Unable to find product to delete.', 'danger');
          }
          return;
        }
        activeProductId = id;
        if (deleteProductName) {
          deleteProductName.textContent = product.name || 'this product';
        }
        const modal = bootstrap.Modal.getOrCreateInstance(deleteModalEl);
        modal.show();
      });
    });
  }

  function populateEditForm(product) {
    if (!editForm) return;
    clearFormErrors(editForm);
    editForm.elements['id'].value = product.id;
    editForm.elements['name'].value = product.name || '';
    editForm.elements['price'].value = product.price ?? '';
    editForm.elements['description'].value = product.description || '';
    editForm.elements['thumbnail'].value = product.thumbnail || '';
    if (editForm.elements['category']) {
      editForm.elements['category'].value = product.category || '';
    }
    if (editForm.elements['is_featured']) {
      editForm.elements['is_featured'].checked = Boolean(product.is_featured);
    }
  }

  async function mutateProduct({ form, url, method, successMessage }) {
    const submitBtn = form?.querySelector('[data-submit-btn]') || deleteConfirmBtn;
    const modalEl = form ? form.closest('.modal') : deleteModalEl;

    if (form) {
      clearFormErrors(form);
      setFormError(form, '');
    }
    if (submitBtn) {
      submitBtn.setAttribute('disabled', 'disabled');
    }

    try {
      const options = {
        method,
        headers: jsonHeaders(method),
      };
      if (method !== 'DELETE' && form) {
        options.body = JSON.stringify(formToPayload(form));
      }

      const response = await fetch(url, options);
      const data = parseJsonSafe(await response.text());

      if (!response.ok) {
        const handled = form && applyFormErrors(form, data.errors);
        if (form && !handled) {
          setFormError(form, data.error || data.detail || 'Request failed.');
        }
        throw new Error(data.error || data.detail || 'Request failed.');
      }

      if (modalEl) {
        bootstrap.Modal.getInstance(modalEl)?.hide();
      }
      if (form) {
        form.reset();
        clearFormErrors(form);
      }
      if (typeof showToast === 'function') {
        showToast(successMessage, 'success');
      }
      await fetchProducts({ showLoading: false });
    } catch (error) {
      console.error(error);
      if (typeof showToast === 'function') {
        showToast(error.message || 'Something went wrong.', 'danger');
      }
    } finally {
      if (submitBtn) {
        submitBtn.removeAttribute('disabled');
      }
    }
  }

  async function fetchProducts({ showLoading = true, announce = false } = {}) {
    if (showLoading) {
      toggleState('loading');
    }
    try {
      const response = await fetch(PRODUCTS_ENDPOINT, { headers: jsonHeaders() });
      const data = parseJsonSafe(await response.text());
      if (!response.ok) {
        throw new Error(data.error || data.detail || 'Unable to fetch products.');
      }
      productsCache = Array.isArray(data.products) ? data.products : [];
      if (!productsCache.length) {
        toggleState('empty');
        productGrid.innerHTML = '';
      } else {
        renderProducts(productsCache);
      }
      if (announce && typeof showToast === 'function') {
        showToast('Product list refreshed.', 'info');
      }
    } catch (error) {
      console.error(error);
      showErrorState(error.message || 'Unable to fetch products.');
    }
  }

  if (refreshBtn) {
    refreshBtn.addEventListener('click', () => fetchProducts({ showLoading: true, announce: true }));
  }

  if (createForm && createModalEl) {
    createForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      await mutateProduct({
        form: createForm,
        url: PRODUCTS_ENDPOINT,
        method: 'POST',
        successMessage: 'Product created!',
      });
    });

    createModalEl.addEventListener('show.bs.modal', () => {
      clearFormErrors(createForm);
      createForm.reset();
      setTimeout(() => {
        createForm.elements['name']?.focus();
      }, 120);
    });
  }

  if (editForm && editModalEl) {
    editForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (!activeProductId) {
        if (typeof showToast === 'function') {
          showToast('Select a product to edit first.', 'warning');
        }
        return;
      }
      await mutateProduct({
        form: editForm,
        url: `${PRODUCTS_ENDPOINT}${activeProductId}/`,
        method: 'PUT',
        successMessage: 'Product updated!',
      });
    });

    editModalEl.addEventListener('show.bs.modal', () => {
      clearFormErrors(editForm);
      setTimeout(() => {
        editForm.elements['name']?.focus();
      }, 120);
    });

    editModalEl.addEventListener('hidden.bs.modal', () => {
      activeProductId = null;
    });
  }

  if (deleteConfirmBtn && deleteModalEl) {
    deleteConfirmBtn.addEventListener('click', async () => {
      if (!activeProductId) return;
      await mutateProduct({
        form: null,
        url: `${PRODUCTS_ENDPOINT}${activeProductId}/`,
        method: 'DELETE',
        successMessage: 'Product deleted!',
      });
      activeProductId = null;
    });

    deleteModalEl.addEventListener('hidden.bs.modal', () => {
      activeProductId = null;
      if (deleteProductName) {
        deleteProductName.textContent = 'this product';
      }
    });
  }

  fetchProducts({ showLoading: true });
});
