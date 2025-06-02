# src/data_handler.py
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import re
import os

class HSNDataHandler:
    """Handles loading and processing of HSN master data from Excel file"""
    
    def __init__(self, excel_file_path: str):
        """
        Initialize with Excel file containing HSN master data
        
        Args:
            excel_file_path (str): Path to the Excel file with HSN data
        """
        self.excel_file_path = excel_file_path
        self.hsn_data = None
        self.hsn_lookup = {}  # For faster lookups
        self._validate_file_exists()
        self.load_data()
        
    def _validate_file_exists(self):
        """Check if the Excel file exists"""
        if not os.path.exists(self.excel_file_path):
            raise FileNotFoundError(f"Excel file not found: {self.excel_file_path}")
    
    def load_data(self):
        """Load HSN data from Excel file efficiently"""
        try:
            print(f"Loading HSN data from: {self.excel_file_path}")
            
            # Read Excel file - adjust column names based on your actual Excel structure
            self.hsn_data = pd.read_excel(
                self.excel_file_path,
                sheet_name=0,  # Use first sheet
                dtype={'HSNCode': str, 'Description': str}  # Ensure proper data types
            )
            
            # Print column names to help debug
            print(f"Available columns: {list(self.hsn_data.columns)}")
            
            # Adjust column names based on your Excel file structure
            # Common variations: 'HSN Code', 'HSN_Code', 'Code', 'Description', 'Product Description'
            column_mapping = self._detect_columns()
            
            if column_mapping['hsn_col'] and column_mapping['desc_col']:
                # Rename columns to standard names
                self.hsn_data = self.hsn_data.rename(columns={
                    column_mapping['hsn_col']: 'HSNCode',
                    column_mapping['desc_col']: 'Description'
                })
            else:
                raise ValueError("Could not detect HSN Code and Description columns")
            
            # Clean and preprocess data
            self._clean_data()
            
            # Create lookup dictionary for faster searches
            self._create_lookup()
            
            print(f"Successfully loaded {len(self.hsn_data)} HSN codes")
            
        except Exception as e:
            raise Exception(f"Error loading HSN data: {str(e)}")
    
    def _detect_columns(self) -> Dict[str, Optional[str]]:
        """Detect HSN Code and Description columns automatically"""
        columns = [col.lower().strip() for col in self.hsn_data.columns]
        
        hsn_col = None
        desc_col = None
        
        # Common HSN code column names
        hsn_patterns = ['hsn', 'code', 'hsn_code', 'hsn code', 'hsncode']
        for pattern in hsn_patterns:
            for col in self.hsn_data.columns:
                if pattern in col.lower():
                    hsn_col = col
                    break
            if hsn_col:
                break
        
        # Common description column names
        desc_patterns = ['description', 'desc', 'product', 'item', 'goods']
        for pattern in desc_patterns:
            for col in self.hsn_data.columns:
                if pattern in col.lower():
                    desc_col = col
                    break
            if desc_col:
                break
        
        return {'hsn_col': hsn_col, 'desc_col': desc_col}
    
    def _clean_data(self):
        """Clean and preprocess the HSN data"""
        # Remove rows with missing values
        self.hsn_data = self.hsn_data.dropna(subset=['HSNCode', 'Description'])
        
        # Clean HSN codes - remove spaces and ensure string format
        self.hsn_data['HSNCode'] = self.hsn_data['HSNCode'].astype(str).str.strip()
        self.hsn_data['HSNCode'] = self.hsn_data['HSNCode'].str.replace(' ', '')
        
        # Clean descriptions
        self.hsn_data['Description'] = self.hsn_data['Description'].astype(str).str.strip()
        
        # Remove duplicates
        self.hsn_data = self.hsn_data.drop_duplicates(subset=['HSNCode'])
        
        # Reset index
        self.hsn_data = self.hsn_data.reset_index(drop=True)
    
    def _create_lookup(self):
        """Create lookup dictionary for faster HSN code searches"""
        for _, row in self.hsn_data.iterrows():
            self.hsn_lookup[row['HSNCode']] = {
                'description': row['Description'],
                'index': row.name
            }
    
    def get_hsn_info(self, hsn_code: str) -> Optional[Dict]:
        """
        Get HSN code information quickly using lookup
        
        Args:
            hsn_code (str): HSN code to search for
            
        Returns:
            Dict with HSN info or None if not found
        """
        hsn_code = str(hsn_code).strip()
        
        if hsn_code in self.hsn_lookup:
            return {
                'hsn_code': hsn_code,
                'description': self.hsn_lookup[hsn_code]['description']
            }
        return None
    
    def search_by_description(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search HSN codes by description using text matching
        
        Args:
            query (str): Search query
            limit (int): Maximum number of results
            
        Returns:
            List of matching HSN codes with descriptions
        """
        query = query.lower().strip()
        
        # Simple text matching - case insensitive
        mask = self.hsn_data['Description'].str.lower().str.contains(
            query, case=False, na=False, regex=False
        )
        
        results = self.hsn_data[mask].head(limit)
        
        return [
            {
                'hsn_code': row['HSNCode'],
                'description': row['Description'],
                'match_type': 'description_search'
            }
            for _, row in results.iterrows()
        ]
    
    def get_all_hsn_codes(self) -> List[str]:
        """Get list of all HSN codes"""
        return self.hsn_data['HSNCode'].tolist()
    
    def get_data_summary(self) -> Dict:
        """Get summary statistics of the loaded data"""
        return {
            'total_codes': len(self.hsn_data),
            'unique_codes': self.hsn_data['HSNCode'].nunique(),
            'code_lengths': self.hsn_data['HSNCode'].str.len().value_counts().to_dict(),
            'sample_codes': self.hsn_data['HSNCode'].head(5).tolist()
        }
