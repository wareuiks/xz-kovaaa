with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

# 1. Update .brand-logo-img to remove glow and borders, just clean rounded corners
old_logo_css = '''.brand-logo-img {
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
}'''

new_logo_css = '''.brand-logo-img {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  object-fit: cover;
  border: none;
  box-shadow: none;
  display: block;
}

.brand-logo:hover .brand-logo-img {
  transform: scale(1.03);
}'''

if old_logo_css in css:
    css = css.replace(old_logo_css, new_logo_css)

# Ensure glow on OVK HAX text remains intense and vibrant
old_text_css = '''.brand-logo-text {
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
}'''

new_text_css = '''.brand-logo-text {
  font-family: var(--font-display);
  font-size: 1.75rem;
  font-weight: 900;
  letter-spacing: 1.5px;
  color: #ff9a00;
  text-transform: uppercase;
  text-shadow: 0 0 12px rgba(255, 154, 0, 0.9),
               0 0 24px rgba(255, 154, 0, 0.7),
               0 0 40px rgba(255, 154, 0, 0.5),
               0 2px 6px rgba(0, 0, 0, 0.9);
  transition: text-shadow 0.25s ease;
}'''

if old_text_css in css:
    css = css.replace(old_text_css, new_text_css)

with open('static/css/style.css', 'w', encoding='utf-8') as f:
    f.write(css)

print('style.css logo clean rounded corners and text glow updated')

# 2. Update app.js:
# - Remove "GAMES" on top of OVK Premium in loadFeaturedProducts
# - Change price to PHP 70.00
# - In loadCatalog, update price to PHP 70.00
with open('static/js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Remove <div class="featured-card-cat">${item.category || 'GAMES'}</div>
js = js.replace('<div class="featured-card-cat">${item.category || \'GAMES\'}</div>', '')

# Change PHP 70 to PHP 70.00 in featured cards
js = js.replace('STARTS ON</span> PHP 70</div>', 'STARTS ON</span> PHP 70.00</div>')
js = js.replace('STARTS ON</span> PHP ${Math.round(item.min_price || 70)}</div>', 'STARTS ON</span> PHP ${parseFloat(item.min_price || 70).toFixed(2)}</div>')

# In loadCatalog on products page
js = js.replace('<span style="font-size: 0.76rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; margin-right: 4px;">STARTS ON</span> PHP 70', '<span style="font-size: 0.76rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; margin-right: 4px;">STARTS ON</span> PHP 70.00')

with open('static/js/app.js', 'w', encoding='utf-8') as f:
    f.write(js)

print('app.js updated: GAMES removed from featured card and price set to PHP 70.00')
