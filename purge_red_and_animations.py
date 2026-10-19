import re

# 1. Update style.css:
# - Remove all @keyframes orangeButtonPulse, pulse-dot, pulseDot, and tilt card animations
# - Strip all red borders, red glows, and red text remnants
# - Remove .glow-btn animation
# - Change all red accents to clean amber or neutral slate borders

with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Remove glow button animation
css = css.replace('animation: orangeButtonPulse 2.5s infinite ease-in-out;', 'animation: none;')
css = re.sub(r'@keyframes orangeButtonPulse\s*\{[^}]*\}', '', css)

# Remove pulsing live stock dot animation
css = css.replace('animation: pulse-dot 1.8s infinite;', 'animation: none;')
css = re.sub(r'@keyframes pulse-dot\s*\{[^}]*\}', '', css)
css = css.replace('animation: pulseDot 2s infinite ease-in-out;', 'animation: none;')
css = re.sub(r'@keyframes pulseDot\s*\{[^}]*\}', '', css)

# Disable any 3D tilt perspective or transform animations on hover
css = css.replace('transform-style: preserve-3d;', '')
css = css.replace('perspective: 1000px;', '')
css = css.replace('will-change: transform;', '')

# Clean up any remaining red hex codes in style.css
css = css.replace('#ff2a44', 'var(--primary-orange)')
css = css.replace('#d9142e', '#e68a00')
css = css.replace('#d91430', '#e68a00')
css = css.replace('#ff455c', '#ffa826')
css = css.replace('#ff4760', '#ff9a00')
css = css.replace('#ff8a98', '#ffd494')
css = css.replace('rgba(255, 42, 68, 0.45)', 'rgba(255, 154, 0, 0.3)')
css = css.replace('rgba(255, 42, 68, 0.4)', 'rgba(255, 154, 0, 0.3)')
css = css.replace('rgba(255, 42, 68, 0.35)', 'rgba(255, 154, 0, 0.25)')
css = css.replace('rgba(255, 42, 68, 0.3)', 'rgba(255, 154, 0, 0.2)')
css = css.replace('rgba(255, 42, 68, 0.28)', 'rgba(255, 154, 0, 0.2)')
css = css.replace('rgba(255, 42, 68, 0.25)', 'rgba(255, 154, 0, 0.2)')
css = css.replace('rgba(255, 42, 68, 0.15)', 'rgba(255, 154, 0, 0.1)')
css = css.replace('rgba(255, 42, 68, 0.12)', 'rgba(255, 154, 0, 0.1)')
css = css.replace('rgba(255, 42, 68, 0.08)', 'rgba(255, 154, 0, 0.08)')
css = css.replace('rgba(255, 42, 68, 0.7)', 'rgba(255, 154, 0, 0.4)')
css = css.replace('rgba(255, 42, 68, 0.65)', 'rgba(255, 154, 0, 0.4)')
css = css.replace('rgba(255, 42, 68, 0.55)', 'rgba(255, 154, 0, 0.35)')

# Remove tactical dash kicker bar red outlines & red glow
css = css.replace(
'''.dash-kicker-bar {
  display: inline-block;
  width: 24px;
  height: 3px;
  background-color: var(--primary-red);
  box-shadow: 0 0 10px var(--primary-red-glow);
}''',
'''.dash-kicker-bar {
  display: inline-block;
  width: 20px;
  height: 3px;
  background-color: var(--primary-orange);
  border-radius: 2px;
}'''
)

# Product detail selected bar border (no red outline)
css = css.replace(
'''  background: #0d1017;
  border: 1px solid rgba(255, 42, 68, 0.4);''',
'''  background: #0d1017;
  border: 1px solid rgba(255, 154, 0, 0.3);'''
)

# Replace red buy buttons in product detail
css = css.replace(
'''.btn-purchase-action.ready {
  background: linear-gradient(135deg, #ff2a44, #d9142e);
  color: #ffffff;
  box-shadow: 0 4px 24px var(--primary-red-glow);
  border: 1px solid rgba(255, 255, 255, 0.2);
}''',
'''.btn-purchase-action.ready {
  background: linear-gradient(135deg, var(--primary-orange), var(--primary-orange-hover));
  color: #000000;
  font-weight: 800;
  border: none;
}'''
)

css = css.replace(
'''.btn-purchase-action.ready:hover {
  background: linear-gradient(135deg, #ff455c, #e01f37);
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(255, 42, 68, 0.7);
}''',
'''.btn-purchase-action.ready:hover {
  background: linear-gradient(135deg, #ffa826, #ea9200);
  transform: translateY(-1px);
}'''
)

with open('static/css/style.css', 'w', encoding='utf-8') as f:
    f.write(css)
print('style.css cleaned of red outlines and animations')

# 2. Update app.js:
# - Completely neuter initTilt3D so mousemove does NOT rotate or tilt cards
with open('static/js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

old_tilt = '''function initTilt3D() {
  const tiltElements = document.querySelectorAll('.tilt-card, [data-tilt], .product-card-horizontal, .wallet-card');
  
  tiltElements.forEach(card => {
    let bounds;
    
    function rotateToMouse(e) {
      const mouseX = e.clientX;
      const mouseY = e.clientY;
      const leftX = mouseX - bounds.x;
      const topY = mouseY - bounds.y;
      const center = {
        x: leftX - bounds.width / 2,
        y: topY - bounds.height / 2
      };
      
      const distance = Math.sqrt(center.x ** 2 + center.y ** 2);
      
      card.style.transform = `
        perspective(1000px)
        scale3d(1.025, 1.025, 1.025)
        rotate3d(
          ${-center.y / 100},
          ${center.x / 100},
          0,
          ${Math.log(distance) * 2.2}deg
        )
      `;
    }
    
    card.addEventListener('mouseenter', () => {
      bounds = card.getBoundingClientRect();
      document.addEventListener('mousemove', rotateToMouse);
    });
    
    card.addEventListener('mouseleave', () => {
      document.removeEventListener('mousemove', rotateToMouse);
      card.style.transform = 'perspective(1000px) scale3d(1, 1, 1) rotate3d(0, 0, 0, 0deg)';
    });
  });
}'''

new_tilt = '''function initTilt3D() {
  // Motion and tilting disabled per user request
  const tiltElements = document.querySelectorAll('.tilt-card, [data-tilt]');
  tiltElements.forEach(card => {
    card.style.transform = 'none';
  });
}'''

if old_tilt in js:
    js = js.replace(old_tilt, new_tilt)
    with open('static/js/app.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print('app.js tilt and wobble disabled')
else:
    print('Old tilt not found in app.js')

# 3. Clean up templates (tutorial.html, products.html, product_detail.html, login.html):
# - Remove dash-title-red -> use clean white or amber
# - Clean kicker text
templates = [
    'templates/tutorial.html',
    'templates/products.html',
    'templates/product_detail.html',
    'templates/dashboard.html',
    'templates/login.html'
]

for tpath in templates:
    try:
        with open(tpath, 'r', encoding='utf-8') as f:
            t = f.read()
        
        # Replace dash-title-red with dash-title-white
        t = t.replace('class="dash-title-red"', 'class="dash-title-white" style="color: var(--primary-orange);"')
        t = t.replace('dash-title-red', 'dash-title-white')
        t = t.replace('tilt-card', '')
        t = t.replace('data-tilt', '')
        t = t.replace('glow-btn', '')
        
        with open(tpath, 'w', encoding='utf-8') as f:
            f.write(t)
        print(f'{tpath} cleaned')
    except Exception as e:
        print(f'Error cleaning {tpath}: {e}')
