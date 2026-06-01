import logging
import os
from datetime import datetime
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
import re

load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Database initialization
DB_FILE = 'escrow_bot.db'

class EscrowBot:
    """Main Escrow Bot Class"""
    
    def __init__(self):
        self.init_database()
        self.OWNER_ID = int(os.getenv('OWNER_ID', '0'))
    
    def init_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS deals
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      deal_id TEXT UNIQUE,
                      creator_id INTEGER,
                      buyer_id INTEGER,
                      seller_id INTEGER,
                      original_amount REAL,
                      fees_percentage REAL,
                      fees_amount REAL,
                      final_amount REAL,
                      status TEXT,
                      created_at TIMESTAMP,
                      description TEXT,
                      confirmations TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (user_id INTEGER PRIMARY KEY,
                      username TEXT,
                      created_at TIMESTAMP)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS settings
                     (key TEXT PRIMARY KEY,
                      value TEXT)''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id, username):
        """Add user to database"""
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        try:
            c.execute('INSERT OR IGNORE INTO users VALUES (?, ?, ?)',
                     (user_id, username, datetime.now()))
            conn.commit()
        except Exception as e:
            logger.error(f"Error adding user: {e}")
        finally:
            conn.close()
    
    def create_deal_with_fees(self, creator_id, buyer_id, seller_id, original_amount, fees_percentage, description=""):
        """Create new escrow deal with fees calculation"""
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        deal_id = f"DEAL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Calculate fees
        fees_amount = (original_amount * fees_percentage) / 100
        final_amount = original_amount - fees_amount
        
        try:
            c.execute('''INSERT INTO deals 
                        (deal_id, creator_id, buyer_id, seller_id, original_amount, fees_percentage, fees_amount, final_amount, status, created_at, description, confirmations)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (deal_id, creator_id, buyer_id, seller_id, original_amount, fees_percentage, fees_amount, final_amount, 'pending', datetime.now(), description, '[]'))
            conn.commit()
            conn.close()
            return deal_id, final_amount, fees_amount
        except Exception as e:
            logger.error(f"Error creating deal: {e}")
            return None, None, None
    
    def create_deal(self, creator_id, buyer_id, seller_id, amount, description):
        """Create new escrow deal without fees"""
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        deal_id = f"DEAL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        try:
            c.execute('''INSERT INTO deals 
                        (deal_id, creator_id, buyer_id, seller_id, original_amount, fees_percentage, fees_amount, final_amount, status, created_at, description, confirmations)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (deal_id, creator_id, buyer_id, seller_id, amount, 0, 0, amount, 'pending', datetime.now(), description, '[]'))
            conn.commit()
            conn.close()
            return deal_id
        except Exception as e:
            logger.error(f"Error creating deal: {e}")
            return None
    
    def get_all_deals(self):
        """Get all deals from database"""
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('SELECT * FROM deals ORDER BY created_at DESC')
        deals = c.fetchall()
        conn.close()
        return deals
    
    def get_deal(self, deal_id):
        """Get specific deal"""
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('SELECT * FROM deals WHERE deal_id = ?', (deal_id,))
        deal = c.fetchone()
        conn.close()
        return deal
    
    def delete_deal(self, deal_id):
        """Delete a deal"""
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM deals WHERE deal_id = ?', (deal_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error deleting deal: {e}")
            return False

# Initialize bot
bot = EscrowBot()

# ============ COMMAND HANDLERS ============

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - Main menu"""
    user = update.effective_user
    bot.add_user(user.id, user.username or "Unknown")
    
    keyboard = [
        [InlineKeyboardButton("🤝 Create Deal", callback_data='create_deal')],
        [InlineKeyboardButton("📋 View All Deals", callback_data='view_deals')],
        [InlineKeyboardButton("👤 Your ID", callback_data='your_id')],
        [InlineKeyboardButton("📊 Statistics", callback_data='stats')],
        [InlineKeyboardButton("❓ Help", callback_data='help_btn')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f"""
╔════════════════════════════════════╗
║    🔐 TELEGRAM ESCROW BOT 🔐      ║
║                                    ║
║  Secure Transaction Management     ║
╚════════════════════════════════════╝

👋 Welcome {user.first_name}!

This bot helps you manage secure escrow transactions between buyers and sellers. All transactions are tracked and managed safely.

**Key Features:**
✅ Create secure deals
✅ Quick add with fees
✅ Track transactions
✅ View deal history

Ready to get started?
"""
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = """
📖 **HELP - All Commands**

🎯 **Main Commands:**
/start - Go to main menu
/help - Show this message
/id - Get your user ID

📊 **Deal Commands:**
/add <amount> <fees%> - Quick add deal with fees
   Example: /add 1000 5%
   (Amount: 1000, Fees: 5% = 50, Final: 950)

/createdeals - Create detailed deal
/deals - View all deals
/stats - Bot statistics

