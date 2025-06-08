"""
Configuration settings for the Telegram bot
"""

import os

class Config:
    """Bot configuration class"""
    
    # Telegram Bot Token (required)
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    
    # Webhook configuration (optional)
    WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
    
    # Server configuration
    PORT = int(os.getenv('PORT', 5000))
    HOST = '0.0.0.0'
    
    # Storage configuration
    STORAGE_FILE = os.getenv('STORAGE_FILE', 'bot_settings.json')
    
    # Bot settings
    DEFAULT_CHAT_SETTINGS = {
        'enabled': True,  # Join/leave hider enabled by default
        'created_at': None,
        'updated_at': None
    }
    
    # Support group URL (optional)
    SUPPORT_GROUP_URL = os.getenv('SUPPORT_GROUP_URL', 'https://t.me/GodAcess')
    
    # Logging configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        
        return True
