import os, glob

# 1. Update templates to have the rounded logo image beside OVK HAX:
# <a href="/dashboard" class="brand-logo">
#   <img src="/static/images/logo.png" alt="OVK Logo" class="brand-logo-img">
#   <span class="brand-logo-text">OVK HAX</span>
# </a>

templates = [
    'templates/dashboard.html',
    'templates/products.html',
    'templates/product_detail.html',
    'templates/tutorial.html',
    'templates/login.html'
]

logo_replacement = '''<a href="/dashboard" class="brand-logo">
        <img src="/static/images/logo.png" alt="OVK Logo" class="brand-logo-img">
        <span class="brand-logo-text">OVK HAX</span>
      </a>'''

for tpath in templates:
    if not os.path.exists(tpath): continue
    with open(tpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace any previous brand logo anchor
    old_logos = [
        '<a href="/dashboard" class="brand-logo">OVKSHOP</a>',
        '<a href="/products" class="brand-logo">OVKSHOP</a>',
        '<a href="/login" class="brand-logo">OVKSHOP</a>',
        '<a href="/dashboard" class="brand-logo">OVK HAX</a>',
        '<a href="/products" class="brand-logo">OVK HAX</a>',
        '<a href="/login" class="brand-logo">OVK HAX</a>'
    ]
    for ol in old_logos:
        content = content.replace(ol, logo_replacement)
    
    # Strip any remaining "//" from headings and tags
    content = content.replace('OFFICIAL VIDEO GUIDES // OPERATIONS', 'OFFICIAL VIDEO GUIDES &bull; OPERATIONS')
    content = content.replace('OFFICIAL ARMORY // VERIFIED BUILDS', 'OFFICIAL ARMORY &bull; VERIFIED BUILDS')
    content = content.replace('PORTAL ACCESS // AUTHORIZATION', 'PORTAL ACCESS &bull; AUTHORIZATION')
    content = content.replace('NEW ENLISTMENT // ACCOUNT CREATION', 'NEW ENLISTMENT &bull; ACCOUNT CREATION')
    content = content.replace('ARMORY // ACTIVE BUILD', 'ARMORY &bull; ACTIVE BUILD')
    content = content.replace('// ALL BUILDS ONLINE', '&bull; ALL BUILDS ONLINE')
    content = content.replace(' // ', ' &bull; ')
    
    with open(tpath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Updated {tpath}')

# 2. Update style.css:
# - Add logo image rounded corners (.brand-logo-img)
# - Add vibrant amber neon glow to OVK HAX text
# - Add Google Fonts: Chakra Petch, Rajdhani, Orbitron, Plus Jakarta Sans, Outfit, Inter
# - Define font-picker classes
with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Replace font import with expanded choices
old_import = "@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,700;1,800&family=Outfit:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600;700;800&display=swap');"
new_import = "@import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600;700;800&family=Rajdhani:wght@600;700;800&family=Orbitron:wght@600;700;800;900&family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Outfit:wght@500;600;700;800;900&family=Inter:wght@500;600;700;800;900&display=swap');"

if old_import in css:
    css = css.replace(old_import, new_import)

# Brand logo styling with rounded image and glowing text
old_brand_logo = '''.brand-logo {
  font-family: var(--font-display);
  font-size: 1.85rem;
  letter-spacing: 1.5px;
  color: var(--primary-orange);
  text-transform: uppercase;
  display: flex;
  align-items: center;
  gap: 8px;
  text-shadow: 0 0 16px var(--primary-orange-glow);
}'''

new_brand_logo = '''.brand-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  cursor: pointer;
}

.brand-logo-img {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  object-fit: cover;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.6), 0 0 16px rgba(255, 154, 0, 0.35);
  border: 1.5px solid rgba(255, 154, 0, 0.5);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.brand-logo:hover .brand-logo-img {
  transform: scale(1.05);
  box-shadow: 0 6px 22px rgba(0, 0, 0, 0.7), 0 0 24px rgba(255, 154, 0, 0.65);
}

.brand-logo-text {
  font-family: var(--font-display);
  font-size: 1.75rem;
  font-weight: 900;
  letter-spacing: 1.5px;
  color: #ff9a00;
  text-transform: uppercase;
  text-shadow: 0 0 10px rgba(255, 154, 0, 0.8),
               0 0 22px rgba(255, 154, 0, 0.6),
               0 0 38px rgba(255, 154, 0, 0.4),
               0 2px 4px rgba(0, 0, 0, 0.9);
  transition: text-shadow 0.25s ease;
}

.brand-logo:hover .brand-logo-text {
  text-shadow: 0 0 14px rgba(255, 154, 0, 1),
               0 0 28px rgba(255, 154, 0, 0.85),
               0 0 46px rgba(255, 154, 0, 0.6),
               0 2px 4px rgba(0, 0, 0, 0.9);
}

/* Interactive Font Theme Classes */
body.font-jakarta {
  --font-display: 'Plus Jakarta Sans', sans-serif;
  --font-heading: 'Plus Jakarta Sans', sans-serif;
  --font-sans: 'Plus Jakarta Sans', sans-serif;
}

body.font-chakra {
  --font-display: 'Chakra Petch', sans-serif;
  --font-heading: 'Chakra Petch', sans-serif;
  --font-sans: 'Chakra Petch', sans-serif;
}

body.font-orbitron {
  --font-display: 'Orbitron', sans-serif;
  --font-heading: 'Plus Jakarta Sans', sans-serif;
  --font-sans: 'Plus Jakarta Sans', sans-serif;
}

body.font-rajdhani {
  --font-display: 'Rajdhani', sans-serif;
  --font-heading: 'Rajdhani', sans-serif;
  --font-sans: 'Rajdhani', sans-serif;
}

body.font-outfit {
  --font-display: 'Outfit', sans-serif;
  --font-heading: 'Outfit', sans-serif;
  --font-sans: 'Outfit', sans-serif;
}

body.font-inter {
  --font-display: 'Inter', sans-serif;
  --font-heading: 'Inter', sans-serif;
  --font-sans: 'Inter', sans-serif;
}

/* Font Selector Button in Header */
.font-selector-pill {
  background-color: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-full);
  padding: 6px 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--text-muted);
  cursor: pointer;
  transition: var(--transition);
  outline: none;
}

.font-selector-pill:hover {
  border-color: var(--primary-orange);
  color: #fff;
}

.font-picker-menu {
  position: absolute;
  top: 60px;
  right: 140px;
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.85);
  width: 210px;
  padding: 8px;
  display: none;
  z-index: 1000;
}

.font-picker-menu.show {
  display: block;
}

.font-picker-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.font-picker-item:hover {
  background: var(--bg-subtle);
  color: #ffffff;
}

.font-picker-item.active {
  color: var(--primary-orange);
  font-weight: 800;
  background: rgba(255, 154, 0, 0.08);
}'''

if old_brand_logo in css:
    css = css.replace(old_brand_logo, new_brand_logo)
else:
    # Append if not exact match
    css += '\n' + new_brand_logo

with open('static/css/style.css', 'w', encoding='utf-8') as f:
    f.write(css)
print('style.css updated with logo, glow, and font picker classes')

# 3. Update app.js:
# - Add interactive font switcher logic with localStorage persistence
# - Add font selector button to header
with open('static/js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Add font selector logic
font_logic = '''
// ==========================================
// INTERACTIVE FONT PICKER SYSTEM
// ==========================================
const AVAILABLE_FONTS = [
  { id: 'font-jakarta', name: 'Jakarta Sans', desc: 'Modern & Crisp' },
  { id: 'font-chakra', name: 'Chakra Petch', desc: 'Tech & Sci-Fi' },
  { id: 'font-orbitron', name: 'Orbitron', desc: 'Cyberpunk' },
  { id: 'font-rajdhani', name: 'Rajdhani', desc: 'Clean Tactical' },
  { id: 'font-outfit', name: 'Outfit', desc: 'Geometric' },
  { id: 'font-inter', name: 'Inter', desc: 'Ultra Clean' }
];

function applySavedFont() {
  const saved = localStorage.getItem('ovk_active_font') || 'font-jakarta';
  document.body.className = document.body.className.replace(/\\bfont-\\w+\\b/g, '').trim();
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
'''

if 'applySavedFont()' not in js:
    js += '\n' + font_logic

# Also remove live clock with '//' if present
js = js.replace('${monthName} ${year} // SYS TIME: ${timeStr} // ALL BUILDS ONLINE', '${monthName} ${year} &bull; SYS TIME: ${timeStr} &bull; ALL BUILDS ONLINE')

with open('static/js/app.js', 'w', encoding='utf-8') as f:
    f.write(js)
print('app.js updated with font switcher logic')