⚙️ **Owner Commands:**
/cleardeal - Clear all deals
/deletedeal <deal_id> - Delete specific deal

**How /add works:**
1. Send: /add 1000 5%
2. Bot creates deal automatically
3. Message gets deleted
4. Fees calculated: 1000 - (1000 × 5%) = 950
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def get_id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get user ID"""
    user = update.effective_user
    text = f"""
👤 **Your Information:**

ID: `{user.id}`
Name: {user.first_name} {user.last_name or ''}
Username: @{user.username or 'Not set'}

📋 **Use this ID when creating deals**
"""
    await update.message.reply_text(text, parse_mode='Markdown')

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show statistics"""
    deals = bot.get_all_deals()
    
    total_deals = len(deals)
    pending_deals = len([d for d in deals if d[9] == 'pending'])
    completed_deals = len([d for d in deals if d[9] == 'completed'])
    total_original = sum([d[5] for d in deals]) if deals else 0
    total_fees = sum([d[7] for d in deals]) if deals else 0
    total_final = sum([d[8] for d in deals]) if deals else 0
    
    stats_text = f"""
📊 **Bot Statistics:**

Total Deals: {total_deals}
Pending: {pending_deals}
Completed: {completed_deals}

💰 **Financial:**
Total Original: ${total_original:,.2f}
Total Fees: ${total_fees:,.2f}
Total Final: ${total_final:,.2f}

🔐 All transactions tracked securely
"""
    await update.message.reply_text(stats_text, parse_mode='Markdown')

# ============ ADD COMMAND - NEW FEATURE ============

async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quick add deal with fees - /add <amount> <fees%>"""
    user = update.effective_user
    bot.add_user(user.id, user.username or "Unknown")
    
    if len(context.args) != 2:
        await update.message.reply_text(
            "❌ Invalid format!\n\n"
            "Usage: /add <amount> <fees%>\n"
            "Example: /add 1000 5%\n\n"
            "This will create a deal with:\n"
            "Amount: 1000\n"
            "Fees: 5% (50)\n"
            "Final: 950"
        )
        return
    
    try:
        amount_str = context.args[0]
        fees_str = context.args[1]
        
        # Parse amount
        amount = float(amount_str)
        
        # Parse fees (remove % if present)
        fees_str = fees_str.replace('%', '')
        fees_percentage = float(fees_str)
        
        if amount <= 0 or fees_percentage < 0:
            await update.message.reply_text("❌ Amount and fees must be positive numbers!")
            return
        
        if fees_percentage > 100:
            await update.message.reply_text("❌ Fees cannot exceed 100%!")
            return
        
        # Create deal
        buyer_id = user.id
        seller_id = bot.OWNER_ID
        description = f"Quick deal created with /add command"
        
        deal_id, final_amount, fees_amount = bot.create_deal_with_fees(
            user.id, buyer_id, seller_id, amount, fees_percentage, description
        )
        
        if deal_id:
            # Send success message
            success_text = f"""
✅ **Deal Created Successfully!**

📌 Deal ID: `{deal_id}`
💰 Original Amount: ${amount:,.2f}
📊 Fees: {fees_percentage}% (${fees_amount:,.2f})
💵 Final Amount: ${final_amount:,.2f}
📅 Status: PENDING

Deal has been added to the system!
"""
            msg = await update.message.reply_text(success_text, parse_mode='Markdown')
            
            # Delete the command message
            try:
                await update.message.delete()
            except Exception as e:
                logger.error(f"Could not delete message: {e}")
        else:
            await update.message.reply_text("❌ Error creating deal. Try again.")
    
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid input!\n\n"
            "Please use:\n"
            "/add <amount> <fees%>\n"
            "Example: /add 1000 5%"
        )

# ============ BUTTON CALLBACKS ============

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button presses"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'create_deal':
        await query.edit_message_text(
            text="🤝 **Create New Deal**\n\nSend buyer ID (Telegram ID of buyer):",
            parse_mode='Markdown'
        )
        context.user_data['creating_deal'] = True
        context.user_data['deal_step'] = 'buyer'
    
    elif query.data == 'view_deals':
        deals = bot.get_all_deals()
        if not deals:
            await query.edit_message_text(text="❌ No deals found yet.")
            return
        
        deals_text = "💼 **All Active Deals:**\n\n"
        for deal in deals[:10]:  # Show last 10
            deals_text += f"""
📌 **Deal ID:** {deal[1]}
👤 Creator: {deal[2]}
Buyer: {deal[3]} | Seller: {deal[4]}
💰 Original: ${deal[5]:,.2f}
📊 Fees: {deal[6]}% (${deal[7]:,.2f})
💵 Final: ${deal[8]:,.2f}
Status: {deal[9].upper()}
─────────────"""
        
        await query.edit_message_text(text=deals_text, parse_mode='Markdown')
    
    elif query.data == 'your_id':
        user = query.from_user
        await query.edit_message_text(
            text=f"👤 **Your ID:** `{user.id}`\n\nName: {user.first_name}\nUsername: @{user.username or 'Not set'}"
        )
    
    elif query.data == 'stats':
        deals = bot.get_all_deals()
        total = len(deals)
        pending = len([d for d in deals if d[9] == 'pending'])
        completed = len([d for d in deals if d[9] == 'completed'])
        total_fees = sum([d[7] for d in deals]) if deals else 0
        
        stats_text = f"""
