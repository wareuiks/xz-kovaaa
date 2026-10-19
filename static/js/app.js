/**
 * OVKSHOP Frontend Engine (Matching Official Reference)
 */

let currentUser = null;
let currentCatalog = [];
let selectedOption = null;
let selectedDepositAmount = 100;

document.addEventListener('DOMContentLoaded', () => {
  initApp();
});

async function initApp() {
  await checkUserAuth();

  // If on products page, load catalog
  if (document.getElementById('products-catalog-container')) {
    loadCatalog();
  }

  // If on dashboard page, load dashboard stats
  if (document.getElementById('dash-balance-val')) {
    loadDashboardStats();
  }

  setupEventListeners();

  // Handle URL deposit query params or pending local checkout
  const params = new URLSearchParams(window.location.search);
  const urlSessionId = params.get('session_id');
  const isDepositSuccess = params.get('deposit') === 'success';

  if (isDepositSuccess || urlSessionId) {
    const sessionId = urlSessionId || localStorage.getItem('ovk_pending_checkout');
    if (sessionId && !sessionId.includes('{CHECKOUT_SESSION_ID}')) {
      showToast('Loading.. Please Wait.', 'info');
      try {
        const verifyRes = await fetch('/api/wallet/verify-checkout', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ session_id: sessionId })
        });
        const verifyData = await verifyRes.json();
        if (verifyData.success) {
          showToast(verifyData.message || 'Payment verified! Credits added automatically.', 'success');
          localStorage.removeItem('ovk_pending_checkout');
        } else {
          localStorage.removeItem('ovk_pending_checkout');
        }
      } catch (err) {
        showToast('Payment received! Refreshing balance...', 'success');
      }
    } else {
      localStorage.removeItem('ovk_pending_checkout');
    }
    window.history.replaceState({}, document.title, window.location.pathname);
    await checkUserAuth();
    if (document.getElementById('dash-balance-val')) {
      loadDashboardStats();
    }
  }
}

async function checkUserAuth() {
  try {
    const res = await fetch('/api/auth/me');
    const data = await res.json();
    const actionsContainer = document.getElementById('header-actions-area');

    if (data.authenticated && data.user) {
      currentUser = data.user;
      const initial = (data.user.username || 'U').charAt(0).toUpperCase();

      if (actionsContainer) {
        actionsContainer.innerHTML = `
          <div class="coin-pill" onclick="openDepositModal()" title="Wallet Balance">
            <div class="coin-icon">₱</div>
            <span id="nav-coin-val">${parseFloat(data.user.balance).toFixed(2)}</span>
          </div>
          <button class="user-avatar-btn" id="avatar-btn" onclick="toggleUserMenu()">${initial}</button>
          
          <div class="user-dropdown-menu" id="user-dropdown">
            <div style="padding: 8px 12px; border-bottom: 1px solid var(--border-card); margin-bottom: 6px;">
              <div style="font-weight: 700; color: #fff;">${data.user.username}</div>
              <div style="font-size: 0.75rem; color: var(--text-dark);">${data.user.email}</div>
            </div>
            <a href="/dashboard" class="dropdown-item">Dashboard</a>
            <a href="/products" class="dropdown-item">Products</a>
            <a href="/tutorial" class="dropdown-item">Tutorial</a>
            <a href="javascript:void(0)" onclick="openDepositModal()" class="dropdown-item" style="color: var(--primary-orange);">+ Deposit</a>
            <a href="javascript:void(0)" onclick="logoutUser()" class="dropdown-item" style="color: #ef4444; border-top: 1px solid var(--border-card); margin-top: 4px;">Sign Out</a>
          </div>
        `;
      }
    } else {
      currentUser = null;
      if (actionsContainer) {
        actionsContainer.innerHTML = `
          <a href="/login" class="btn btn-withdraw btn-sm">Sign In</a>
          <a href="/login?tab=register" class="btn btn-deposit btn-sm">Register</a>
        `;
      }
    }
  } catch (err) {
    console.error('Auth error:', err);
  }
}

