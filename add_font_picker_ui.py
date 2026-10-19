import os

templates = [
    'templates/dashboard.html',
    'templates/products.html',
    'templates/product_detail.html',
    'templates/tutorial.html'
]

font_picker_header_html = '''        <!-- Interactive Font Picker -->
        <button class="font-selector-pill" id="font-picker-btn" onclick="toggleFontPicker(event)" title="Change Theme Font">
          <i class="fa-solid fa-font"></i>
          <span>Font</span>
        </button>

        <div class="font-picker-menu" id="font-picker-dropdown">
          <div style="font-size: 0.72rem; font-weight: 800; color: var(--text-dark); text-transform: uppercase; letter-spacing: 0.8px; padding: 4px 8px 8px; border-bottom: 1px solid var(--border-card); margin-bottom: 6px;">
            Choose Typography
          </div>
          <div id="font-picker-list"></div>
        </div>'''

for tpath in templates:
    if not os.path.exists(tpath): continue
    with open(tpath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Insert font picker button right before coin-pill
    target = '<div class="coin-pill"'
    if target in content and 'font-selector-pill' not in content:
        content = content.replace(target, font_picker_header_html + '\n        ' + target)
        with open(tpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Added font picker to {tpath}')
    else:
        print(f'Skipped or already present in {tpath}')