📊 **Statistics:**

Total Deals: {total}
Pending: {pending}
Completed: {completed}
Total Fees Collected: ${total_fees:,.2f}
"""
        await query.edit_message_text(text=stats_text, parse_mode='Markdown')
    
    elif query.data == 'help_btn':
        await query.edit_message_text(
            text="/help - Use this command for all available options"
        )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages during deal creation"""
    if context.user_data.get('creating_deal'):
        text = update.message.text
        
        if context.user_data.get('deal_step') == 'buyer':
            try:
                buyer_id = int(text)
                context.user_data['buyer_id'] = buyer_id
                context.user_data['deal_step'] = 'seller'
                await update.message.reply_text("✅ Buyer ID saved!\n\nNow send seller ID:")
            except ValueError:
                await update.message.reply_text("❌ Invalid ID. Please send a numeric ID.")
        
        elif context.user_data.get('deal_step') == 'seller':
            try:
                seller_id = int(text)
                context.user_data['seller_id'] = seller_id
                context.user_data['deal_step'] = 'amount'
                await update.message.reply_text("✅ Seller ID saved!\n\nNow send amount (e.g., 1000):")
            except ValueError:
                await update.message.reply_text("❌ Invalid ID. Please send a numeric ID.")
        
        elif context.user_data.get('deal_step') == 'amount':
            try:
                amount = float(text)
                context.user_data['amount'] = amount
                context.user_data['deal_step'] = 'fees'
                await update.message.reply_text("✅ Amount saved!\n\nNow send fees percentage (e.g., 5 for 5%):")
            except ValueError:
                await update.message.reply_text("❌ Invalid amount. Please send a number.")
        
        elif context.user_data.get('deal_step') == 'fees':
            try:
                fees = float(text.replace('%', ''))
                context.user_data['fees'] = fees
                context.user_data['deal_step'] = 'description'
                await update.message.reply_text("✅ Fees saved!\n\nNow describe the deal (optional, or type 'skip'):")
            except ValueError:
                await update.message.reply_text("❌ Invalid fees. Please send a number.")
        
        elif context.user_data.get('deal_step') == 'description':
            description = text if text.lower() != 'skip' else ''
            
            # Create the deal
            buyer_id = context.user_data['buyer_id']
            seller_id = context.user_data['seller_id']
            amount = context.user_data['amount']
            fees = context.user_data['fees']
            creator_id = update.effective_user.id
            
            deal_id, final_amount, fees_amount = bot.create_deal_with_fees(
                creator_id, buyer_id, seller_id, amount, fees, description
            )
            
            if deal_id:
                success_text = f"""
✅ **Deal Created Successfully!**

📌 Deal ID: `{deal_id}`
👤 Buyer: {buyer_id}
👤 Seller: {seller_id}
💰 Original Amount: ${amount:,.2f}
📊 Fees: {fees}% (${fees_amount:,.2f})
💵 Final Amount: ${final_amount:,.2f}
📝 Description: {description or 'N/A'}
📅 Status: PENDING

Both parties must confirm this deal!
"""
                await update.message.reply_text(success_text, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Error creating deal. Try again.")
            
            # Reset
            context.user_data['creating_deal'] = False
            context.user_data['deal_step'] = None

async def owner_clear_deals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear all deals (owner only)"""
    if update.effective_user.id != bot.OWNER_ID:
        await update.message.reply_text("❌ Permission denied!")
        return
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM deals')
    conn.commit()
    conn.close()
    
    await update.message.reply_text("✅ All deals cleared!")

async def owner_delete_deal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete specific deal (owner only)"""
    if update.effective_user.id != bot.OWNER_ID:
        await update.message.reply_text("❌ Permission denied!")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /deletedeal <deal_id>")
        return
    
    deal_id = context.args[0]
    if bot.delete_deal(deal_id):
        await update.message.reply_text(f"✅ Deal {deal_id} deleted!")
    else:
        await update.message.reply_text("❌ Deal not found!")

def main():
    """Start the bot"""
    token = os.getenv('BOT_TOKEN')
    if not token:
        print("❌ BOT_TOKEN not found! Set it in .env file")
        return
    
    # Create app
    app = Application.builder().token(token).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("id", get_id_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("add", add_command))
    app.add_handler(CommandHandler("cleardeal", owner_clear_deals))
    app.add_handler(CommandHandler("deletedeal", owner_delete_deal))
    
    # Add callback handler
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Add text message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("🤖 Bot started! Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == '__main__':
    main()