function toggleUserMenu() {
  const menu = document.getElementById('user-dropdown');
  if (menu) {
    menu.classList.toggle('show');
  }
}

// Close dropdown on outside click
document.addEventListener('click', (e) => {
  const menu = document.getElementById('user-dropdown');
  const btn = document.getElementById('avatar-btn');
  if (menu && menu.classList.contains('show')) {
    if (!menu.contains(e.target) && e.target !== btn) {
      menu.classList.remove('show');
    }
  }
});

// ==========================================
// PRODUCTS CATALOG & OPTIONS (Screenshot 2)
// ==========================================

async function loadCatalog() {
  const container = document.getElementById('products-catalog-container');
  if (!container) return;

  try {
    const res = await fetch('/api/catalog');
    const data = await res.json();
    currentCatalog = data.catalog || [];

    const countEl = document.getElementById('products-count');
    if (countEl) countEl.innerText = `${currentCatalog.length} products`;

    if (currentCatalog.length === 0) {
      container.innerHTML = '<div class="empty-state"><p>No products available.</p></div>';
      return;
    }

    container.innerHTML = currentCatalog.map(item => `
      <div class="product-card-horizontal" style="cursor: pointer;" onclick="window.location.href='/product/${item.id}'">
        <div class="product-thumbnail-box">
          <img src="${item.image_url}" alt="${item.title}" class="product-thumbnail-img" onerror="this.src='/static/images/product1.jpg'">
          <span class="platform-badge">${item.platform}</span>
        </div>

        <div class="product-details">
          <span class="product-cat-label">${item.category}</span>
          <h2 class="product-title">${item.title}</h2>
          
          <div class="product-badges-row">
            <span class="pill-badge"><i class="fa-solid fa-layer-group" style="margin-right: 4px; font-size: 0.72rem;"></i> ${item.options_count} OPTIONS</span>
            <span class="pill-badge pill-badge-stock"><i class="fa-solid fa-circle" style="margin-right: 4px; font-size: 0.55rem; color: ${item.total_stock > 0 ? 'var(--badge-green)' : '#ef4444'};"></i> ${item.total_stock > 0 ? `${item.total_stock} IN STOCK` : 'OUT OF STOCK'}</span>
          </div>

          <div class="card-feature-pills" style="margin-bottom: 8px;">
            <span class="tech-tag-pill active">ESP</span>
            <span class="tech-tag-pill active">AIMBOT</span>
            <span class="tech-tag-pill">RADAR</span>
            <span class="tech-tag-pill">ANTI-BAN</span>
          </div>

          <div class="product-price-range">
            <span style="font-size: 0.76rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; margin-right: 4px;">STARTS ON</span> PHP 70.00
          </div>

          <a href="/product/${item.id}" class="btn-view-options" onclick="event.stopPropagation();">
            View options <i class="fa-solid fa-arrow-right" style="margin-left: 4px; font-size: 0.8rem;"></i>
          </a>
        </div>
      </div>
    `).join('');
  } catch (err) {
    container.innerHTML = '<p style="color: #ef4444; padding: 20px;">Failed to load products.</p>';
  }
}

function openOptionsModal(catalogId) {
  const item = currentCatalog.find(c => c.id === catalogId);
  if (!item) return;

  const modal = document.getElementById('options-modal');
  if (!modal) return;

  document.getElementById('opt-modal-title').innerText = item.title;
  document.getElementById('opt-modal-cat').innerText = item.category;

  const listContainer = document.getElementById('options-list');
  listContainer.innerHTML = item.options.map((opt, idx) => `
    <div class="option-select-item ${idx === 0 ? 'selected' : ''}" onclick="selectTierOption(${opt.id}, ${opt.price}, '${opt.name}')" id="opt-item-${opt.id}">
      <div>
        <div class="option-item-name">${opt.duration}</div>
        <div style="font-size: 0.75rem; color: var(--text-dark);">${opt.badge || 'Instant Delivery'} &bull; ${opt.stock > 0 ? `${opt.stock} in stock` : 'Auto-Gen'}</div>
      </div>
      <div class="option-item-price">₱${parseFloat(opt.price).toFixed(2)}</div>
    </div>
  `).join('');

  if (item.options.length > 0) {
    selectedOption = item.options[0];
    updateOptionSummary();
  }

  modal.classList.add('active');
}

