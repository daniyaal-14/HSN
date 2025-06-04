import argparse
import asyncio
from src.agent import HSNAgent

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', choices=['validate', 'suggest'], required=True)
    parser.add_argument('--input', required=True)
    args = parser.parse_args()
    
    agent = HSNAgent("data/HSN_Master_Data.xlsx")
    
    if args.action == 'validate':
        result = await agent.validate_hsn(args.input)
        print(f"Validation Result: {result}")
    elif args.action == 'suggest':
        result = await agent.suggest_hsn(args.input)
        print("Suggestions:")
        for item in result:
            print(f"{item['hsn_code']}: {item['description']} (Score: {item['score']:.2f})")

if __name__ == "__main__":
    asyncio.run(main())
