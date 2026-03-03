import asyncio
import logging
from mcp.server.fastmcp import FastMCP
from narad_mcp.tools.github_tools import GitHubTools
from narad_mcp.agents.gemini_agent import GeminiAgent
from narad_mcp.config import settings

# Initialize logging for the server
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger("narad_mcp_server")

# Create an industry-grade MCP server
mcp = FastMCP(settings.app_name)

# Initialize our components
github_tools = GitHubTools()
gemini = GeminiAgent()

@mcp.tool()
async def list_repositories(username: str = None):
    """List GitHub repositories for a user or the authenticated user."""
    logger.info(f"Listing repositories for: {username or 'me'}")
    return github_tools.get_user_repositories(username)

@mcp.tool()
async def get_commits(full_repo_name: str, limit: int = None):
    """Fetch recent commits for a repository (e.g., 'owner/repo')."""
    logger.info(f"Fetching commits for: {full_repo_name}")
    return github_tools.get_recent_commits(full_repo_name, limit)

@mcp.tool()
async def analyze_repository(full_repo_name: str):
    """Perform a deep AI analysis of a repository's health and activity."""
    logger.info(f"Deep analyzing repository: {full_repo_name}")
    
    readme = github_tools.get_repo_readme(full_repo_name)
    commits = github_tools.get_recent_commits(full_repo_name, limit=10)
    
    if isinstance(readme, str) and "Error" in readme:
        return f"Could not analyze: {readme}"
        
    activity_summary = "\n".join([f"- {c['sha']}: {c['message']}" for c in commits])
    return gemini.analyze_repo_health(full_repo_name, readme, activity_summary)

@mcp.tool()
async def read_file(full_repo_name: str, file_path: str, branch: str = "main"):
    """Read the content of a specific file from a GitHub repository."""
    logger.info(f"Reading file '{file_path}' from '{full_repo_name}' [{branch}]")
    return github_tools.get_file_content(full_repo_name, file_path, branch)

@mcp.tool()
async def search_github_code(query: str):
    """Search for code snippets across all public GitHub repositories."""
    logger.info(f"Searching GitHub code for: {query}")
    return github_tools.search_code(query)

@mcp.tool()
async def list_repo_branches(full_repo_name: str):
    """List all available branches for a GitHub repository."""
    logger.info(f"Listing branches for: {full_repo_name}")
    return github_tools.list_branches(full_repo_name)

@mcp.tool()
async def ask_gemini_github(question: str):
    """Ask Gemini 2.0 Flash a general question about GitHub or software engineering."""
    logger.info(f"Answering general question: {question}")
    return gemini.generate_response(question)

if __name__ == "__main__":
    logger.info(f"Starting {settings.app_name}...")
    mcp.run()