function closeOptionsModal() {
  const modal = document.getElementById('options-modal');
  if (modal) modal.classList.remove('active');
}

function selectTierOption(id, price, name) {
  document.querySelectorAll('.option-select-item').forEach(el => el.classList.remove('selected'));
  const target = document.getElementById(`opt-item-${id}`);
  if (target) target.classList.add('selected');

  for (const item of currentCatalog) {
    const found = item.options.find(o => o.id === id);
    if (found) {
      selectedOption = found;
      break;
    }
  }

  updateOptionSummary();
}

function updateOptionSummary() {
  if (!selectedOption) return;
  const buyBtn = document.getElementById('btn-buy-option');
  if (buyBtn) {
    buyBtn.innerText = `PURCHASE FOR ₱${parseFloat(selectedOption.price).toFixed(2)}`;
  }
}

async function handlePurchaseSelected() {
  if (!currentUser) {
    showToast('Please sign in to make a purchase!', 'error');
    setTimeout(() => { window.location.href = '/login'; }, 1000);
    return;
  }

  if (!selectedOption) {
    showToast('Please select a duration option.', 'error');
    return;
  }

  const price = parseFloat(selectedOption.price);
  if (currentUser.balance < price) {
    const diff = price - currentUser.balance;
    closeOptionsModal();
    openDepositModal(Math.ceil(diff));
    showToast(`Insufficient credits! You need ₱${diff.toFixed(2)} more.`, 'error');
    return;
  }

  const buyBtn = document.getElementById('btn-buy-option');
  if (buyBtn) {
    buyBtn.disabled = true;
    buyBtn.innerText = 'Delivering key...';
  }

  try {
    const res = await fetch('/api/purchase', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_id: selectedOption.id })
    });

    const data = await res.json();
    if (!res.ok) {
      showToast(data.error || 'Purchase failed', 'error');
      if (buyBtn) {
        buyBtn.disabled = false;
        buyBtn.innerText = `PURCHASE FOR ₱${price.toFixed(2)}`;
      }
      return;
    }

    // Success
    currentUser.balance = data.new_balance;
    const navCoin = document.getElementById('nav-coin-val');
    if (navCoin) navCoin.innerText = parseFloat(data.new_balance).toFixed(2);

    closeOptionsModal();
    showKeyModal(data);
  } catch (err) {
    showToast('Network error during purchase.', 'error');
    if (buyBtn) {
      buyBtn.disabled = false;
      buyBtn.innerText = `PURCHASE FOR ₱${price.toFixed(2)}`;
    }
  }
}

function showKeyModal(data) {
  const modal = document.getElementById('key-delivery-modal');
  if (!modal) return;

  document.getElementById('delivered-key-tier').innerText = data.product_name;
  document.getElementById('delivered-key-text').innerText = data.license_key;
  document.getElementById('delivered-key-order').innerText = `Order ID: ${data.order_id}`;

  modal.classList.add('active');
}

function closeKeyModal() {
  const modal = document.getElementById('key-delivery-modal');
  if (modal) modal.classList.remove('active');
}

// ==========================================
// DASHBOARD VIEW (Screenshot 1)
// ==========================================

