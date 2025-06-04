from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
import asyncio

class HSNAgent:
    def __init__(self, data_path):
        # Initialize components
        self.data_handler = HSNDataHandler(data_path)
        self.validator = HSNValidator(self.data_handler)
        self.suggester = HSNSuggester(self.data_handler)
        
        # Create ADK tools
        self.tools = [
            FunctionTool(self.validate_hsn),
            FunctionTool(self.suggest_hsn)
        ]
        
        # Configure ADK agent
        self.agent = LlmAgent(
            name="hsn_agent",
            model="gemini-2.0-flash-exp",
            tools=self.tools,
            instruction=self._get_instruction()
        )
        
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=self.agent,
            session_service=self.session_service
        )
    
    def _get_instruction(self):
        return """You are an HSN code expert. Follow these rules:
        1. Validate codes for format, existence, and hierarchy
        2. Suggest codes using ML similarity
        3. Return detailed validation results
        4. Format responses with markdown"""
    
    async def validate_hsn(self, code: str) -> dict:
        """ADK Tool: Validate HSN code"""
        return {
            'valid_format': self.validator.validate_format(code),
            'exists': self.validator.validate_existence(code),
            'valid_hierarchy': self.validator.validate_hierarchy(code)
        }
    
    async def suggest_hsn(self, query: str) -> list:
        """ADK Tool: Suggest HSN codes"""
        return self.suggester.suggest(query)
    
    async def process_query(self, query: str):
        """Process user query through ADK"""
        session = await self.session_service.create_session(
            app_name="hsn_app",
            user_id="user1"
        )
        response = await self.runner.run(
            user_id="user1",
            session_id=session.id,
            new_message={"text": query}
        )
        return response
