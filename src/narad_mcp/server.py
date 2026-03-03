import asyncio
import os
from mcp.server.fastmcp import FastMCP
from narad_mcp.tools.github_tools import GitHubTools
from narad_mcp.agents.gemini_agent import GeminiAgent
from dotenv import load_dotenv

load_dotenv()

# Create an MCP server
mcp = FastMCP("Narad GitHub Agent")

# Initialize our components
github_tools = GitHubTools()
# Gemini isn't directly exposed as a tool usually, but can be used for reasoning
# or exposed as a specialized "ask_gemini" tool.
gemini = GeminiAgent()

@mcp.tool()
async def list_repositories(username: str = None):
    """List GitHub repositories for a specific user or the authenticated user."""
    return github_tools.get_user_repositories(username)

@mcp.tool()
async def get_commits(full_repo_name: str, limit: int = 5):
    """Fetch recent commits for a given repository (e.g., 'owner/repo')."""
    return github_tools.get_recent_commits(full_repo_name, limit)

@mcp.tool()
async def explain_repo(full_repo_name: str):
    """Use Gemini 2.0 Flash to explain what a repository does based on its README."""
    readme_content = github_tools.get_repo_readme(full_repo_name)
    if readme_content.startswith("Error"):
        return readme_content
    
    prompt = f"Here is the README content of the repository '{full_repo_name}'. Please provide a concise and premium summary of what this project does and its key features:\n\n{readme_content}"
    summary = gemini.generate_response(prompt)
    return summary

@mcp.tool()
async def create_github_issue(full_repo_name: str, title: str, body: str = ""):
    """Create a new issue on GitHub."""
    return github_tools.create_issue(full_repo_name, title, body)

if __name__ == "__main__":
    # FastMCP can be run as a server
    mcp.run()