async function loadDashboardStats() {
  try {
    const res = await fetch('/api/dashboard/stats');
    if (res.status === 401) {
      window.location.href = '/login';
      return;
    }

    const data = await res.json();

    // Welcome user
    const userEl = document.getElementById('dash-welcome-user');
    if (userEl) userEl.innerText = data.username;

    // Wallet Balance
    const balEl = document.getElementById('dash-balance-val');
    if (balEl) balEl.innerText = parseFloat(data.balance).toFixed(2);

    // Top Hero Stats
    const totalKeysEl = document.getElementById('dash-total-keys-val');
    if (totalKeysEl) totalKeysEl.innerText = data.total_keys !== undefined ? data.total_keys : '0';

    // 3 Global Stat Bar Cards (Users, Orders, Products)
    const registeredUsersEl = document.getElementById('stat-registered-users');
    if (registeredUsersEl) {
      const uCount = data.registered_users || 0;
      registeredUsersEl.innerText = Number(uCount).toLocaleString();
    }

    const totalOrdersEl = document.getElementById('stat-total-orders');
    if (totalOrdersEl) {
      const oCount = data.global_orders !== undefined ? data.global_orders : data.total_orders || 0;
      totalOrdersEl.innerText = Number(oCount).toLocaleString();
    }

    const totalProductsEl = document.getElementById('stat-total-products');
    if (totalProductsEl) {
      totalProductsEl.innerText = data.total_products !== undefined ? data.total_products : '1';
    }

    // Render Featured Products
    loadFeaturedProducts();

    // Render Recent Orders
    renderRecentOrders(data.recent_orders || []);

    // Render Recent Transactions
    renderRecentTransactions(data.recent_transactions || []);
  } catch (err) {
    console.error('Dashboard load error:', err);
  }
}

async function loadFeaturedProducts() {
  const container = document.getElementById('featured-products-grid');
  if (!container) return;

  try {
    const res = await fetch('/api/catalog');
    const data = await res.json();
    const items = data.catalog || [];

    if (items.length === 0) {
      container.innerHTML = '<div class="empty-state" style="grid-column: 1 / -1;"><p>No featured products available.</p></div>';
      return;
    }

    container.innerHTML = items.map(item => {
      const isCodm = item.id === 1 || (item.title && item.title.toLowerCase().includes('codm'));
      const priceHtml = isCodm
        ? `<div class="featured-card-price"><span class="price-starts-label">STARTS ON</span> PHP 70.00</div>`
        : `<div class="featured-card-price"><span class="price-starts-label">STARTS ON</span> PHP ${parseFloat(item.min_price || 70).toFixed(2)}</div>`;

      return `
        <div class="featured-prod-card tilt-card" data-tilt onclick="window.location.href='/product/${item.id}'">
          <div class="featured-thumb-wrap">
            <img src="${item.image_url}" alt="${item.title}" class="featured-thumb-img" onerror="this.src='/static/images/product1.jpg'">
            <div class="featured-badge-stock">
              <span class="stock-live-dot"></span> STOCK
            </div>
            <div class="featured-badge-platform">${item.platform || 'ANDROID'}</div>
          </div>

          <div class="featured-card-info">
            <h3 class="featured-card-title">${item.title}</h3>
            
            <div class="card-feature-pills">
              <span class="tech-tag-pill active">ESP</span>
              <span class="tech-tag-pill active">AIMBOT</span>
              <span class="tech-tag-pill">RADAR</span>
              <span class="tech-tag-pill">NO RECOIL</span>
              <span class="tech-tag-pill">BYPASS</span>
            </div>

            ${priceHtml}
            
            <a href="/product/${item.id}" class="btn-featured-buy" onclick="event.stopPropagation();">
              <i class="fa-solid fa-bolt"></i> BUY
            </a>
          </div>
        </div>
      `;
    }).join('');

    if (typeof initTilt3D === 'function') {
      initTilt3D();
    }
  } catch (err) {
    console.error('Featured products error:', err);
  }
}

