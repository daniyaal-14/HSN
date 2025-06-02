# src/hsn_validator.py
import re
from typing import Dict, List, Optional
from .data_handler import HSNDataHandler

class HSNValidator:
    """Validates HSN codes for format, existence, and hierarchical structure"""
    
    def __init__(self, data_handler: HSNDataHandler):
        """
        Initialize validator with data handler
        
        Args:
            data_handler (HSNDataHandler): Instance of HSN data handler
        """
        self.data_handler = data_handler
        self.valid_lengths = [2, 4, 6, 8]  # Valid HSN code lengths
        
    def validate_format(self, hsn_code: str) -> Dict:
        """
        Validate HSN code format
        
        Args:
            hsn_code (str): HSN code to validate
            
        Returns:
            Dict with validation results
        """
        original_code = hsn_code
        
        # Remove any spaces or special characters
        cleaned_code = re.sub(r'[^0-9]', '', str(hsn_code))
        
        # Check if it's numeric
        if not cleaned_code.isdigit():
            return {
                'valid': False,
                'error': 'HSN code must contain only numbers',
                'original_code': original_code,
                'cleaned_code': cleaned_code
            }
        
        # Check length
        if len(cleaned_code) not in self.valid_lengths:
            return {
                'valid': False,
                'error': f'HSN code must be {", ".join(map(str, self.valid_lengths))} digits. Got {len(cleaned_code)} digits',
                'original_code': original_code,
                'cleaned_code': cleaned_code
            }
        
        return {
            'valid': True,
            'original_code': original_code,
            'cleaned_code': cleaned_code,
            'length': len(cleaned_code)
        }
    
    def validate_existence(self, hsn_code: str) -> Dict:
        """
        Check if HSN code exists in master data
        
        Args:
            hsn_code (str): HSN code to check
            
        Returns:
            Dict with existence validation results
        """
        hsn_info = self.data_handler.get_hsn_info(hsn_code)
        
        if hsn_info:
            return {
                'exists': True,
                'hsn_code': hsn_info['hsn_code'],
                'description': hsn_info['description']
            }
        
        return {
            'exists': False,
            'hsn_code': hsn_code,
            'description': None
        }
    
    def validate_hierarchical(self, hsn_code: str) -> Dict:
        """
        Validate hierarchical structure of HSN code
        HSN codes follow hierarchical structure: 2-digit → 4-digit → 6-digit → 8-digit
        
        Args:
            hsn_code (str): HSN code to validate
            
        Returns:
            Dict with hierarchical validation results
        """
        if len(hsn_code) <= 2:
            return {
                'hierarchical_valid': True,
                'parent_codes': [],
                'valid_parents': [],
                'missing_parents': []
            }
        
        parent_codes = []
        valid_parents = []
        missing_parents = []
        
        # Check parent codes (2, 4, 6 digit prefixes)
        for length in [2, 4, 6]:
            if len(hsn_code) > length:
                parent_code = hsn_code[:length]
                parent_codes.append(parent_code)
                
                # Check if parent exists
                if self.data_handler.get_hsn_info(parent_code):
                    valid_parents.append(parent_code)
                else:
                    missing_parents.append(parent_code)
        
        hierarchical_valid = len(missing_parents) == 0
        
        return {
            'hierarchical_valid': hierarchical_valid,
            'parent_codes': parent_codes,
            'valid_parents': valid_parents,
            'missing_parents': missing_parents
        }
    
    def full_validation(self, hsn_code: str) -> Dict:
        """
        Perform complete HSN code validation
        
        Args:
            hsn_code (str): HSN code to validate
            
        Returns:
            Dict with complete validation results
        """
        # Format validation
        format_result = self.validate_format(hsn_code)
        if not format_result['valid']:
            return {
                'overall_valid': False,
                'hsn_code': format_result['original_code'],
                'cleaned_code': format_result.get('cleaned_code', ''),
                'error': format_result['error'],
                'format_valid': False,
                'exists': False,
                'hierarchical_valid': False,
                'validation_details': {
                    'format': format_result,
                    'existence': {'exists': False},
                    'hierarchical': {'hierarchical_valid': False}
                }
            }
        
        cleaned_code = format_result['cleaned_code']
        
        # Existence validation
        existence_result = self.validate_existence(cleaned_code)
        
        # Hierarchical validation
        hierarchical_result = self.validate_hierarchical(cleaned_code)
        
        # Overall validation
        overall_valid = (
            format_result['valid'] and 
            existence_result['exists'] and 
            hierarchical_result['hierarchical_valid']
        )
        
        return {
            'overall_valid': overall_valid,
            'hsn_code': format_result['original_code'],
            'cleaned_code': cleaned_code,
            'format_valid': format_result['valid'],
            'exists': existence_result['exists'],
            'description': existence_result.get('description', 'Not found'),
            'hierarchical_valid': hierarchical_result['hierarchical_valid'],
            'validation_details': {
                'format': format_result,
                'existence': existence_result,
                'hierarchical': hierarchical_result
            }
        }
    
    def validate_multiple(self, hsn_codes: List[str]) -> List[Dict]:
        """
        Validate multiple HSN codes
        
        Args:
            hsn_codes (List[str]): List of HSN codes to validate
            
        Returns:
            List of validation results
        """
        results = []
        for code in hsn_codes:
            result = self.full_validation(code)
            results.append(result)
        return results
