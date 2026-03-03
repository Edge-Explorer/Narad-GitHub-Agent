import sys
import asyncio
import json
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from narad_mcp.tools.github_tools import GitHubTools
from narad_mcp.agents.gemini_agent import GeminiAgent
from narad_mcp.config import settings

console = Console()

INTENT_PROMPT = """
You are the command parser for the Narad GitHub Agent CLI. The user typed a natural language message.
Your job is to convert it into a structured command JSON.

Available commands and their JSON format:
- repos (own): {{"cmd": "repos", "username": null}}
- repos (other user): {{"cmd": "repos", "username": "<username>"}}
- commits: {{"cmd": "commits", "repo": "<owner/repo>", "limit": <number or 5>}}
- branches: {{"cmd": "branches", "repo": "<owner/repo>"}}
- analyze: {{"cmd": "analyze", "repo": "<owner/repo>"}}
- file: {{"cmd": "file", "repo": "<owner/repo>", "path": "<file_path>", "branch": "main"}}
- ask (general question): {{"cmd": "ask", "question": "<the question>"}}
- exit: {{"cmd": "exit"}}

Rules:
- If the user says "my repos", "list my repos" etc: cmd=repos, username=null.
- If the user asks for commits but does NOT mention a specific repo (owner/repo format), use cmd=ask with question set to: "I need a specific repository to fetch commits from the GitHub API. Which repo do you want? Example: type  commits Edge-Explorer/Narad-GitHub-Agent"
- If a specific repo is mentioned in the query, extract it and use cmd=commits.
- For general coding, GitHub, or open-ended questions: use cmd=ask.
- Return ONLY valid JSON. No markdown, no explanation.

User message: "{message}"
"""

