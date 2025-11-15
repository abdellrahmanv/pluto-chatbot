"""
Scenario Layer
Generates appropriate responses based on detected intent
"""

import yaml
import random
import logging
from typing import Optional


class ScenarioManager:
    """Manages different conversation scenarios"""
    
    def __init__(self, config_path: str = "config/config.yaml",
                 fun_facts_path: str = "data/fun_facts.txt"):
        """Initialize scenario manager"""
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.responses = config['responses']
        
        # Load fun facts
        self.fun_facts = self._load_fun_facts(fun_facts_path)
        
        self.logger.info("Scenario manager initialized")
    
    def _load_fun_facts(self, filepath: str) -> list:
        """Load fun facts from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                facts = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            self.logger.info(f"Loaded {len(facts)} fun facts")
            return facts
        except FileNotFoundError:
            self.logger.warning(f"Fun facts file not found: {filepath}")
            return ["I'd love to share a fun fact, but I seem to have misplaced my list!"]
    
    def get_response(self, intent: str, context: Optional[dict] = None) -> str:
        """
        Generate response based on intent
        
        Args:
            intent: Detected intent name
            context: Optional context data
        
        Returns:
            Response text to be spoken
        """
        self.logger.info(f"Generating response for intent: {intent}")
        
        if intent == 'greeting':
            return self._handle_greeting(context)
        
        elif intent == 'fun_fact':
            return self._handle_fun_fact(context)
        
        else:  # unknown or fallback
            return self._handle_fallback(context)
    
    def _handle_greeting(self, context: Optional[dict] = None) -> str:
        """Handle greeting scenario"""
        response = self.responses['greeting']
        self.logger.debug(f"Greeting response: {response}")
        return response
    
    def _handle_fun_fact(self, context: Optional[dict] = None) -> str:
        """Handle fun fact scenario"""
        if not self.fun_facts:
            return "I don't have any fun facts available right now."
        
        fact = random.choice(self.fun_facts)
        response = f"Here's a fun fact for you: {fact}"
        
        self.logger.debug(f"Fun fact response: {response}")
        return response
    
    def _handle_fallback(self, context: Optional[dict] = None) -> str:
        """Handle unknown/fallback scenario"""
        response = self.responses['fallback']
        self.logger.debug(f"Fallback response: {response}")
        return response
    
    def get_startup_message(self) -> str:
        """Get startup greeting message"""
        return self.responses.get('startup', "Hello! I'm ready!")
    
    def get_shutdown_message(self) -> str:
        """Get shutdown message"""
        return self.responses.get('shutdown', "Goodbye!")