function renderRecentOrders(orders) {
  const container = document.getElementById('recent-orders-box');
  if (!container) return;

  if (orders.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <svg class="empty-cart-icon" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 3h1.386c.51 0 .955.343 1.087.835l.383 1.437M7.5 14.25a3 3 0 0 0-3 3h15.75m-12.75-3h11.218c1.121-2.3 2.1-4.684 2.924-7.138a60.114 60.114 0 0 0-16.536-1.84M7.5 14.25 5.106 5.272M6 20.25a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0Zm12.75 0a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0Z"/></svg>
        <p>No orders yet. <a href="/products">Browse products →</a></p>
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <div class="table-wrap">
      <table class="dash-table">
        <thead>
          <tr>
            <th>Product Tier</th>
            <th>License Key</th>
            <th>Price</th>
            <th>Order Date</th>
          </tr>
        </thead>
        <tbody>
          ${orders.map(o => `
            <tr>
              <td style="font-weight: 700; color: #fff;">${o.product_name}</td>
              <td>
                <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                  <span style="font-family: var(--font-mono); color: var(--primary-orange); font-size: 0.85rem;">${o.license_key}</span>
                  <button class="btn btn-sm btn-orange-outline" style="padding: 2px 8px; font-size: 0.7rem;" onclick="copyText('${o.license_key}')">Copy</button>
                  <a href="https://t.me/ovkfiles" target="_blank" class="btn btn-sm" style="padding: 2px 8px; font-size: 0.7rem; background: rgba(0, 136, 204, 0.2); border: 1px solid rgba(0, 136, 204, 0.4); color: #38bdf8; text-decoration: none; border-radius: 4px;" title="Download loader and files from official channel"><i class="fa-solid fa-download"></i> Files</a>
                </div>
              </td>
              <td style="font-family: var(--font-mono); font-weight: 700; color: #f8fafc;">₱${parseFloat(o.price).toFixed(2)}</td>
              <td style="color: var(--text-dark);">${new Date(o.created_at).toLocaleDateString()}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}

function renderRecentTransactions(txs) {
  const container = document.getElementById('recent-tx-box');
  if (!container) return;

  if (txs.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <p style="color: var(--text-dark);">No transactions recorded yet.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <div class="table-wrap">
      <table class="dash-table">
        <thead>
          <tr>
            <th>Type</th>
            <th>Reference</th>
            <th>Amount</th>
            <th>Status</th>
            <th>Date</th>
          </tr>
        </thead>
        <tbody>
          ${txs.map(t => {
            const isDeposit = t.type === 'deposit';
            const color = isDeposit ? '#f8fafc' : '#f59e0b';
            const sign = isDeposit ? '+' : '-';
            return `
              <tr>
                <td style="text-transform: uppercase; font-weight: 700; font-size: 0.75rem; color: ${color};">${t.type}</td>
                <td style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--text-muted);">${t.reference_id}</td>
                <td style="font-family: var(--font-mono); font-weight: 700; color: ${color};">${sign}₱${parseFloat(t.amount).toFixed(2)}</td>
                <td>
                  <span style="font-size: 0.7rem; font-weight: 700; text-transform: uppercase; padding: 2px 8px; border-radius: var(--radius-full); ${t.status === 'completed' ? 'background: rgba(255, 255, 255, 0.15); color: #f8fafc;' : 'background: rgba(245, 158, 11, 0.15); color: #f59e0b;'}">${t.status}</span>
                </td>
                <td style="color: var(--text-dark);">${new Date(t.created_at).toLocaleString()}</td>
              </tr>
            `;
          }).join('')}
        </tbody>
      </table>
    </div>
  `;
}

// ==========================================
// DEPOSIT MODAL (PAYMONGO INTEGRATION)
// ==========================================

const ALLOWED_DEPOSIT_PRESETS = [70, 100, 150, 200, 250, 300, 320, 500, 700, 1000];

function openDepositModal(suggestedAmount = null) {
  if (!currentUser) {
    window.location.href = '/login';
    return;
  }

  const modal = document.getElementById('deposit-modal');
  if (!modal) return;

  const input = document.getElementById('deposit-amt-input');
  if (suggestedAmount) {
    const matched = ALLOWED_DEPOSIT_PRESETS.find(p => p >= suggestedAmount) || 1000;
    selectedDepositAmount = matched;
  } else if (!ALLOWED_DEPOSIT_PRESETS.includes(selectedDepositAmount)) {
    selectedDepositAmount = 100;
  }

  if (input) input.value = selectedDepositAmount;
  highlightPreset(selectedDepositAmount);

  modal.classList.add('active');
}

function closeDepositModal() {
  const modal = document.getElementById('deposit-modal');
  if (modal) modal.classList.remove('active');
}

function selectDepositPreset(amt) {
  selectedDepositAmount = amt;
  const input = document.getElementById('deposit-amt-input');
  if (input) input.value = amt;
  highlightPreset(amt);
}

function highlightPreset(amt) {
  document.querySelectorAll('.preset-chip').forEach(btn => {
    btn.classList.toggle('active', parseInt(btn.dataset.amount) === parseInt(amt));
  });
}

async function proceedPaymongoCheckout() {
  const input = document.getElementById('deposit-amt-input');
  const amount = parseFloat(input ? input.value : selectedDepositAmount);

  if (isNaN(amount) || amount < 20) {
    showToast('Minimum deposit is ₱20.00', 'error');
    return;
  }

  const btn = document.getElementById('btn-paymongo-checkout');
  if (btn) {
    btn.disabled = true;
    btn.innerText = 'Connecting to PayMongo...';
  }

  try {
    const res = await fetch('/api/wallet/create-checkout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount })
    });

    const data = await res.json();
    if (!res.ok) {
      showToast(data.error || 'Failed to initialize PayMongo', 'error');
      if (btn) {
        btn.disabled = false;
        btn.innerText = 'DEPOSIT VIA PAYMONGO (GCASH / MAYA)';
      }
      return;
    }

    if (data.demo_mode) {
      const sBox = document.getElementById('sandbox-deposit-box');
      if (sBox) sBox.style.display = 'block';
      showToast(data.message, 'info');
      if (btn) {
        btn.disabled = false;
        btn.innerText = 'DEPOSIT VIA PAYMONGO (GCASH / MAYA)';
      }
      return;
    }

    if (data.session_id) {
      localStorage.setItem('ovk_pending_checkout', data.session_id);
    }

    if (data.checkout_url) {
      showToast('Redirecting to PayMongo secure payment...', 'success');
      setTimeout(() => { window.location.href = data.checkout_url; }, 800);
    }
  } catch (err) {
    showToast('Could not reach payment service.', 'error');
    if (btn) {
      btn.disabled = false;
      btn.innerText = 'DEPOSIT VIA PAYMONGO (GCASH / MAYA)';
    }
  }
}

async function triggerSandboxTopUp() {
  const input = document.getElementById('deposit-amt-input');
  const amount = parseFloat(input ? input.value : selectedDepositAmount);

  if (isNaN(amount) || amount < 20) {
    showToast('Minimum amount is ₱20.00', 'error');
    return;
  }

  try {
    const res = await fetch('/api/wallet/simulate-deposit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount })
    });

    const data = await res.json();
    if (!res.ok) {
      showToast(data.error || 'Deposit failed', 'error');
      return;
    }

    showToast(data.message, 'success');
    currentUser.balance = data.new_balance;

    const navCoin = document.getElementById('nav-coin-val');
    if (navCoin) navCoin.innerText = parseFloat(data.new_balance).toFixed(2);

    const dashBal = document.getElementById('dash-balance-val');
    if (dashBal) dashBal.innerText = parseFloat(data.new_balance).toFixed(2);

    closeDepositModal();

    if (typeof loadDashboardStats === 'function') {
      loadDashboardStats();
    }
  } catch (err) {
    showToast('Sandbox deposit failed.', 'error');
  }
}

