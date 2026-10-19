import sqlite3, os, re

# 1. Update shop.db product description away from AI-speak to real gamer description
conn = sqlite3.connect('shop.db')
c = conn.cursor()
c.execute("""
    UPDATE catalog_items 
    SET description = 'Undetected CODM aimbot, wallhack & ESP. Instant key delivery right after payment.'
    WHERE id = 1
""")
conn.commit()
conn.close()
print("Updated database catalog_items description")

# Also update database.py so future boots keep the real gamer description
with open('database.py', 'r', encoding='utf-8') as f:
    db_py = f.read()

db_py = db_py.replace(
    "'Premium undetected memory enhancement and ESP overlay with automated loader.'",
    "'Undetected CODM aimbot, wallhack & ESP. Instant key delivery right after payment.'"
)
with open('database.py', 'w', encoding='utf-8') as f:
    f.write(db_py)
print("database.py updated")

# 2. Update dashboard.html:
# - Remove withdraw button completely (make deposit full width)
# - Add Support & Help Modal matching reference screenshot (with accordion & bottom help card)
with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    d = f.read()

old_wallet_btn_row = '''        <div class="cid-wallet-btn-row">
          <button class="btn cid-btn-deposit" onclick="openDepositModal()">
            <i class="fa-solid fa-arrow-down"></i> Deposit
          </button>
          <button class="btn cid-btn-withdraw" onclick="openWithdrawModal()">
            <i class="fa-solid fa-arrow-up"></i> Withdraw
          </button>
        </div>'''

new_wallet_btn_row = '''        <div class="cid-wallet-btn-row" style="grid-template-columns: 1fr;">
          <button class="btn cid-btn-deposit" onclick="openDepositModal()" style="width: 100%; font-size: 1rem; padding: 14px 20px;">
            <i class="fa-solid fa-arrow-down"></i> Deposit
          </button>
        </div>'''

if old_wallet_btn_row in d:
    d = d.replace(old_wallet_btn_row, new_wallet_btn_row)
else:
    # If already modified, replace any remaining cid-btn-withdraw
    d = re.sub(r'<button class="btn cid-btn-withdraw"[^>]*>.*?</button>', '', d, flags=re.DOTALL)
    d = d.replace('<div class="cid-wallet-btn-row">', '<div class="cid-wallet-btn-row" style="grid-template-columns: 1fr;">')

# Support & Help Modal Template (Matching Screenshot exactly, excluding referral & withdraw earnings)
support_modal_html = '''
  <!-- ========================================== -->
  <!-- MODAL: SUPPORT & HELP (Reference Design) -->
  <!-- ========================================== -->
  <div class="modal-overlay" id="support-modal">
    <div class="modal-box support-modal-box">
      <button class="modal-close-btn" onclick="closeSupportModal()">&times;</button>
      
      <div class="support-modal-header">
        <h2 class="support-main-title">Support &amp; Help</h2>
        <p class="support-main-subtext">Get help with orders, keys, or account issues.</p>
      </div>

      <div class="support-faq-list">
        <!-- 1. License key delivery -->
        <div class="support-faq-item open" onclick="toggleFaqItem(this)">
          <div class="faq-item-head">
            <div class="faq-head-left">
              <div class="faq-icon-box icon-purple">
                <i class="fa-solid fa-key"></i>
              </div>
              <div>
                <div class="faq-question">How do I receive my license key?</div>
                <div class="faq-hint">Instant delivery after purchase</div>
              </div>
            </div>
            <div class="faq-chevron"><i class="fa-solid fa-chevron-down"></i></div>
          </div>
          <div class="faq-item-body">
            After a successful purchase, your license key is immediately visible in <strong>My Orders</strong> on your dashboard. You can copy it directly from there. Keys are never sent by email — always check your Orders section.
          </div>
        </div>

        <!-- 2. Deposit time -->
        <div class="support-faq-item" onclick="toggleFaqItem(this)">
          <div class="faq-item-head">
            <div class="faq-head-left">
              <div class="faq-icon-box icon-green">
                <i class="fa-solid fa-wallet"></i>
              </div>
              <div>
                <div class="faq-question">How long does a deposit take?</div>
                <div class="faq-hint">Deposit processing time</div>
              </div>
            </div>
            <div class="faq-chevron"><i class="fa-solid fa-chevron-down"></i></div>
          </div>
          <div class="faq-item-body">
            Deposits via PayMongo (GCash, Maya, and Card) are fully automated and credited within seconds. If you ever have a pending transaction, refresh your balance or contact admin with your receipt.
          </div>
        </div>

        <!-- 3. Refund policy -->
        <div class="support-faq-item" onclick="toggleFaqItem(this)">
          <div class="faq-item-head">
            <div class="faq-head-left">
              <div class="faq-icon-box icon-red">
                <i class="fa-solid fa-rotate-left"></i>
              </div>
              <div>
                <div class="faq-question">Can I get a refund?</div>
                <div class="faq-hint">Refund policy</div>
              </div>
            </div>
            <div class="faq-chevron"><i class="fa-solid fa-chevron-down"></i></div>
          </div>
          <div class="faq-item-body">
            Due to the digital nature of instant license keys, all sales are final once the key is generated and revealed. Please ensure you are purchasing the right tier for your device before confirming.
          </div>
        </div>

        <!-- 4. Payment Security -->
        <div class="support-faq-item" onclick="toggleFaqItem(this)">
          <div class="faq-item-head">
            <div class="faq-head-left">
              <div class="faq-icon-box icon-amber">
                <i class="fa-solid fa-shield-halved"></i>
              </div>
              <div>
                <div class="faq-question">Is my payment secure?</div>
                <div class="faq-hint">Security &amp; privacy</div>
              </div>
            </div>
            <div class="faq-chevron"><i class="fa-solid fa-chevron-down"></i></div>
          </div>
          <div class="faq-item-body">
            Yes! All payment channels are processed directly through PayMongo encrypted gateways. We never see or store your payment passwords or PIN numbers.
          </div>
        </div>
      </div>

      <!-- Still need help bottom box -->
      <div class="support-bottom-card">
        <div class="support-agent-icon">
          <i class="fa-solid fa-headset"></i>
        </div>
        <h3 class="support-bottom-title">Still need help?</h3>
        <p class="support-bottom-sub">Our support team is available to assist you. Reach out through any channel below.</p>
        <div class="support-action-buttons">
          <a href="https://t.me/kovalucy" target="_blank" class="btn-support-channel btn-tg">
            <i class="fa-brands fa-telegram"></i> Telegram
          </a>
          <a href="https://t.me/ovkfiles" target="_blank" class="btn-support-channel btn-files">
            <i class="fa-solid fa-folder-open"></i> OVK Files
          </a>
        </div>
      </div>
    </div>
  </div>
'''

if 'id="support-modal"' not in d:
    d = d.replace('</body>', support_modal_html + '\n</body>')

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(d)
print("Updated templates/dashboard.html with withdraw removed & support modal added")

# Also add Support Modal to products.html, product_detail.html, and tutorial.html
other_templates = ['templates/products.html', 'templates/product_detail.html', 'templates/tutorial.html']
for tpath in other_templates:
    if os.path.exists(tpath):
        with open(tpath, 'r', encoding='utf-8') as f:
            tc = f.read()
        if 'id="support-modal"' not in tc:
            tc = tc.replace('</body>', support_modal_html + '\n</body>')
            with open(tpath, 'w', encoding='utf-8') as f:
                f.write(tc)
            print(f"Added support modal to {tpath}")
