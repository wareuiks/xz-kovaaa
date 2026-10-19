with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    h = f.read()

# Locate the DASHBOARD TITLE to the end of stats-grid-2x2
start_mark = '<!-- DASHBOARD TITLE -->'
end_mark = '<!-- FEATURED PRODUCTS -->'

start_idx = h.find(start_mark)
end_idx = h.find(end_mark)

if start_idx != -1 and end_idx != -1:
    new_block = '''<!-- CID-STYLE HERO BANNER (Matches Reference Layout) -->
      <div class="cid-hero-banner">
        <div class="cid-hero-bg-accent"></div>
        <div class="cid-hero-content">
          <div class="cid-hero-welcome">Welcome back</div>
          <div class="cid-hero-username" id="dash-welcome-user">Member</div>
        </div>
      </div>

      <!-- FLOATING WALLET & TOTAL KEYS CARD -->
      <div class="cid-wallet-panel">
        <div class="cid-wallet-grid">
          <div class="cid-wallet-cell">
            <div class="cid-cell-lbl">Wallet balance</div>
            <div class="cid-cell-val cid-balance-val">₱<span id="dash-balance-val">0.00</span></div>
          </div>
          <div class="cid-wallet-cell">
            <div class="cid-cell-lbl">Total keys</div>
            <div class="cid-cell-val cid-keys-val" id="dash-total-keys-val">0</div>
          </div>
        </div>

        <div class="cid-wallet-btn-row">
          <button class="btn cid-btn-deposit" onclick="openDepositModal()">
            <i class="fa-solid fa-arrow-down"></i> Deposit
          </button>
          <button class="btn cid-btn-withdraw" onclick="openWithdrawModal()">
            <i class="fa-solid fa-arrow-up"></i> Withdraw
          </button>
        </div>
      </div>

      <!-- 3-COLUMN STAT BAR (Users / Orders / Products) -->
      <div class="cid-stats-bar">
        <!-- 1. Users (Registered to the web) -->
        <div class="cid-stat-col">
          <div class="cid-stat-icon cid-icon-green">
            <i class="fa-solid fa-user-group"></i>
          </div>
          <div class="cid-stat-number" id="stat-registered-users">0</div>
          <div class="cid-stat-label">Users</div>
        </div>

        <div class="cid-stat-divider"></div>

        <!-- 2. Orders -->
        <div class="cid-stat-col">
          <div class="cid-stat-icon cid-icon-green">
            <i class="fa-solid fa-check"></i>
          </div>
          <div class="cid-stat-number" id="stat-total-orders">0</div>
          <div class="cid-stat-label">Orders</div>
        </div>

        <div class="cid-stat-divider"></div>

        <!-- 3. Products -->
        <div class="cid-stat-col">
          <div class="cid-stat-icon cid-icon-green">
            <i class="fa-solid fa-key"></i>
          </div>
          <div class="cid-stat-number" id="stat-total-products">1</div>
          <div class="cid-stat-label">Products</div>
        </div>
      </div>

      '''
    h = h[:start_idx] + new_block + h[end_idx:]
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(h)
    print('dashboard.html updated successfully')
else:
    print('Indices not found:', start_idx, end_idx)
