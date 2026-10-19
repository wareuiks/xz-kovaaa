# ⚡ OVK DIGITAL SHOP & PAYMONGO PAYMENT GATEWAY

A complete, high-performance digital license store and wallet system built with **Python (Flask)**, **SQLite**, and direct **PayMongo API integration** (supporting **GCash**, **Maya**, **GrabPay**, and **Credit/Debit Cards**).

---

## 💎 Configured Price List

| Tier | Duration | Price (PHP) | Badge |
|---|---|---|---|
| **Tier 1** | 3 DAYS | **₱70.00** | Trial Tier |
| **Tier 2** | 7 DAYS | **₱100.00** | Popular |
| **Tier 3** | 14 DAYS | **₱200.00** | Great Value |
| **Tier 4** | 30 DAYS | **₱300.00** | Best Seller |
| **Tier 5** | 60 DAYS | **₱450.00** | Pro Choice |
| **Tier 6** | LIFETIME | **₱700.00** | Ultimate Value |

---

## 🚀 Quick Start (Running Locally)

### 1. Start the Server
Open PowerShell in this directory:
```powershell
& 'C:\Users\Lorenz\AppData\Local\Python\bin\python.exe' app.py
```
Or if Python is in your PATH:
```bash
python app.py
```

Open your browser at: **[http://localhost:5000](http://localhost:5000)**

---

## 🔑 Master Admin Account

| Account | Username | Password | Role |
|---|---|---|---|
| **Administrator** | `admin` | `admin123` | Master Admin (`/admin`) |

*Customers create their own accounts via the Register tab.*

## 🇵🇭 Connecting Your Real PayMongo Account

### Step 1: Get Your API Keys
1. Go to [https://dashboard.paymongo.com](https://dashboard.paymongo.com).
2. Toggle to **Test Mode** (top-right or settings).
3. Navigate to **Developers > API Keys**:
   - Copy your `Secret Key` (`sk_test_...` or `sk_live_...`).
   - Copy your `Public Key` (`pk_test_...` or `pk_live_...`).

### Step 2: Update Your `.env` File
Open `.env` in this project folder and paste your keys:
```env
PAYMONGO_SECRET_KEY=sk_test_your_real_key_here
PAYMONGO_PUBLIC_KEY=pk_test_your_real_key_here
PAYMONGO_WEBHOOK_SECRET=whsec_your_webhook_secret_here
APP_URL=http://localhost:5000
PORT=5000
```

---

## 🔗 Setting Up PayMongo Webhooks (Automatic Crediting)

When a customer pays with GCash or Maya, PayMongo notifies your server via a **Webhook** to instantly add the money to their wallet.

### For Local Testing (Using ngrok):
1. In a terminal, run:
   ```bash
   ngrok http 5000
   ```
2. Copy your public forwarding URL (e.g. `https://xxxx-xx-xx.ngrok-free.app`).
3. In your **PayMongo Dashboard > Developers > Webhooks**:
   - Click **Add Webhook Endpoint**.
   - URL: `https://xxxx-xx-xx.ngrok-free.app/api/webhooks/paymongo`
   - Select Event: `checkout_session.payment.paid`
   - Save and copy the **Webhook Signing Secret** (`whsec_...`) into `.env`.
4. Update `APP_URL` in `.env` to your ngrok URL.

### Sandbox Simulator (Zero Configuration Needed):
Inside the "Add Funds" modal, you can also click **⚡ Instant Top-Up (Sandbox Sim)** to instantly test wallet balance crediting and purchasing without waiting for PayMongo live verification!

---

## 🛡️ Admin Features (`/admin`)
Log in with `admin` / `admin123` to access `/admin`:
- **Bulk Key Importer:** Paste batches of license keys (1 per line) for any duration tier.
- **Manual Balance Adjuster:** Add or deduct funds to any customer's account.
- **Revenue & Orders Overview:** Real-time stats on orders and sales.