class NaradCLI:
    def __init__(self):
        self.github = GitHubTools()
        self.gemini = GeminiAgent()
        self.me = self.github.get_authenticated_username()

    def show_welcome(self):
        console.print(Panel.fit(
            f"[bold cyan]Narad GitHub Agent[/bold cyan]"
            f" [dim]v2.0 | Gemini 2.0 Flash[/dim]\n"
            f"[green]Logged in as:[/green] [bold white]{self.me}[/bold white]\n\n"
            f"[dim]You can type natural language or use commands:[/dim]\n"
            f"  [green]repos[/green]                     - [dim]Your repos (auto-detected)[/dim]\n"
            f"  [green]repos <username>[/green]          - [dim]Any user's repos[/dim]\n"
            f"  [green]commits <owner/repo>[/green]      - [dim]Recent commits[/dim]\n"
            f"  [green]branches <owner/repo>[/green]     - [dim]List branches[/dim]\n"
            f"  [green]analyze <owner/repo>[/green]      - [dim]AI health report[/dim]\n"
            f"  [green]file <owner/repo> <path>[/green]  - [dim]Read a file[/dim]\n"
            f"  [green]ask <question>[/green]            - [dim]Ask Gemini anything[/dim]\n"
            f"  [green]exit[/green]                      - [dim]Quit[/dim]",
            title="🚀 Narad CLI",
            border_style="bright_blue"
        ))

    def display_repos(self, repos):
        if isinstance(repos, str):
            console.print(f"[red]{repos}[/red]")
            return
        table = Table(title="📦 Repositories", box=box.ROUNDED, border_style="blue")
        table.add_column("Repository", style="cyan", no_wrap=True)
        for repo in repos:
            table.add_row(repo)
        console.print(table)

    def display_commits(self, commits, repo=""):
        if isinstance(commits, str):
            console.print(f"[red]{commits}[/red]")
            return
        table = Table(title=f"📜 Commits: {repo}", box=box.ROUNDED, border_style="green")
        table.add_column("SHA", style="yellow", width=8)
        table.add_column("Author", style="cyan", width=20)
        table.add_column("Date", style="dim", width=22)
        table.add_column("Message", style="white")
        for c in commits:
            table.add_row(c['sha'], c['author'], c['date'], c['message'].strip()[:80])
        console.print(table)

    def display_list(self, title, items):
        if isinstance(items, str):
            console.print(f"[red]{items}[/red]")
            return
        table = Table(title=title, box=box.ROUNDED, border_style="magenta")
        table.add_column("Name", style="cyan")
        for item in items:
            table.add_row(item)
        console.print(table)

    def parse_intent(self, user_input: str) -> dict:
        """Use Gemini to convert natural language to a structured command."""
        prompt = INTENT_PROMPT.format(message=user_input)
        response = self.gemini.generate_response(prompt, system_instruction="You are a JSON command parser. Return only valid JSON.")
        # Strip markdown code blocks if Gemini wraps it
        response = response.strip().strip("```json").strip("```").strip()
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback: treat as an ask question
            return {"cmd": "ask", "question": user_input}

    async def execute_command(self, parsed: dict):
        cmd = parsed.get("cmd", "ask")

        if cmd == "repos":
            username = parsed.get("username")
            label = username or self.me
            with console.status(f"[bold green]Fetching repositories for [cyan]{label}[/cyan]..."):
                repos = self.github.get_user_repositories(username)
            self.display_repos(repos)

        elif cmd == "commits":
            repo = parsed.get("repo")
            limit = parsed.get("limit", 5)
            if not repo:
                console.print("[yellow]Please specify a repo, e.g. 'commits for Edge-Explorer/Narad-GitHub-Agent'[/yellow]")
                return
            with console.status(f"[bold green]Fetching commits for [cyan]{repo}[/cyan]..."):
                commits = self.github.get_recent_commits(repo, limit)
            self.display_commits(commits, repo)

        elif cmd == "branches":
            repo = parsed.get("repo")
            with console.status(f"[bold green]Fetching branches for [cyan]{repo}[/cyan]..."):
                branches = self.github.list_branches(repo)
            self.display_list(f"🌿 Branches: {repo}", branches)

        elif cmd == "analyze":
            repo = parsed.get("repo")
            with console.status(f"[bold cyan]Running AI analysis on [green]{repo}[/green]..."):
                readme = self.github.get_repo_readme(repo)
                commits = self.github.get_recent_commits(repo, limit=10)
                activity = "\n".join([f"- {c['sha']}: {c['message']}" for c in commits]) if isinstance(commits, list) else "N/A"
                result = self.gemini.analyze_repo_health(repo, readme, activity)
            console.print(Panel(result, title=f"🧠 AI Analysis: {repo}", border_style="cyan"))

        elif cmd == "file":
            repo = parsed.get("repo")
            path = parsed.get("path")
            branch = parsed.get("branch", "main")
            with console.status(f"[bold green]Reading [cyan]{path}[/cyan] from [green]{repo}[/green]..."):
                content = self.github.get_file_content(repo, path, branch)
            if isinstance(content, str) and "Error" not in content:
                console.print(Panel(content[:3000], title=f"📄 {path}", border_style="green"))
            else:
                console.print(f"[red]{content}[/red]")

        elif cmd == "ask":
            question = parsed.get("question", "")
            with console.status("[bold cyan]Asking Gemini..."):
                answer = self.gemini.generate_response(question)
            console.print(Panel(answer, title="🤖 Gemini Says", border_style="cyan"))

        elif cmd == "exit":
            raise SystemExit

        else:
            console.print(f"[yellow]I didn't understand that. Try rephrasing![/yellow]")

    async def run(self):
        self.show_welcome()
        while True:
            try:
                user_input = Prompt.ask("\n[bold green]➜[/bold green]")
                if user_input.lower() in ['exit', 'quit']:
                    console.print("[yellow]Goodbye! Keep building! 🚀[/yellow]")
                    break

                with console.status("[dim]Parsing intent...[/dim]"):
                    parsed = self.parse_intent(user_input)

                await self.execute_command(parsed)

            except SystemExit:
                console.print("[yellow]Goodbye! Keep building! 🚀[/yellow]")
                break
            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted. Goodbye![/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    cli = NaradCLI()
    asyncio.run(cli.run())
