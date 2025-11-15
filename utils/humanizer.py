"""
Humanization Layer
Post-processes responses to make them more natural and human-like
"""

import logging
import yaml
import re


class Humanizer:
    """Makes responses more natural and conversational"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize humanizer"""
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.enabled = config['system'].get('enable_humanization', True)
        
        self.logger.info(f"Humanizer initialized (enabled: {self.enabled})")
    
    def humanize(self, text: str) -> str:
        """
        Make text more natural and human-like
        
        Args:
            text: Original response text
        
        Returns:
            Humanized text
        """
        if not self.enabled or not text:
            return text
        
        self.logger.debug(f"Humanizing: '{text}'")
        
        # Apply humanization techniques
        humanized = text
        
        # 1. Add natural pauses (commas for breathing)
        humanized = self._add_natural_pauses(humanized)
        
        # 2. Remove overly formal language
        humanized = self._casual_language(humanized)
        
        # 3. Fix punctuation
        humanized = self._fix_punctuation(humanized)
        
        self.logger.debug(f"Humanized: '{humanized}'")
        
        return humanized
    
    def _add_natural_pauses(self, text: str) -> str:
        """Add natural pauses for better speech flow"""
        # Add comma after introductory phrases if missing
        patterns = [
            (r'^(Well|So|Actually|Basically|Honestly)\s+', r'\1, '),
            (r'^(By the way|As a matter of fact)\s+', r'\1, '),
        ]
        
        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _casual_language(self, text: str) -> str:
        """Replace formal phrases with casual ones"""
        replacements = {
            'I would like to': "I'd like to",
            'I am': "I'm",
            'You are': "You're",
            'It is': "It's",
            'That is': "That's",
            'Cannot': "Can't",
            'Do not': "Don't",
            'Will not': "Won't",
        }
        
        for formal, casual in replacements.items():
            text = re.sub(formal, casual, text, flags=re.IGNORECASE)
        
        return text
    
    def _fix_punctuation(self, text: str) -> str:
        """Ensure proper punctuation"""
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Ensure space after punctuation
        text = re.sub(r'([.,!?])(\w)', r'\1 \2', text)
        
        # Remove space before punctuation
        text = re.sub(r'\s+([.,!?])', r'\1', text)
        
        # Ensure sentence ends with punctuation
        if text and not text[-1] in '.!?':
            text += '.'
        
        return text.strip()
