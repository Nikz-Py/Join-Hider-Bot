#!/usr/bin/env python3
"""
Telegram Join/Leave Message Hider Bot
Main Flask application with webhook handling
"""

import os
import logging
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config import Config
from bot_handlers import BotHandlers
from storage import Storage

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize storage
storage = Storage()

# Initialize bot handlers
bot_handlers = BotHandlers(storage)

# Initialize Telegram bot application
bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
if not bot_token:
    logger.error("TELEGRAM_BOT_TOKEN environment variable is required")
    exit(1)

application = Application.builder().token(bot_token).build()

# Add handlers
application.add_handler(CommandHandler("start", bot_handlers.start_command))
application.add_handler(MessageHandler(
    filters.StatusUpdate.NEW_CHAT_MEMBERS | filters.StatusUpdate.LEFT_CHAT_MEMBER,
    bot_handlers.handle_join_leave
))

@app.route('/')
def index():
    """Basic health check endpoint"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Telegram Join/Leave Hider Bot</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 600px; margin: 0 auto; }
            .status { color: green; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Telegram Join/Leave Hider Bot</h1>
            <p class="status">✅ Bot is running and ready!</p>
            <p>This bot automatically hides join/leave messages in Telegram groups.</p>
            <h3>Features:</h3>
            <ul>
                <li>Automatically delete join/leave notifications</li>
                <li>Works immediately once given admin permissions</li>
                <li>No configuration required</li>
                <li>Simple and reliable operation</li>
            </ul>
            <h3>Commands:</h3>
            <ul>
                <li><code>/start</code> - Welcome message and setup info</li>
            </ul>
        </div>
    </body>
    </html>
    """

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook updates from Telegram"""
    try:
        update_data = request.get_json()
        if update_data:
            update = Update.de_json(update_data, application.bot)
            application.update_queue.put_nowait(update)
        return jsonify({"status": "ok"})
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return {"status": "healthy", "bot": "running"}

def setup_webhook():
    """Set up webhook URL if WEBHOOK_URL is provided"""
    webhook_url = os.getenv('WEBHOOK_URL')
    if webhook_url:
        try:
            import asyncio
            asyncio.run(application.bot.set_webhook(f"{webhook_url}/webhook"))
            logger.info(f"Webhook set to: {webhook_url}/webhook")
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")

if __name__ == '__main__':
    import asyncio
    import threading
    
    # Initialize the bot application
    asyncio.run(application.initialize())
    
    # Set up webhook if URL is provided, otherwise use polling
    webhook_url = os.getenv('WEBHOOK_URL')
    
    if webhook_url:
        setup_webhook()
        # Run Flask app for webhook mode
        port = int(os.getenv('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        # Run both Flask and bot in polling mode
        logger.info("Starting bot in polling mode with web interface...")
        
        def run_bot():
            """Run bot in a separate thread"""
            try:
                # Create new event loop for this thread
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Run polling without signal handlers (background thread limitation)
                application.run_polling(drop_pending_updates=True, close_loop=False, stop_signals=None)
            except Exception as e:
                logger.error(f"Bot polling error: {e}")
        
        # Start bot in background thread
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        
        # Give bot time to start
        import time
        time.sleep(2)
        logger.info("Bot started in background, Flask starting on port 5000...")
        
        # Run Flask app on main thread
        port = int(os.getenv('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=False)
