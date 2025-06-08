"""
Storage management for bot settings and data
"""

import json
import os
import logging
from typing import Dict, Any
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class Storage:
    """Simple JSON file storage for bot settings"""
    
    def __init__(self, storage_file: str = None):
        """
        Initialize storage
        
        Args:
            storage_file: Path to storage file (optional)
        """
        self.storage_file = storage_file or Config.STORAGE_FILE
        self.data = self._load_data()
    
    def _load_data(self) -> dict:
        """Load data from storage file"""
        if not os.path.exists(self.storage_file):
            logger.info(f"Storage file {self.storage_file} doesn't exist, creating new one")
            return {'chats': {}, 'metadata': {'created_at': datetime.now().isoformat()}}
        
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Loaded data from {self.storage_file}")
                return data
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading storage file {self.storage_file}: {e}")
            logger.info("Creating new storage data")
            return {'chats': {}, 'metadata': {'created_at': datetime.now().isoformat()}}
    
    def _save_data(self):
        """Save data to storage file"""
        try:
            # Update metadata
            self.data['metadata']['updated_at'] = datetime.now().isoformat()
            
            # Write to file
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Data saved to {self.storage_file}")
        except IOError as e:
            logger.error(f"Error saving to storage file {self.storage_file}: {e}")
    
    def get_chat_settings(self, chat_id: int) -> dict:
        """
        Get settings for a specific chat
        
        Args:
            chat_id: Telegram chat ID
            
        Returns:
            dict: Chat settings
        """
        chat_key = str(chat_id)
        
        if chat_key not in self.data['chats']:
            # Create default settings for new chat
            settings = Config.DEFAULT_CHAT_SETTINGS.copy()
            settings['created_at'] = datetime.now().isoformat()
            settings['updated_at'] = settings['created_at']
            
            self.data['chats'][chat_key] = settings
            self._save_data()
            
            logger.info(f"Created default settings for chat {chat_id}")
        
        return self.data['chats'][chat_key].copy()
    
    def save_chat_settings(self, chat_id: int, settings: dict):
        """
        Save settings for a specific chat
        
        Args:
            chat_id: Telegram chat ID
            settings: Settings dictionary to save
        """
        chat_key = str(chat_id)
        
        # Update timestamp
        settings['updated_at'] = datetime.now().isoformat()
        
        # If this is a new chat, add created_at
        if chat_key not in self.data['chats']:
            settings['created_at'] = settings['updated_at']
        
        self.data['chats'][chat_key] = settings
        self._save_data()
        
        logger.info(f"Saved settings for chat {chat_id}: {settings}")
    
    def delete_chat_settings(self, chat_id: int):
        """
        Delete settings for a specific chat
        
        Args:
            chat_id: Telegram chat ID
        """
        chat_key = str(chat_id)
        
        if chat_key in self.data['chats']:
            del self.data['chats'][chat_key]
            self._save_data()
            logger.info(f"Deleted settings for chat {chat_id}")
    
    def get_all_chats(self) -> Dict[str, Any]:
        """
        Get settings for all chats
        
        Returns:
            dict: All chat settings
        """
        return self.data['chats'].copy()
    
    def get_enabled_chats(self) -> Dict[str, Any]:
        """
        Get all chats where the bot is enabled
        
        Returns:
            dict: Enabled chat settings
        """
        enabled_chats = {}
        
        for chat_id, settings in self.data['chats'].items():
            if settings.get('enabled', False):
                enabled_chats[chat_id] = settings
        
        return enabled_chats
    
    def get_stats(self) -> dict:
        """
        Get storage statistics
        
        Returns:
            dict: Storage statistics
        """
        total_chats = len(self.data['chats'])
        enabled_chats = len(self.get_enabled_chats())
        disabled_chats = total_chats - enabled_chats
        
        return {
            'total_chats': total_chats,
            'enabled_chats': enabled_chats,
            'disabled_chats': disabled_chats,
            'storage_file': self.storage_file,
            'created_at': self.data['metadata'].get('created_at'),
            'updated_at': self.data['metadata'].get('updated_at')
        }
    
    def backup_data(self, backup_file: str = None) -> str:
        """
        Create a backup of the current data
        
        Args:
            backup_file: Path for backup file (optional)
            
        Returns:
            str: Path to backup file
        """
        if not backup_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"{self.storage_file}.backup_{timestamp}"
        
        try:
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Data backed up to {backup_file}")
            return backup_file
        except IOError as e:
            logger.error(f"Error creating backup {backup_file}: {e}")
            raise
    
    def restore_data(self, backup_file: str):
        """
        Restore data from a backup file
        
        Args:
            backup_file: Path to backup file
        """
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            
            self._save_data()
            logger.info(f"Data restored from {backup_file}")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error restoring from backup {backup_file}: {e}")
            raise
