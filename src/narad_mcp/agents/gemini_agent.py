import google.generativeai as genai
from narad_mcp.config import settings

class GeminiAgent:
    def __init__(self, api_key=None):
        self.api_key = api_key or settings.gemini_api_key.get_secret_value()
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in configuration")
        
        genai.configure(api_key=self.api_key)
        self.model_name = settings.gemini_model
        
        self.base_system_instruction = """
        You are the Narad GitHub Agent, a premium AI assistant powered by Gemini 2.0 Flash and the Model Context Protocol (MCP).
        Your mission is to provide expert-level technical analysis of GitHub repositories, commits, and codebases.
        
        Guidelines:
        - Be concise and professional.
        - Use technical terminology accurately.
        - When analyzing code, focus on architecture, efficiency, and security.
        - If a tool call fails, explain why clearly and suggest an alternative.
        """

    def generate_response(self, prompt: str, system_instruction: str = None) -> str:
        """
        Generate a high-quality response for a given prompt using Gemini 2.0 Flash.
        """
        instruction = system_instruction or self.base_system_instruction
        
        # Re-initialize model with specific system instruction if provided
        agent_model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=instruction
        )
        
        response = agent_model.generate_content(prompt)
        return response.text

    def analyze_repo_health(self, repo_name: str, readme_content: str, commit_history: str) -> str:
        """
        Provide a specialized 'Health Report' for a repository based on README and recent activity.
        """
        prompt = f"""
        Analyze the health and quality of the repository '{repo_name}' based on its README and recent commits:
        
        README:
        {readme_content}
        
        RECENT COMMITS:
        {commit_history}
        
        Evaluate project maturity, activity level, and documentation quality. Provide a score out of 10.
        """
        return self.generate_response(prompt)
