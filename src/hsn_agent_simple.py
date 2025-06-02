# src/hsn_agent_simple.py
from typing import Dict, List, Any, Optional
import json
import os

from .data_handler import HSNDataHandler
from .hsn_validator import HSNValidator
from .hsn_suggester import HSNSuggester

class HSNAgentSimple:
    """Simplified HSN Agent without full ADK integration for testing"""
    
    def __init__(self, excel_file_path: str):
        """Initialize HSN Agent with core components"""
        print("Initializing HSN Agent (Simplified)...")
        
        # Validate file path
        if not os.path.exists(excel_file_path):
            raise FileNotFoundError(f"Excel file not found: {excel_file_path}")
        
        # Initialize core components
        print("Loading HSN data...")
        self.data_handler = HSNDataHandler(excel_file_path)
        
        print("Setting up validator...")
        self.validator = HSNValidator(self.data_handler)
        
        print("Preparing ML suggestion engine...")
        self.suggester = HSNSuggester(self.data_handler)
        
        print("HSN Agent initialized successfully!")
        
        # Print summary
        summary = self.data_handler.get_data_summary()
        print(f"Loaded {summary['total_codes']} HSN codes")
        print(f"Code length distribution: {summary['code_lengths']}")
    
    def validate_hsn(self, hsn_code: str) -> Dict:
        """Validate a single HSN code"""
        return self.validator.full_validation(hsn_code)
    
    def validate_multiple_hsn(self, hsn_codes: List[str]) -> List[Dict]:
        """Validate multiple HSN codes"""
        return self.validator.validate_multiple(hsn_codes)
    
    def suggest_hsn(self, product_description: str, top_k: int = 5) -> List[Dict]:
        """Suggest HSN codes for a product description"""
        return self.suggester.suggest_hsn_codes(product_description, top_k)
    
    def suggest_with_explanation(self, product_description: str, top_k: int = 5) -> Dict:
        """Get HSN suggestions with detailed explanation"""
        return self.suggester.suggest_with_explanation(product_description, top_k)
    
    def get_data_summary(self) -> Dict:
        """Get summary of loaded HSN data"""
        return self.data_handler.get_data_summary()
    
    def health_check(self) -> Dict:
        """Perform health check on all components"""
        try:
            summary = self.data_handler.get_data_summary()
            test_validation = self.validator.full_validation("01")
            test_suggestion = self.suggester.suggest_hsn_codes("test product", 1)
            
            return {
                'status': 'healthy',
                'data_loaded': summary['total_codes'] > 0,
                'validator_working': isinstance(test_validation, dict),
                'suggester_working': isinstance(test_suggestion, list),
                'components': {
                    'data_handler': 'OK',
                    'validator': 'OK',
                    'suggester': 'OK'
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
