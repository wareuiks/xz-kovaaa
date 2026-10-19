with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Replace font imports with Plus Jakarta Sans and Outfit
old_import = "@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Chakra+Petch:ital,wght@0,400;0,600;0,700;1,700&family=Rajdhani:wght@500;600;700;800&family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600;700;800&display=swap');"
new_import = "@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,700;1,800&family=Outfit:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600;700;800&display=swap');"

if old_import in css:
    css = css.replace(old_import, new_import)

# Update font tokens to Plus Jakarta Sans & Outfit
css = css.replace(
'''  --font-display: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-heading: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;''',
'''  --font-display: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-heading: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;'''
)

# Now replace the dashboard CSS section with the new CID reference styles
start_mark = '/* ==========================================\n   DASHBOARD (Screenshot 1)'
end_mark = '/* ==========================================\n   FEATURED PRODUCTS'

start_idx = css.find(start_mark)
end_idx = css.find(end_mark)

new_dashboard_css = '''/* ==========================================
   DASHBOARD (Cid Reference Exact Layout)
   ========================================== */
.page-wrap {
  padding: 30px 0 80px;
}

/* 1. Curved Hero Welcome Banner */
.cid-hero-banner {
  background: linear-gradient(135deg, rgba(255, 154, 0, 0.16), rgba(255, 154, 0, 0.05)), #121824;
  border: 1px solid rgba(255, 154, 0, 0.25);
  border-radius: 20px;
  padding: 28px 36px 65px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

.cid-hero-bg-accent {
  position: absolute;
  top: 0;
  right: 0;
  width: 220px;
  height: 100%;
  background: radial-gradient(circle at 85% 20%, rgba(255, 154, 0, 0.35) 0%, rgba(230, 138, 0, 0.15) 50%, transparent 75%);
  pointer-events: none;
  border-top-right-radius: 20px;
}

.cid-hero-content {
  position: relative;
  z-index: 2;
}

.cid-hero-welcome {
  font-size: 0.88rem;
  font-weight: 600;
  color: #cbd5e1;
  letter-spacing: -0.2px;
  margin-bottom: 2px;
}

.cid-hero-username {
  font-size: 1.75rem;
  font-weight: 800;
  font-style: italic;
  letter-spacing: -0.5px;
  color: #ffffff;
  line-height: 1.15;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.6);
}

/* 2. Floating Wallet & Total Keys Card (Overlaps Banner) */
.cid-wallet-panel {
  background: #111723;
  border: 1px solid var(--border-card);
  border-radius: 18px;
  padding: 24px 28px;
  margin-top: -42px;
  margin-bottom: 24px;
  position: relative;
  z-index: 5;
  box-shadow: 0 14px 34px rgba(0, 0, 0, 0.65), 0 0 0 1px rgba(255, 255, 255, 0.04);
}

.cid-wallet-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 20px;
}

@media (max-width: 580px) {
  .cid-wallet-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}

.cid-wallet-cell {
  display: flex;
  flex-direction: column;
}

.cid-cell-lbl {
  font-size: 0.78rem;
  font-weight: 600;
  color: #94a3b8;
  margin-bottom: 6px;
  letter-spacing: -0.1px;
}

.cid-cell-val {
  font-size: 2.2rem;
  font-weight: 800;
  letter-spacing: -0.8px;
  line-height: 1;
}

.cid-balance-val {
  color: var(--primary-orange);
  text-shadow: 0 0 20px rgba(255, 154, 0, 0.3);
}

.cid-keys-val {
  color: #ffffff;
}

.cid-wallet-btn-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

@media (max-width: 580px) {
  .cid-wallet-btn-row {
    grid-template-columns: 1fr;
  }
}

.cid-btn-deposit {
  background: linear-gradient(135deg, var(--primary-orange), var(--primary-orange-hover));
  color: #000000;
  font-weight: 800;
  font-style: italic;
  font-size: 0.95rem;
  padding: 13px 20px;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 4px 16px var(--primary-orange-glow);
  border: none;
  cursor: pointer;
  transition: var(--transition);
}

.cid-btn-deposit:hover {
  background: linear-gradient(135deg, #ffa826, #ea9200);
  box-shadow: 0 6px 24px rgba(255, 154, 0, 0.65);
  transform: translateY(-2px);
}

.cid-btn-withdraw {
  background: rgba(255, 154, 0, 0.08);
  color: #ffd494;
  border: 1px solid rgba(255, 154, 0, 0.22);
  font-weight: 800;
  font-style: italic;
  font-size: 0.95rem;
  padding: 13px 20px;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: var(--transition);
}

.cid-btn-withdraw:hover {
  background: rgba(255, 154, 0, 0.16);
  border-color: rgba(255, 154, 0, 0.4);
  color: #ffffff;
  transform: translateY(-2px);
}

/* 3. Sleek 3-Column Stats Bar (Users, Orders, Products) */
.cid-stats-bar {
  background: #101520;
  border: 1px solid var(--border-card);
  border-radius: 16px;
  padding: 18px 24px;
  margin-bottom: 28px;
  display: grid;
  grid-template-columns: 1fr auto 1fr auto 1fr;
  align-items: center;
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.4);
}

@media (max-width: 640px) {
  .cid-stats-bar {
    grid-template-columns: 1fr;
    gap: 16px;
    padding: 20px;
  }
  .cid-stat-divider {
    display: none;
  }
}

.cid-stat-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 4px;
}

.cid-stat-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.92rem;
  margin-bottom: 4px;
}

.cid-icon-green {
  background: rgba(255, 154, 0, 0.14);
  color: var(--primary-orange);
  border: 1px solid rgba(255, 154, 0, 0.3);
}

.cid-stat-number {
  font-size: 1.55rem;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: -0.5px;
  line-height: 1;
}

.cid-stat-label {
  font-size: 0.76rem;
  font-weight: 600;
  color: #94a3b8;
  letter-spacing: -0.1px;
}

.cid-stat-divider {
  width: 1px;
  height: 48px;
  background: rgba(255, 255, 255, 0.08);
}

'''

if start_idx != -1 and end_idx != -1:
    css = css[:start_idx] + new_dashboard_css + css[end_idx:]
    with open('static/css/style.css', 'w', encoding='utf-8') as f:
        f.write(css)
    print('style.css updated successfully with Cid reference styles')
else:
    print('Dashboard boundaries not found:', start_idx, end_idx)
