# 🔐 Telegram Escrow Bot

> A professional Telegram bot for managing secure escrow transactions between buyers and sellers with advanced fee management.

## ✨ Features

- 🤝 **Create Deals** - Manage transactions with buyer & seller
- ⚡ **Quick Add** - `/add amount fees%` for instant deal creation
- 📋 **Track Deals** - View all active and completed deals with detailed breakdowns
- 💰 **Secure** - SQLite database with encrypted data
- 🎯 **Easy to Use** - Simple buttons and commands
- 👥 **Multi-user** - Support for multiple users
- ⚙️ **Owner Controls** - Admin commands for management

## 🎮 Commands

```
/start          → Show main menu
/help           → Show all commands
/id             → Get your Telegram ID
/add <amt> <%>  → Quick add deal with fees
                   Example: /add 1000 5%
                   (Creates deal: 1000 - 50 = 950)

/createdeals    → Create detailed deal
/deals          → View all deals
/stats          → View bot statistics

Owner Only:
/cleardeal      → Clear all deals
/deletedeal     → Delete specific deal
```

## ⚡ Quick Add Feature

### How it works:

```
/add 1000 5%

📌 Original Amount: $1000.00
📊 Fees: 5% = $50.00
💵 Final Amount: $950.00
```

**Steps:**
1. Send: `/add <amount> <fees%>`
2. Bot creates deal automatically
3. Command message gets deleted
4. Deal saved to database
5. Fees automatically calculated and deducted

**Examples:**
```
/add 500 2%     → $500 - $10 = $490
/add 2000 10%   → $2000 - $200 = $1800
/add 100 5%     → $100 - $5 = $95
```

## 🚀 Quick Start

### Step 1: Create Bot on Telegram

1. Open [@BotFather](https://t.me/botfather)
2. Send `/newbot`
3. Choose a name & username
4. Copy the **BOT_TOKEN**

### Step 2: Clone Repository

```bash
git clone https://github.com/Winy1234/telegram-escrow-bot.git
cd telegram-escrow-bot
```

### Step 3: Setup Environment

```bash
# Create .env file
cp .env.example .env

# Edit .env and add your BOT_TOKEN
nano .env
```

### Step 4: Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run bot
python main.py
```

## 🌐 Deploy on Render

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Add escrow bot with /add feature"
git push
```

### Step 2: Create Render Service

1. Go to [render.com](https://render.com)
2. Sign in with GitHub
3. Click **"New +"** → **"Web Service"**
4. Select your repository
5. Configure:
   - **Name:** `telegram-escrow-bot`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`

### Step 3: Add Environment Variables

- Key: `BOT_TOKEN`
- Value: Your token from BotFather

### Step 4: Deploy

Click **"Create Web Service"** and wait ~2 minutes for deployment ✅

## 📊 Database Schema

### deals table
```
- id (auto increment)
- deal_id (unique)
- creator_id
- buyer_id
- seller_id
- original_amount (before fees)
- fees_percentage
- fees_amount (calculated)
- final_amount (original - fees)
- status (pending/completed/cancelled)
- created_at
- description
- confirmations
```

### users table
```
- user_id (primary)
- username
- created_at
```

### settings table
```
- key
- value
```

## 🔧 Configuration

Edit `main.py` to customize:

```python
self.OWNER_ID = 7967147174  # Change to your ID
```

## 📝 How It Works

### Using /add command:
1. **Send:** `/add 1000 5%`
2. **Bot calculates:** 1000 - (1000 × 5%) = 950
3. **Creates deal** with amount 950
4. **Deletes command** message
5. **Saves to database** with all details

### Using /createdeals:
1. Send buyer ID
2. Send seller ID
3. Send amount
4. Send fees percentage
5. Send description
6. Deal created with detailed info

## ⚠️ Important Notes

- Bot token should be kept secret
- Never commit `.env` file to GitHub
- Use `.env.example` as template
- Owner ID: 7967147174
- Owner: @underlimitz
- Fees are automatically deducted from original amount

## 🐛 Troubleshooting

**Bot not responding?**
- Check if `BOT_TOKEN` is correct
- Verify internet connection
- Check bot logs

**Database errors?**
- Delete `escrow_bot.db` and restart
- Check write permissions

**Render deployment issues?**
- Check build logs
- Verify environment variables
- Check `requirements.txt` syntax

**Command not working?**
- Make sure you're using correct format: `/add 1000 5%`
- Amount must be a number
- Fees must be between 0-100

## 📞 Support

- **Owner:** @underlimitz
- **Owner ID:** 7967147174
- **Repo:** Winy1234/telegram-escrow-bot

## 📜 License

MIT License - Free to use and modify

---

**Made with ❤️ for secure transactions**

> Last Updated: 2026-06-01
> Version: 2.0 (with /add feature)