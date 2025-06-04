import pandas as pd
import os

class HSNDataHandler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None
        self._load_data()
    
    def _load_data(self):
        """Load and preprocess HSN data"""
        self.data = pd.read_excel(
            self.file_path,
            usecols=['HSNCode', 'Description'],
            dtype={'HSNCode': str}
        )
        self.data['HSNCode'] = self.data['HSNCode'].str.strip()
        self.data = self.data.dropna().drop_duplicates()
    
    def get_hsn_info(self, code):
        """Get HSN code details"""
        return self.data[self.data['HSNCode'] == code].to_dict('records')
    
    def get_all_codes(self):
        """Get all HSN codes for validation"""
        return self.data['HSNCode'].tolist()
