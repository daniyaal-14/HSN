# main.py
import argparse
import json
import os
import sys
from typing import List, Dict

# Add src to path for imports
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import the correct class name
from src.hsn_agent_simple import HSNAgentSimple

def print_json_pretty(data):
    """Print JSON data in a pretty format"""
    print(json.dumps(data, indent=2, ensure_ascii=False))

def validate_single_hsn(agent: HSNAgentSimple, hsn_code: str):
    """Validate a single HSN code"""
    print(f"\n{'='*50}")
    print(f"VALIDATING HSN CODE: {hsn_code}")
    print(f"{'='*50}")
    
    result = agent.validate_hsn(hsn_code)
    print_json_pretty(result)
    
    # Print summary
    print(f"\n📊 VALIDATION SUMMARY:")
    print(f"   Overall Valid: {'✅ YES' if result['overall_valid'] else '❌ NO'}")
    print(f"   Format Valid: {'✅' if result['format_valid'] else '❌'}")
    print(f"   Exists in DB: {'✅' if result['exists'] else '❌'}")
    print(f"   Hierarchical: {'✅' if result['hierarchical_valid'] else '❌'}")

def validate_multiple_hsn(agent: HSNAgentSimple, hsn_codes: List[str]):
    """Validate multiple HSN codes"""
    print(f"\n{'='*50}")
    print(f"BATCH VALIDATION: {len(hsn_codes)} HSN CODES")
    print(f"{'='*50}")
    
    results = agent.validate_multiple_hsn(hsn_codes)
    
    # Print individual results
    for i, result in enumerate(results):
        print(f"\n[{i+1}] HSN Code: {result['hsn_code']}")
        print(f"    Valid: {'✅' if result['overall_valid'] else '❌'}")
        if not result['overall_valid']:
            print(f"    Error: {result.get('error', 'Multiple validation failures')}")
    
    # Print batch summary
    valid_count = sum(1 for r in results if r['overall_valid'])
    print(f"\n📊 BATCH SUMMARY:")
    print(f"   Total Codes: {len(results)}")
    print(f"   Valid Codes: {valid_count}")
    print(f"   Invalid Codes: {len(results) - valid_count}")
    print(f"   Success Rate: {(valid_count/len(results)*100):.1f}%")

def suggest_hsn_codes(agent: HSNAgentSimple, product_description: str, top_k: int):
    """Suggest HSN codes for a product description"""
    print(f"\n{'='*50}")
    print(f"HSN SUGGESTIONS FOR: {product_description}")
    print(f"{'='*50}")
    
    suggestions = agent.suggest_hsn(product_description, top_k)
    
    if not suggestions:
        print("❌ No suggestions found for this product description.")
        return
    
    print(f"\n🎯 TOP {len(suggestions)} SUGGESTIONS:")
    for i, suggestion in enumerate(suggestions):
        print(f"\n[{i+1}] HSN Code: {suggestion['hsn_code']}")
        print(f"    Description: {suggestion['description']}")
        print(f"    Confidence: {suggestion['confidence_level']}")
        print(f"    Similarity: {suggestion['similarity_score']:.3f}")
        print(f"    Method: {suggestion['match_type']}")

def suggest_with_explanation(agent: HSNAgentSimple, product_description: str, top_k: int):
    """Get HSN suggestions with detailed explanation"""
    print(f"\n{'='*50}")
    print(f"DETAILED HSN ANALYSIS FOR: {product_description}")
    print(f"{'='*50}")
    
    result = agent.suggest_with_explanation(product_description, top_k)
    
    print(f"\n🔍 ANALYSIS:")
    print(f"   Key Terms: {', '.join(result['analysis']['key_terms_identified'])}")
    print(f"   Methods Used: {', '.join(result['analysis']['suggestion_methods'])}")
    
    print(f"\n🎯 SUGGESTIONS:")
    for i, suggestion in enumerate(result['suggestions']):
        print(f"\n[{i+1}] {suggestion['hsn_code']} - {suggestion['confidence_level']} Confidence")
        print(f"    {suggestion['description']}")
        print(f"    Score: {suggestion['similarity_score']:.3f}")

def interactive_mode(agent: HSNAgentSimple):
    """Run in interactive mode"""
    print(f"\n{'='*60}")
    print("🚀 HSN AGENT INTERACTIVE MODE")
    print(f"{'='*60}")
    print("Commands:")
    print("  validate <hsn_code>     - Validate HSN code")
    print("  suggest <description>   - Get HSN suggestions")
    print("  batch <code1,code2,...> - Validate multiple codes")
    print("  summary                 - Show data summary")
    print("  health                  - Health check")
    print("  quit                    - Exit")
    print(f"{'='*60}")
    
    while True:
        try:
            user_input = input("\n💬 Enter command: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'summary':
                summary = agent.get_data_summary()
                print_json_pretty(summary)
                continue
            
            if user_input.lower() == 'health':
                health = agent.health_check()
                print_json_pretty(health)
                continue
            
            if user_input.startswith('validate '):
                hsn_code = user_input[9:].strip()
                validate_single_hsn(agent, hsn_code)
                continue
            
            if user_input.startswith('suggest '):
                description = user_input[8:].strip()
                suggest_hsn_codes(agent, description, 5)
                continue
            
            if user_input.startswith('batch '):
                codes_str = user_input[6:].strip()
                codes = [code.strip() for code in codes_str.split(',')]
                validate_multiple_hsn(agent, codes)
                continue
            
            print("❌ Unknown command. Type 'quit' to exit.")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='HSN Code Validation and Suggestion Agent',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --excel-file data/HSN_Master_Data.xlsx --action validate --input "01011010"
  python main.py --excel-file data/HSN_Master_Data.xlsx --action suggest --input "Cotton shirts"
  python main.py --excel-file data/HSN_Master_Data.xlsx --action batch --input "01,0101,010110"
  python main.py --excel-file data/HSN_Master_Data.xlsx --interactive
        """
    )
    
    parser.add_argument(
        '--excel-file', 
        required=True, 
        help='Path to HSN master data Excel file'
    )
    
    parser.add_argument(
        '--action', 
        choices=['validate', 'suggest', 'batch', 'explain'], 
        help='Action to perform'
    )
    
    parser.add_argument(
        '--input', 
        help='HSN code(s) to validate or product description for suggestion'
    )
    
    parser.add_argument(
        '--top-k', 
        type=int, 
        default=5, 
        help='Number of suggestions to return (default: 5)'
    )
    
    parser.add_argument(
        '--interactive', 
        action='store_true', 
        help='Run in interactive mode'
    )
    
    args = parser.parse_args()
    
    # Validate Excel file exists
    if not os.path.exists(args.excel_file):
        print(f"❌ Error: Excel file not found: {args.excel_file}")
        return 1
    
    try:
        # Initialize agent with correct class name
        print("🚀 Initializing HSN Agent...")
        agent = HSNAgentSimple(args.excel_file)
        
        # Interactive mode
        if args.interactive:
            interactive_mode(agent)
            return 0
        
        # Command line mode
        if not args.action or not args.input:
            print("❌ Error: --action and --input are required for non-interactive mode")
            return 1
        
        if args.action == 'validate':
            validate_single_hsn(agent, args.input)
        
        elif args.action == 'suggest':
            suggest_hsn_codes(agent, args.input, args.top_k)
        
        elif args.action == 'explain':
            suggest_with_explanation(agent, args.input, args.top_k)
        
        elif args.action == 'batch':
            hsn_codes = [code.strip() for code in args.input.split(',')]
            validate_multiple_hsn(agent, hsn_codes)
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
