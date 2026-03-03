import sys
import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from narad_mcp.tools.github_tools import GitHubTools
from narad_mcp.agents.gemini_agent import GeminiAgent
from narad_mcp.config import settings

console = Console()

class NaradCLI:
    def __init__(self):
        self.github = GitHubTools()
        self.gemini = GeminiAgent()

    def show_welcome(self):
        me = self.github.get_authenticated_username()
        console.print(Panel.fit(
            f"[bold cyan]Narad GitHub Agent[/bold cyan]"
            f" [dim]v2.0 | Gemini 2.0 Flash[/dim]\n"
            f"[green]Logged in as:[/green] [bold white]{me}[/bold white]\n\n"
            f"Commands:\n"
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

    def display_commits(self, commits):
        if isinstance(commits, str):
            console.print(f"[red]{commits}[/red]")
            return
        table = Table(title="📜 Recent Commits", box=box.ROUNDED, border_style="green")
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

    async def handle_query(self, user_input: str):
        parts = user_input.strip().split()
        if not parts:
            return

        cmd = parts[0].lower()

        # --- repos ---
        if cmd == "repos":
            username = parts[1] if len(parts) > 1 else None
            label = username or self.github.get_authenticated_username()
            with console.status(f"[bold green]Fetching repositories for [cyan]{label}[/cyan]..."):
                repos = self.github.get_user_repositories(username)
            self.display_repos(repos)

        # --- commits ---
        elif cmd == "commits":
            if len(parts) < 2:
                console.print("[yellow]Usage: commits <owner/repo>[/yellow]")
                return
            repo = parts[1]
            limit = int(parts[2]) if len(parts) > 2 else 5
            with console.status(f"[bold green]Fetching commits for {repo}..."):
                commits = self.github.get_recent_commits(repo, limit)
            self.display_commits(commits)

        # --- branches ---
        elif cmd == "branches":
            if len(parts) < 2:
                console.print("[yellow]Usage: branches <owner/repo>[/yellow]")
                return
            repo = parts[1]
            with console.status(f"[bold green]Fetching branches for {repo}..."):
                branches = self.github.list_branches(repo)
            self.display_list(f"🌿 Branches of {repo}", branches)

        # --- analyze ---
        elif cmd == "analyze":
            if len(parts) < 2:
                console.print("[yellow]Usage: analyze <owner/repo>[/yellow]")
                return
            repo = parts[1]
            with console.status(f"[bold cyan]Running AI analysis on {repo}..."):
                readme = self.github.get_repo_readme(repo)
                commits = self.github.get_recent_commits(repo, limit=10)
                if isinstance(commits, list):
                    activity = "\n".join([f"- {c['sha']}: {c['message']}" for c in commits])
                else:
                    activity = "No commits available"
                analysis = self.gemini.analyze_repo_health(repo, readme, activity)
            console.print(Panel(analysis, title=f"🧠 AI Analysis: {repo}", border_style="cyan"))

        # --- file ---
        elif cmd == "file":
            if len(parts) < 3:
                console.print("[yellow]Usage: file <owner/repo> <file_path> [branch][/yellow]")
                return
            repo = parts[1]
            path = parts[2]
            branch = parts[3] if len(parts) > 3 else "main"
            with console.status(f"[bold green]Reading {path} from {repo}..."):
                content = self.github.get_file_content(repo, path, branch)
            if isinstance(content, str) and "Error" not in content:
                console.print(Panel(content[:3000], title=f"📄 {path}", border_style="green"))
            else:
                console.print(f"[red]{content}[/red]")

        # --- ask ---
        elif cmd == "ask":
            if len(parts) < 2:
                console.print("[yellow]Usage: ask <your question>[/yellow]")
                return
            question = " ".join(parts[1:])
            with console.status("[bold cyan]Asking Gemini..."):
                answer = self.gemini.generate_response(question)
            console.print(Panel(answer, title="🤖 Gemini Says", border_style="cyan"))

        else:
            console.print(
                f"[yellow]Unknown command '[bold]{cmd}[/bold]'. "
                f"Type [bold]help[/bold] or see the welcome panel for available commands.[/yellow]"
            )

    async def run(self):
        self.show_welcome()
        while True:
            try:
                user_input = Prompt.ask("\n[bold green]➜[/bold green]")
                if user_input.lower() in ['exit', 'quit']:
                    console.print("[yellow]Goodbye! Keep building! 🚀[/yellow]")
                    break
                await self.handle_query(user_input)
            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted. Goodbye![/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    cli = NaradCLI()
    asyncio.run(cli.run())
