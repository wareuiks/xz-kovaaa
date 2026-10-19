with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

# 1. Add Slanted Bold Cartoony Font Import
old_fonts = "@import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600;700;800&family=Rajdhani:wght@600;700;800&family=Orbitron:wght@600;700;800;900&family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Outfit:wght@500;600;700;800;900&family=Inter:wght@500;600;700;800;900&display=swap');"
new_fonts = "@import url('https://fonts.googleapis.com/css2?family=Paytone+One&family=Righteous&family=Plus+Jakarta+Sans:ital,wght@0,600;0,700;0,800;1,700;1,800&display=swap');"

if old_fonts in css:
    css = css.replace(old_fonts, new_fonts)
else:
    css = new_fonts + '\n' + css

# 2. Update default display and heading fonts to slanted bold cartoony style
css = css.replace(
'''  --font-display: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-heading: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;''',
'''  --font-display: 'Paytone One', 'Righteous', 'Plus Jakarta Sans', sans-serif;
  --font-heading: 'Paytone One', 'Righteous', 'Plus Jakarta Sans', sans-serif;
  --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;'''
)

# 3. Add styles for Support Modal (Matching Reference Image) and Mobile Tab visibility
support_css = '''
/* ==========================================
   SUPPORT & HELP MODAL (Reference Design)
   ========================================== */

.support-modal-box {
  background: #0e121a;
  border: 1px solid #1a2234;
  border-radius: 20px;
  max-width: 680px;
  width: 94%;
  padding: 32px 28px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.85);
  max-height: 90vh;
  overflow-y: auto;
}

.support-modal-header {
  text-align: center;
  margin-bottom: 24px;
}

.support-main-title {
  font-family: var(--font-display);
  font-style: italic;
  font-size: 2rem;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: -0.5px;
  margin-bottom: 6px;
}

.support-main-subtext {
  font-size: 0.88rem;
  color: #94a3b8;
}

.support-faq-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

.support-faq-item {
  background: #141924;
  border: 1px solid #1f293d;
  border-radius: 14px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
}

.support-faq-item:hover {
  border-color: rgba(255, 154, 0, 0.4);
  background: #161c28;
}

.support-faq-item.open {
  border-color: rgba(255, 154, 0, 0.5);
  background: #151b27;
}

.faq-item-head {
  padding: 16px 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  user-select: none;
}

.faq-head-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.faq-icon-box {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.95rem;
  flex-shrink: 0;
}

.icon-purple {
  background: rgba(168, 85, 247, 0.15);
  color: #a855f7;
  border: 1px solid rgba(168, 85, 247, 0.3);
}

.icon-green {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.icon-red {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.icon-amber {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.faq-question {
  font-family: var(--font-heading);
  font-size: 0.96rem;
  font-weight: 700;
  color: #ffffff;
  line-height: 1.25;
}

.faq-hint {
  font-size: 0.72rem;
  color: #64748b;
  margin-top: 2px;
}

.faq-chevron {
  color: #64748b;
  font-size: 0.85rem;
  transition: transform 0.25s ease;
}

.support-faq-item.open .faq-chevron {
  transform: rotate(180deg);
  color: var(--primary-orange);
}

.faq-item-body {
  padding: 0 18px 16px 68px;
  font-size: 0.86rem;
  color: #cbd5e1;
  line-height: 1.55;
  display: none;
  border-top: 1px solid rgba(255, 255, 255, 0.04);
  padding-top: 12px;
  margin-top: -2px;
}

.support-faq-item.open .faq-item-body {
  display: block;
}

/* Bottom help contact box */
.support-bottom-card {
  background: #11151f;
  border: 1px solid #1a2233;
  border-radius: 16px;
  padding: 22px 20px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.support-agent-icon {
  width: 44px;
  height: 44px;
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #10b981;
  font-size: 1.2rem;
  margin-bottom: 10px;
}

.support-bottom-title {
  font-family: var(--font-display);
  font-style: italic;
  font-size: 1.25rem;
  font-weight: 800;
  color: #ffffff;
  margin-bottom: 4px;
}

.support-bottom-sub {
  font-size: 0.82rem;
  color: #94a3b8;
  max-width: 400px;
  margin-bottom: 16px;
}

.support-action-buttons {
  display: flex;
  gap: 12px;
  width: 100%;
  max-width: 380px;
}

.btn-support-channel {
  flex: 1;
  padding: 10px 16px;
  border-radius: 9999px;
  font-size: 0.85rem;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  text-decoration: none;
  transition: all 0.2s ease;
}

.btn-tg {
  background: #0088cc;
  color: #ffffff;
}

.btn-tg:hover {
  background: #0099e6;
  transform: translateY(-1px);
}

.btn-files {
  background: rgba(255, 154, 0, 0.15);
  border: 1px solid rgba(255, 154, 0, 0.4);
  color: #ff9a00;
}

.btn-files:hover {
  background: rgba(255, 154, 0, 0.25);
  color: #ffffff;
  transform: translateY(-1px);
}

/* ==========================================
   ENHANCED MOBILE NAVIGATION (All 4 Tabs Visible)
   ========================================== */
@media (max-width: 768px) {
  .site-header {
    height: auto;
    padding: 8px 0 10px;
  }
  .header-container {
    flex-wrap: wrap;
    gap: 8px;
    align-items: center;
  }
  .brand-logo-text {
    font-size: 1.35rem;
  }
  .brand-logo-img {
    width: 36px;
    height: 36px;
  }
  .nav-pills {
    order: 3;
    width: 100%;
    display: flex !important;
    flex-direction: row !important;
    justify-content: space-between;
    padding: 3px;
    margin-top: 6px;
    gap: 3px;
    border-radius: 10px;
  }
  .nav-pill-item {
    flex: 1;
    text-align: center;
  }
  .nav-pill-item a {
    display: block;
    width: 100%;
    padding: 8px 2px;
    font-size: 0.72rem;
    font-weight: 800;
    white-space: nowrap;
    text-align: center;
    letter-spacing: 0.3px;
    border-radius: 6px;
  }
}
'''

css += '\n' + support_css

with open('static/css/style.css', 'w', encoding='utf-8') as f:
    f.write(css)

print("style.css updated with Paytone One font, support modal, and mobile nav rules")
