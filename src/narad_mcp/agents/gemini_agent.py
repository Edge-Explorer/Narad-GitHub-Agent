import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiAgent:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=self.api_key)
        # Using Gemini 2.0 Flash (Experimental is currently available as 2.0-flash-exp)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def generate_response(self, prompt, system_instruction=None):
        """Generate a response structure based on user query."""
        if system_instruction:
            self.model = genai.GenerativeModel(
                model_name='gemini-2.0-flash-exp',
                system_instruction=system_instruction
            )
        
        response = self.model.generate_content(prompt)
        return response.text

    def decide_tool_call(self, query):
        """Analyze user query and decide which GitHub tools to use."""
        prompt = f"""
        Analyze the following user query about GitHub:
        "{query}"

        Decide which tool and parameters should be used.
        Available tools:
        - get_user_repositories(username: str | None)
        - get_recent_commits(full_repo_name: str, limit: int)
        - create_issue(full_repo_name: str, title: str, body: str)
        - get_repo_readme(full_repo_name: str)

        Return the decision in JSON format like: {{"tool": "tool_name", "params": {{...}}}}
        """
        response = self.model.generate_content(prompt)
        return response.text
