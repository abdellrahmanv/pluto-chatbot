"""
Intent Detection Layer
Detects user intent from transcribed text using keyword matching
"""

import yaml
import logging
from typing import Dict, List


class IntentDetector:
    """Simple keyword-based intent detection"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize intent detector with configuration"""
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.intents = config['intents']
        self.logger.info("Intent detector initialized")
    
    def detect(self, text: str) -> str:
        """
        Detect intent from user input text
        
        Args:
            text: User's transcribed speech
        
        Returns:
            Intent name (e.g., 'greeting', 'fun_fact', 'unknown')
        """
        if not text:
            return 'unknown'
        
        # Convert to lowercase for case-insensitive matching
        text_lower = text.lower().strip()
        
        self.logger.debug(f"Detecting intent for: '{text}'")
        
        # Check each intent's keywords
        for intent_name, intent_data in self.intents.items():
            keywords = intent_data.get('keywords', [])
            
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    self.logger.info(f"Intent detected: {intent_name} (matched: '{keyword}')")
                    return intent_name
        
        # No match found
        self.logger.info("Intent detected: unknown (no keyword match)")
        return 'unknown'
    
    def get_intent_keywords(self, intent: str) -> List[str]:
        """Get list of keywords for a specific intent"""
        return self.intents.get(intent, {}).get('keywords', [])
    
    def get_all_intents(self) -> List[str]:
        """Get list of all available intents"""
        return list(self.intents.keys())
