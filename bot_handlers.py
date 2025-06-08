"""
Telegram bot handlers for commands, callbacks, and message processing
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatType
from storage import Storage
from config import Config

logger = logging.getLogger(__name__)

class BotHandlers:
    def __init__(self, storage: Storage):
        self.storage = storage
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        chat = update.effective_chat
        user = update.effective_user
        
        if chat.type == ChatType.PRIVATE:
            welcome_text = (
                "Join/Leave Message Hider Bot\n\n"
                "Hello! I Help Keep Your Group Chats Clean By Automatically Hiding "
                "Join And Leave Messages.\n\n"
                "**How To Use:**\n"
                "1. Add Me To Your Group Chat\n"
                "2. Make Me An Admin With 'Delete Messages' Permission\n"
                "3. I'll Automatically Start Hiding Join/leave Messages\n\n"
                "𝘛𝘩𝘢𝘵'𝘴 𝘐𝘵! 𝘕𝘰 𝘊𝘰𝘯𝘧𝘪𝘨𝘶𝘳𝘢𝘵𝘪𝘰𝘯 𝘕𝘦𝘦𝘥𝘦𝘥 - 𝘐 𝘞𝘰𝘳𝘬 𝘈𝘶𝘵𝘰𝘮𝘢𝘵𝘪𝘤𝘢𝘭𝘭𝘺 𝘖𝘯𝘤𝘦 𝘠𝘰𝘶 𝘎𝘪𝘷𝘦 𝘔𝘦 𝘈𝘥𝘮𝘪𝘯 𝘗𝘦𝘳𝘮𝘪𝘴𝘴𝘪𝘰𝘯𝘴.  "
            )
            
            # Get bot username for the inline button
            bot_info = await context.bot.get_me()
            bot_username = bot_info.username
            
            # Create inline keyboard with "Add to Group" button
            keyboard = [
                [InlineKeyboardButton(
                    '➕ 𝗔𝗱𝗱 𝗠𝗲 𝗧𝗼 𝗬𝗼𝘂𝗿 𝗚𝗿𝗼𝘂𝗽𝘀 ➕', 
                    url=f'https://t.me/{bot_username}?startgroup=true'
                )]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                welcome_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            # In group chat
            welcome_text = (
                "**Join/Leave Message Hider Bot is now active!**\n\n"
                "I will automatically hide join/leave messages to keep your chat clean.\n\n"
                "Make sure I have admin permissions with 'Delete Messages' enabled."
            )
            
            await update.message.reply_text(
                welcome_text,
                parse_mode='Markdown'
            )
    

    
    async def handle_join_leave(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle join/leave messages"""
        message = update.message
        chat = message.chat
        
        # Only process group messages
        if chat.type == ChatType.PRIVATE:
            return
        
        # Check if the bot itself was added to the group
        if message.new_chat_members:
            bot_info = await context.bot.get_me()
            for new_member in message.new_chat_members:
                if new_member.id == bot_info.id:
                    # Bot was added to the group, send welcome message
                    invite_message = (
                        "**🎊 Thank You** For **Adding** Me To **Your Group!**\n\n "
                        "Join/Leave Message Hider Bot is now active!**\n\n"
                        "I Will Automatically Hide Join And Leave Messages To Keep Your Chat Clean.\n\n"
                        "**To Get Started:**\n"
                        "1. Make Me An Admin With 'Delete Messages' Permission\n"
                        "2. That's it! I'll Automatically Start Hiding Join/Leave Notifications\n\n"
                    )
                    
                    # Create inline keyboard with support group button (if configured)
                    keyboard = []
                    if Config.SUPPORT_GROUP_URL:
                        keyboard.append([InlineKeyboardButton(
                            '💬 Support Group', 
                            url=Config.SUPPORT_GROUP_URL
                        )])
                    
                    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
                    
                    try:
                        await context.bot.send_message(
                            chat.id,
                            invite_message,
                            parse_mode='Markdown',
                            reply_markup=reply_markup
                        )
                        logger.info(f"Sent welcome message to new group {chat.id} ({chat.title})")
                    except Exception as e:
                        logger.error(f"Failed to send welcome message to chat {chat.id}: {e}")
                    
                    # Don't delete the bot's own join message yet, let it be visible briefly
                    return
        
        # Always try to delete join/leave messages (bot is always enabled now)
        # Check if this is a join/leave message
        if message.new_chat_members or message.left_chat_member:
            try:
                # Delete the join/leave message
                await message.delete()
                logger.info(f"Deleted join/leave message in chat {chat.id} ({chat.title})")
            except Exception as e:
                logger.error(f"Failed to delete message in chat {chat.id}: {e}")
                # If we can't delete messages, we might not have the right permissions
                if "not enough rights" in str(e).lower() or "insufficient rights" in str(e).lower():
                    # Try to send a warning to admins
                    try:
                        await context.bot.send_message(
                            chat.id,
                            "⚠️ **Permission Error**\n\n"
                            "I need admin privileges with 'Delete Messages' permission "
                            "to hide join/leave messages.\n\n"
                            "Please make me an admin with the required permissions.",
                            parse_mode='Markdown'
                        )
                    except:
                        pass  # If we can't even send messages, just log it
                        