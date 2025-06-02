# tests/test_agent.py
import sys
import os
import unittest
from unittest.mock import Mock, patch

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.hsn_agent_simple import HSNAgent
from src.data_handler import HSNDataHandler
from src.hsn_validator import HSNValidator
from src.hsn_suggester import HSNSuggester

class TestHSNAgent(unittest.TestCase):
    """Test cases for HSN Agent functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        # You'll need to provide a test Excel file
        cls.test_excel_path = "data/HSN_Master_Data.xlsx"
        
        # Skip tests if Excel file doesn't exist
        if not os.path.exists(cls.test_excel_path):
            raise unittest.SkipTest(f"Test Excel file not found: {cls.test_excel_path}")
    
    def setUp(self):
        """Set up for each test"""
        self.agent = HSNAgent(self.test_excel_path)
    
    def test_agent_initialization(self):
        """Test that agent initializes correctly"""
        self.assertIsNotNone(self.agent.data_handler)
        self.assertIsNotNone(self.agent.validator)
        self.assertIsNotNone(self.agent.suggester)
        self.assertIsNotNone(self.agent.agent)
    
    def test_hsn_validation_valid_code(self):
        """Test validation of valid HSN code"""
        # Test with a 2-digit code that should exist
        result = self.agent.validate_hsn("01")
        
        self.assertIsInstance(result, dict)
        self.assertIn('overall_valid', result)
        self.assertIn('format_valid', result)
        self.assertIn('exists', result)
    
    def test_hsn_validation_invalid_format(self):
        """Test validation of invalid format"""
        result = self.agent.validate_hsn("abc123")
        
        self.assertIsInstance(result, dict)
        self.assertFalse(result['overall_valid'])
        self.assertFalse(result['format_valid'])
    
    def test_hsn_validation_invalid_length(self):
        """Test validation of invalid length"""
        result = self.agent.validate_hsn("123456789")
        
        self.assertIsInstance(result, dict)
        self.assertFalse(result['overall_valid'])
        self.assertFalse(result['format_valid'])
    
    def test_batch_validation(self):
        """Test batch validation"""
        test_codes = ["01", "0101", "abc123"]
        results = self.agent.validate_multiple_hsn(test_codes)
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 3)
        
        for result in results:
            self.assertIsInstance(result, dict)
            self.assertIn('overall_valid', result)
    
    def test_hsn_suggestion(self):
        """Test HSN code suggestion"""
        suggestions = self.agent.suggest_hsn("cotton textile", top_k=3)
        
        self.assertIsInstance(suggestions, list)
        self.assertLessEqual(len(suggestions), 3)
        
        for suggestion in suggestions:
            self.assertIsInstance(suggestion, dict)
            self.assertIn('hsn_code', suggestion)
            self.assertIn('description', suggestion)
            self.assertIn('similarity_score', suggestion)
    
    def test_suggestion_with_explanation(self):
        """Test suggestion with explanation"""
        result = self.agent.suggest_with_explanation("mobile phone", top_k=2)
        
        self.assertIsInstance(result, dict)
        self.assertIn('suggestions', result)
        self.assertIn('analysis', result)
        self.assertIn('query', result)
    
    def test_health_check(self):
        """Test health check functionality"""
        health = self.agent.health_check()
        
        self.assertIsInstance(health, dict)
        self.assertIn('status', health)
        self.assertIn('components', health)
    
    def test_data_summary(self):
        """Test data summary"""
        summary = self.agent.get_data_summary()
        
        self.assertIsInstance(summary, dict)
        self.assertIn('total_codes', summary)
        self.assertIn('unique_codes', summary)
        self.assertGreater(summary['total_codes'], 0)

def run_comprehensive_test():
    """Run comprehensive test with sample data"""
    print("🧪 Running Comprehensive HSN Agent Test")
    print("="*50)
    
    try:
        # Initialize agent
        agent = HSNAgent("data/HSN_Master_Data.xlsx")
        
        # Test 1: Data Summary
        print("\n📊 Test 1: Data Summary")
        summary = agent.get_data_summary()
        print(f"   Total HSN codes loaded: {summary['total_codes']}")
        print(f"   Code length distribution: {summary['code_lengths']}")
        
        # Test 2: Health Check
        print("\n🏥 Test 2: Health Check")
        health = agent.health_check()
        print(f"   Status: {health['status']}")
        print(f"   All components: {health['components']}")
        
        # Test 3: HSN Validation Tests
        print("\n✅ Test 3: HSN Validation")
        test_codes = ["01", "0101", "010110", "01011010", "999999", "abc123"]
        
        for code in test_codes:
            result = agent.validate_hsn(code)
            status = "✅" if result['overall_valid'] else "❌"
            print(f"   {code}: {status} {result.get('error', 'Valid')}")
        
        # Test 4: HSN Suggestions
        print("\n🎯 Test 4: HSN Suggestions")
        test_descriptions = [
            "cotton shirts",
            "wheat flour",
            "mobile phone",
            "leather shoes"
        ]
        
        for desc in test_descriptions:
            suggestions = agent.suggest_hsn(desc, top_k=2)
            print(f"   '{desc}': {len(suggestions)} suggestions found")
            if suggestions:
                top_suggestion = suggestions[0]
                print(f"      Top: {top_suggestion['hsn_code']} (confidence: {top_suggestion['confidence_level']})")
        
        # Test 5: Batch Validation
        print("\n📦 Test 5: Batch Validation")
        batch_codes = ["01", "0101", "999999"]
        batch_results = agent.validate_multiple_hsn(batch_codes)
        valid_count = sum(1 for r in batch_results if r['overall_valid'])
        print(f"   Batch validation: {valid_count}/{len(batch_codes)} codes valid")
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")

if __name__ == "__main__":
    # Run comprehensive test
    run_comprehensive_test()
    
    # Run unit tests
    print("\n" + "="*50)
    print("Running Unit Tests...")
    unittest.main(verbosity=2)