// ==========================================
// UTILITIES
// ==========================================

function setupEventListeners() {
  document.querySelectorAll('.preset-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      selectDepositPreset(parseInt(chip.dataset.amount));
    });
  });

  const amtInput = document.getElementById('deposit-amt-input');
  if (amtInput) {
    amtInput.addEventListener('input', (e) => {
      selectedDepositAmount = parseFloat(e.target.value) || 0;
      highlightPreset(selectedDepositAmount);
    });
  }

  // Filter search on products page
  const searchInput = document.getElementById('catalog-search-input');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      const query = e.target.value.toLowerCase();
      document.querySelectorAll('.product-card-horizontal').forEach(card => {
        const title = card.querySelector('.product-title').innerText.toLowerCase();
        card.style.display = title.includes(query) ? 'flex' : 'none';
      });
    });
  }
}

function copyDeliveredKey() {
  const keyText = document.getElementById('delivered-key-text').innerText;
  copyText(keyText);
}

function copyText(text) {
  navigator.clipboard.writeText(text).then(() => {
    showToast('Copied to clipboard!', 'success');
  }).catch(() => {
    showToast('Failed to copy', 'error');
  });
}

function copyReferralLink() {
  const refLink = `${window.location.origin}/login?ref=${currentUser ? currentUser.username : 'user'}`;
  copyText(refLink);
}

