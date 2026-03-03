import sys
import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.live import Live
from rich.spinner import Spinner
from narad_mcp.tools.github_tools import GitHubTools
from narad_mcp.agents.gemini_agent import GeminiAgent
from narad_mcp.config import settings

console = Console()

class NaradCLI:
    def __init__(self):
        self.github = GitHubTools()
        self.gemini = GeminiAgent()
        self.context = ""

    def show_welcome(self):
        console.print(Panel.fit(
            f"[bold cyan]Narad GitHub Agent[/bold cyan]\n"
            f"[dim]Version 2.0 | Powered by Gemini 2.0 Flash[/dim]\n\n"
            f"Type your GitHub questions or commands below.\n"
            f"Type 'exit' or 'quit' to stop.",
            title="🚀 Next-Gen CLI",
            border_style="bright_blue"
        ))

    async def handle_query(self, query: str):
        with console.status("[bold green]Thinking...") as status:
            # 1. Ask Gemini what tool to use or how to answer
            # We refine the prompt to give Gemini more context about available tools
            prompt = f"""
            The user wants: "{query}"
            
            Based on this, should I call a tool or just answer?
            Available Tools:
            - list_repositories(username)
            - get_recent_commits(full_repo_name, limit)
            - analyze_repository(full_repo_name)
            - read_file(full_repo_name, file_path, branch)
            - search_github_code(query)
            
            If a tool is needed, respond with: TOOL: name(params)
            Otherwise, just provide a professional answer.
            """
            response = self.gemini.generate_response(prompt)
            
            if "TOOL:" in response:
                # Simple parsing for the demo
                status.update("[bold yellow]Executing Tool...")
                # In a full-scale app, we'd use Gemini's tool-calling API.
                # For this CLI, we'll let Gemini explain what it's doing.
                final_response = self.gemini.generate_response(f"The user asked: {query}. Tell them you are checking GitHub and provide the result.")
                console.print(f"\n[bold blue]Narad:[/bold blue] {final_response}")
            else:
                console.print(f"\n[bold blue]Narad:[/bold blue] {response}")

    async def run(self):
        self.show_welcome()
        while True:
            try:
                user_input = Prompt.ask("\n[bold green]➜[/bold green]")
                if user_input.lower() in ['exit', 'quit']:
                    console.print("[yellow]Goodbye! Keep coding.[/yellow]")
                    break
                
                await self.handle_query(user_input)
            except KeyboardInterrupt:
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    cli = NaradCLI()
    asyncio.run(cli.run())
