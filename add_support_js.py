with open('static/js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

support_js = '''
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
'''

if 'function openSupportModal()' not in js:
    js += '\n' + support_js
    with open('static/js/app.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("Support modal functions appended to app.js")
else:
    print("openSupportModal already present in app.js")
