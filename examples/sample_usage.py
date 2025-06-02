# examples/sample_usage.py
import sys
import os

# Get the absolute path to the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Now import should work
from src.hsn_agent_simple import HSNAgentSimple as HSNAgent
import json

def demo_hsn_agent():
    """Demonstrate HSN Agent capabilities"""
    
    print("🚀 HSN Code Validation and Suggestion Agent Demo")
    print("="*60)
    
    # Initialize agent
    excel_path = os.path.join(project_root, "data", "HSN_Master_Data.xlsx")
    
    if not os.path.exists(excel_path):
        print(f"❌ Please place your HSN Excel file at: {excel_path}")
        return
    
    agent = HSNAgent(excel_path)
    
    # Demo 1: Health Check
    print("\n🏥 Demo 1: Health Check")
    print("-" * 40)
    health = agent.health_check()
    print(f"Status: {health['status']}")
    
    # Demo 2: Data Summary
    print("\n📊 Demo 2: Data Summary")
    print("-" * 40)
    summary = agent.get_data_summary()
    print(f"Total HSN codes: {summary['total_codes']}")
    print(f"Code lengths: {summary['code_lengths']}")
    
    # Demo 3: Single HSN Validation
    print("\n📋 Demo 3: Single HSN Code Validation")
    print("-" * 40)
    
    test_hsn = "01"
    result = agent.validate_hsn(test_hsn)
    
    print(f"HSN Code: {test_hsn}")
    print(f"Valid: {'✅' if result['overall_valid'] else '❌'}")
    print(f"Description: {result.get('description', 'N/A')}")
    
    print("\n🎉 Demo completed!")

if __name__ == "__main__":
    demo_hsn_agent()
