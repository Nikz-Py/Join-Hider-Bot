"""
Utility functions for the Telegram bot
"""

import logging
from datetime import datetime
from telegram import Bot, Chat
from telegram.constants import ChatMemberStatus
from telegram.error import TelegramError

logger = logging.getLogger(__name__)

async def is_admin(bot: Bot, chat_id: int, user_id: int) -> bool:
    """
    Check if a user is an administrator in a chat
    
    Args:
        bot: Telegram Bot instance
        chat_id: Chat ID to check
        user_id: User ID to check
        
    Returns:
        bool: True if user is admin, False otherwise
    """
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except TelegramError as e:
        logger.error(f"Error checking admin status for user {user_id} in chat {chat_id}: {e}")
        return False

def format_chat_settings(chat: Chat, settings: dict) -> str:
    """
    Format chat settings for display
    
    Args:
        chat: Telegram Chat object
        settings: Chat settings dictionary
        
    Returns:
        str: Formatted settings text
    """
    status_emoji = "🟢" if settings['enabled'] else "🔴"
    status_text = "Enabled" if settings['enabled'] else "Disabled"
    
    text = (
        f"⚙️ **Bot Settings for {chat.title}**\n\n"
        f"**Join/Leave Message Hider:** {status_emoji} {status_text}\n\n"
    )
    
    if settings['enabled']:
        text += (
            "✅ Join and leave messages will be automatically deleted\n"
            "🔧 Use the button below to disable this feature\n\n"
        )
    else:
        text += (
            "❌ Join and leave messages will NOT be deleted\n"
            "🔧 Use the button below to enable this feature\n\n"
        )
    
    text += (
        "**How it works:**\n"
        "• When enabled, I automatically delete join/leave notifications\n"
        "• I need admin privileges with 'Delete Messages' permission\n"
        "• Only group admins can change these settings\n\n"
        "**Note:** Make sure I have the required permissions to delete messages!"
    )
    
    return text

def get_current_timestamp() -> str:
    """Get current timestamp as string"""
    return datetime.now().isoformat()

def format_error_message(error: str, context: str = "") -> str:
    """
    Format error messages consistently
    
    Args:
        error: Error message
        context: Additional context (optional)
        
    Returns:
        str: Formatted error message
    """
    base_msg = f"❌ **Error:** {error}"
    
    if context:
        base_msg += f"\n\n**Context:** {context}"
    
    base_msg += "\n\nIf this problem persists, please check the bot's permissions or contact support."
    
    return base_msg

def escape_markdown(text: str) -> str:
    """
    Escape markdown special characters in text
    
    Args:
        text: Text to escape
        
    Returns:
        str: Escaped text
    """
    # Characters that need escaping in Telegram Markdown
    escape_chars = ['_', '*', '`', '[', ']', '(', ')', '~', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    
    return text

def truncate_text(text: str, max_length: int = 4096) -> str:
    """
    Truncate text to fit Telegram message limits
    
    Args:
        text: Text to truncate
        max_length: Maximum length (default: 4096 for Telegram)
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."

def format_chat_type(chat_type: str) -> str:
    """
    Format chat type for display
    
    Args:
        chat_type: Raw chat type from Telegram
        
    Returns:
        str: Formatted chat type
    """
    type_mapping = {
        'private': '👤 Private Chat',
        'group': '👥 Group',
        'supergroup': '👥 Supergroup',
        'channel': '📢 Channel'
    }
    
    return type_mapping.get(chat_type, f"🤖 {chat_type.title()}")
