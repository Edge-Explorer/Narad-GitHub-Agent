from google import genai
from google.genai import types
from narad_mcp.config import settings

class GeminiAgent:
    def __init__(self, api_key=None):
        api_key = api_key or settings.gemini_api_key.get_secret_value()
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in configuration")
        
        # New Google GenAI SDK Client
        self.client = genai.Client(api_key=api_key)
        self.model_name = settings.gemini_model  # should be gemini-2.0-flash or gemini-2.0-flash-exp
        
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
        Generate a high-quality response for a given prompt using Gemini 2.0 Flash (New SDK).
        """
        instruction = system_instruction or self.base_system_instruction
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                config=types.GenerateContentConfig(
                    system_instruction=instruction,
                ),
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Gemini API Error: {str(e)}"

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
