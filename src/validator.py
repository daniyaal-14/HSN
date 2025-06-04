import re

class HSNValidator:
    def __init__(self, data_handler):
        self.data = data_handler
        self.valid_lengths = [2, 4, 6, 8]
    
    def validate_format(self, code):
        """Validate HSN code structure"""
        code = re.sub(r'\D', '', code)
        return len(code) in self.valid_lengths and code.isdigit()
    
    def validate_existence(self, code):
        """Check code exists in dataset"""
        return bool(self.data.get_hsn_info(code))
    
    def validate_hierarchy(self, code):
        """Check parent codes exist"""
        code = re.sub(r'\D', '', code)
        parents = [code[:l] for l in [2,4,6] if len(code) > l]
        return all(self.data.get_hsn_info(p) for p in parents)