async function logoutUser() {
  try {
    await fetch('/api/auth/logout', { method: 'POST' });
    showToast('Signed out.', 'info');
    setTimeout(() => { window.location.href = '/login'; }, 500);
  } catch (err) {
    window.location.reload();
  }
}

function showToast(msg, type = 'info') {
  let box = document.getElementById('toast-container');
  if (!box) {
    box = document.createElement('div');
    box.id = 'toast-container';
    box.className = 'toast-box';
    document.body.appendChild(box);
  }

  const toast = document.createElement('div');
  toast.className = `toast-msg ${type}`;
  
  if (msg.toLowerCase().includes('loading')) {
    toast.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin" style="color: var(--primary-orange); margin-right: 8px;"></i><span>${msg}</span>`;
  } else {
    toast.innerText = msg;
  }
  
  toast.style.animation = 'toastSlideIn 0.28s cubic-bezier(0.16, 1, 0.3, 1) forwards';
  box.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(20px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// ==========================================
// STEALTH ADMIN ACCESS GATEWAY
// (Trigger via Ctrl+Shift+A or triple-click on brand logo)
// ==========================================
document.addEventListener('keydown', (e) => {
  if (e.ctrlKey && e.shiftKey && (e.key === 'A' || e.key === 'a')) {
    e.preventDefault();
    openStealthGate();
  }
});

let logoClickCount = 0;
let logoClickTimer = null;
document.addEventListener('DOMContentLoaded', () => {
  const brandLogo = document.querySelector('.brand-logo');
  if (brandLogo) {
    brandLogo.addEventListener('click', (e) => {
      logoClickCount++;
      clearTimeout(logoClickTimer);
      if (logoClickCount >= 5) {
        e.preventDefault();
        logoClickCount = 0;
        openStealthGate();
      } else {
        logoClickTimer = setTimeout(() => { logoClickCount = 0; }, 1200);
      }
    });
  }
});

function openStealthGate() {
  window.location.href = '/admin';
}

// ==========================================
// 3D TACTICAL CARD TILT & HOVER SPRING ENGINE
// ==========================================
function initTilt3D() {
  // Motion and tilting disabled per user request
  const tiltElements = document.querySelectorAll('.tilt-card, [data-tilt]');
  tiltElements.forEach(card => {
    card.style.transform = 'none';
  });
}

// Live Time for Enforcement Banner
function updateLiveDashboardTime() {
  const el = document.getElementById('dash-live-time');
  if (!el) return;
  const now = new Date();
  const months = ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER'];
  const monthName = months[now.getMonth()];
  const year = now.getFullYear();
  const timeStr = now.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
  el.innerText = `${monthName} ${year} &bull; SYS TIME: ${timeStr} &bull; ALL BUILDS ONLINE`;
}

document.addEventListener('DOMContentLoaded', () => {
  initTilt3D();
  updateLiveDashboardTime();
  setInterval(updateLiveDashboardTime, 1000);
});


// ==========================================
// INTERACTIVE FONT PICKER SYSTEM
// ==========================================
const AVAILABLE_FONTS = [
  { id: 'font-syne', name: 'Syne Avant-Garde', desc: 'Elite Luxury & Editorial' },
  { id: 'font-space', name: 'Space Grotesk', desc: 'Precision Hacker High-Tech' },
  { id: 'font-rajdhani', name: 'Rajdhani Tactical', desc: 'Special Ops Monospace' },
  { id: 'font-jakarta', name: 'Jakarta Crisp', desc: 'Clean Minimalist' },
  { id: 'font-chakra', name: 'Chakra Petch', desc: 'Cyber Syndicate' },
  { id: 'font-orbitron', name: 'Orbitron Stealth', desc: 'Sub-Zero Futuristic' }
];

function applySavedFont() {
  const saved = localStorage.getItem('ovk_active_font') || 'font-syne';
  document.body.className = document.body.className.replace(/\bfont-\w+\b/g, '').trim();
  document.body.classList.add(saved);
}

function selectFont(fontId) {
  localStorage.setItem('ovk_active_font', fontId);
  applySavedFont();
  const menu = document.getElementById('font-picker-dropdown');
  if (menu) menu.classList.remove('show');
  renderFontPickerItems();
}

function toggleFontPicker(e) {
  if (e) e.stopPropagation();
  const menu = document.getElementById('font-picker-dropdown');
  if (menu) menu.classList.toggle('show');
}

function renderFontPickerItems() {
  const list = document.getElementById('font-picker-list');
  if (!list) return;
  const current = localStorage.getItem('ovk_active_font') || 'font-jakarta';
  list.innerHTML = AVAILABLE_FONTS.map(f => `
    <div class="font-picker-item ${f.id === current ? 'active' : ''}" onclick="selectFont('${f.id}')">
      <div>
        <div style="font-weight: 700;">${f.name}</div>
        <div style="font-size: 0.68rem; color: var(--text-dark);">${f.desc}</div>
      </div>
      ${f.id === current ? '<i class="fa-solid fa-check" style="font-size: 0.75rem;"></i>' : ''}
    </div>
  `).join('');
}

document.addEventListener('click', (e) => {
  const menu = document.getElementById('font-picker-dropdown');
  const btn = document.getElementById('font-picker-btn');
  if (menu && menu.classList.contains('show')) {
    if (!menu.contains(e.target) && e.target !== btn && !btn.contains(e.target)) {
      menu.classList.remove('show');
    }
  }
});

// Run font init immediately
applySavedFont();


// ==========================================
// SUPPORT & HELP MODAL FUNCTIONS (Reference Layout)
// ==========================================
function openSupportModal() {
  const modal = document.getElementById('support-modal');
  if (modal) {
    modal.classList.add('active');
  } else {
    window.open('https://t.me/kovalucy', '_blank');
  }
}

function closeSupportModal() {
  const modal = document.getElementById('support-modal');
  if (modal) modal.classList.remove('active');
}

function toggleFaqItem(itemEl) {
  if (!itemEl) return;
  const wasOpen = itemEl.classList.contains('open');
  // Optional: close siblings if you want single-item accordion
  document.querySelectorAll('.support-faq-item').forEach(el => el.classList.remove('open'));
  if (!wasOpen) {
    itemEl.classList.add('open');
  }
}

// ==========================================
// SMOOTH 3D TAB NAVIGATION TRANSITIONS
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
  const navLinks = document.querySelectorAll('.nav-pill-item a');
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      const href = link.getAttribute('href');
      // Ignore JS triggers, external links or current page
      if (!href || href.startsWith('javascript') || href.startsWith('#') || link.classList.contains('active')) {
        return;
      }
      
      const targetUrl = new URL(link.href, window.location.origin);
      if (targetUrl.origin === window.location.origin && targetUrl.pathname !== window.location.pathname) {
        e.preventDefault();
        showToast('Loading.. Please wait.', 'info');
        const pageWrap = document.querySelector('.page-wrap');
        if (pageWrap) {
          pageWrap.classList.add('page-switching-out');
          setTimeout(() => {
            window.location.href = href;
          }, 240);
        } else {
          window.location.href = href;
        }
      }
    });
  });
});
