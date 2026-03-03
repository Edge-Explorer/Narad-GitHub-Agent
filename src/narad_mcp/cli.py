import sys
import asyncio
import json
import uuid
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from narad_mcp.tools.github_tools import GitHubTools
from narad_mcp.agents.gemini_agent import GeminiAgent
from narad_mcp.config import settings
from narad_mcp import database as db

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
- prs: {{"cmd": "prs", "repo": "<owner/repo>"}}
- review_pr: {{"cmd": "review_pr", "repo": "<owner/repo>", "pr_number": <number>}}
- digest: {{"cmd": "digest"}}
- history: {{"cmd": "history"}}
- ask (general question): {{"cmd": "ask", "question": "<the question>"}}
- exit: {{"cmd": "exit"}}

Rules:
- If the user says "my repos", "list my repos" etc: cmd=repos, username=null.
- If the user asks for commits but does NOT mention a specific repo (owner/repo format), use cmd=ask with question set to: "I need a specific repository to fetch commits. Which repo? Example: commits Edge-Explorer/Narad-GitHub-Agent"
- If a specific repo is mentioned in the query, extract it and use the right cmd.
- "digest", "daily digest", "morning report" -> cmd=digest.
- "review PR", "code review" -> cmd=review_pr with repo and pr_number.
- "open PRs", "list PRs" -> cmd=prs.
- "history", "past questions", "what did I ask" -> cmd=history.
- For general coding, GitHub, or open-ended questions: use cmd=ask.
- Return ONLY valid JSON. No markdown, no explanation.

User message: "{message}"
"""

class NaradCLI:
    def __init__(self):
        db.init_db()
        self.github = GitHubTools()
        self.gemini = GeminiAgent()
        self.me = self.github.get_authenticated_username()
        self.session_id = str(uuid.uuid4())

    def show_welcome(self):
        console.print(Panel.fit(
            f"[bold cyan]Narad GitHub Agent[/bold cyan]"
            f" [dim]v2.0 | Gemini 2.0 Flash[/dim]\n"
            f"[green]Logged in as:[/green] [bold white]{self.me}[/bold white]"
            f" [dim]| Session: {self.session_id[:8]}[/dim]\n\n"
            f"[dim]You can type natural language or use these keywords:[/dim]\n"
            f"  [green]repos[/green]                       - [dim]Your repos[/dim]\n"
            f"  [green]commits <owner/repo>[/green]        - [dim]Recent commits[/dim]\n"
            f"  [green]branches <owner/repo>[/green]       - [dim]Branches[/dim]\n"
            f"  [green]prs <owner/repo>[/green]            - [dim]Open pull requests[/dim]\n"
            f"  [green]review pr <owner/repo> <#>[/green]  - [dim]🔥 AI Code Review a PR[/dim]\n"
            f"  [green]analyze <owner/repo>[/green]        - [dim]AI health report[/dim]\n"
            f"  [green]digest[/green]                      - [dim]🌅 Daily GitHub Digest[/dim]\n"
            f"  [green]history[/green]                     - [dim]💬 View past questions[/dim]\n"
            f"  [green]ask <question>[/green]              - [dim]Ask Gemini anything[/dim]\n"
            f"  [green]exit[/green]                        - [dim]Quit[/dim]",
            title="🚀 Narad CLI",
            border_style="bright_blue"
        ))

    # ─── Display Helpers ──────────────────────────────────────────────────────

    def display_repos(self, repos):
        if isinstance(repos, str):
            console.print(f"[red]{repos}[/red]"); return
        table = Table(title="📦 Repositories", box=box.ROUNDED, border_style="blue")
        table.add_column("Repository", style="cyan", no_wrap=True)
        for repo in repos:
            table.add_row(repo)
        console.print(table)

    def display_commits(self, commits, repo=""):
        if isinstance(commits, str):
            console.print(f"[red]{commits}[/red]"); return
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
            console.print(f"[red]{items}[/red]"); return
        table = Table(title=title, box=box.ROUNDED, border_style="magenta")
        table.add_column("Name", style="cyan")
        for item in items:
            table.add_row(item)
        console.print(table)

    def display_prs(self, prs, repo=""):
        if isinstance(prs, str):
            console.print(f"[red]{prs}[/red]"); return
        if not prs:
            console.print("[green]✅ No open pull requests![/green]"); return
        table = Table(title=f"🔀 Open PRs: {repo}", box=box.ROUNDED, border_style="yellow")
        table.add_column("#", style="yellow", width=6)
        table.add_column("Title", style="white")
        table.add_column("Author", style="cyan", width=20)
        for pr in prs:
            table.add_row(str(pr['number']), pr['title'], pr['author'])
        console.print(table)

    def display_history(self, history):
        if not history:
            console.print("[dim]No conversation history yet in this session.[/dim]")
            return
        table = Table(title="💬 Conversation History", box=box.ROUNDED, border_style="dim")
        table.add_column("Role", style="cyan", width=12)
        table.add_column("Message", style="white")
        for h in history:
            role_label = "[green]You[/green]" if h['role'] == 'user' else "[blue]Narad[/blue]"
            table.add_row(role_label, h['message'][:120])
        console.print(table)

    # ─── Intent Parser ────────────────────────────────────────────────────────

    def parse_intent(self, user_input: str) -> dict:
        prompt = INTENT_PROMPT.format(message=user_input)
        response = self.gemini.generate_response(
            prompt,
            system_instruction="You are a JSON command parser. Return ONLY valid JSON. No markdown."
        )
        response = response.strip().strip("```json").strip("```").strip()
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"cmd": "ask", "question": user_input}

    # ─── Command Executor ────────────────────────────────────────────────────

    async def execute_command(self, parsed: dict, original_input: str):
        cmd = parsed.get("cmd", "ask")

        # Save user message to memory
        db.save_message(self.session_id, "user", original_input)

        if cmd == "repos":
            username = parsed.get("username")
            label = username or self.me
            with console.status(f"[bold green]Fetching repos for [cyan]{label}[/cyan]..."):
                repos = self.github.get_user_repositories(username)
            self.display_repos(repos)

        elif cmd == "commits":
            repo = parsed.get("repo")
            limit = parsed.get("limit", 5)
            if not repo:
                console.print("[yellow]Please specify a repo: commits Edge-Explorer/Narad-GitHub-Agent[/yellow]")
                return
            with console.status(f"[bold green]Fetching commits for [cyan]{repo}[/cyan]..."):
                commits = self.github.get_recent_commits(repo, limit)
            self.display_commits(commits, repo)

        elif cmd == "branches":
            repo = parsed.get("repo")
            with console.status(f"[bold green]Fetching branches for [cyan]{repo}[/cyan]..."):
                branches = self.github.list_branches(repo)
            self.display_list(f"🌿 Branches: {repo}", branches)

        elif cmd == "prs":
            repo = parsed.get("repo")
            with console.status(f"[bold yellow]Fetching open PRs for [cyan]{repo}[/cyan]..."):
                prs = self.github.list_open_prs(repo)
            self.display_prs(prs, repo)

        elif cmd == "review_pr":
            repo = parsed.get("repo")
            pr_number = parsed.get("pr_number")
            if not repo or not pr_number:
                console.print("[yellow]Usage: review pr <owner/repo> <pr#>[/yellow]")
                return
            with console.status(f"[bold red]🔍 Fetching PR #{pr_number} from [cyan]{repo}[/cyan]..."):
                pr_data = self.github.get_pull_request_diff(repo, int(pr_number))
            if "error" in pr_data:
                console.print(f"[red]{pr_data['error']}[/red]"); return
            with console.status("[bold cyan]🤖 Gemini is reviewing the code..."):
                review = self.gemini.review_pull_request(pr_data)
                db.save_pr_review(repo, pr_data['number'], pr_data['title'], review)
            console.print(Panel(
                review,
                title=f"🔥 AI Code Review: PR #{pr_data['number']} — {pr_data['title']}",
                border_style="red"
            ))
            db.save_message(self.session_id, "assistant", f"Reviewed PR #{pr_number} in {repo}")

        elif cmd == "analyze":
            repo = parsed.get("repo")
            with console.status(f"[bold cyan]Running AI analysis on [green]{repo}[/green]..."):
                readme = self.github.get_repo_readme(repo)
                commits = self.github.get_recent_commits(repo, limit=10)
                activity = "\n".join([f"- {c['sha']}: {c['message']}" for c in commits]) if isinstance(commits, list) else "N/A"
                result = self.gemini.analyze_repo_health(repo, readme, activity)
            console.print(Panel(result, title=f"🧠 AI Analysis: {repo}", border_style="cyan"))
            db.save_message(self.session_id, "assistant", f"Analyzed repo: {repo}")

        elif cmd == "digest":
            with console.status("[bold yellow]🌅 Gathering your GitHub activity..."):
                data = self.github.get_daily_digest_data()
            with console.status("[bold cyan]✍️ Gemini is writing your Daily Digest..."):
                digest = self.gemini.generate_daily_digest(data)
                db.save_digest(digest)
            console.print(Panel(digest, title=f"🌅 Daily GitHub Digest — {datetime.now().strftime('%A, %d %b %Y')}", border_style="yellow"))
            db.save_message(self.session_id, "assistant", "Generated daily digest")

        elif cmd == "history":
            history = db.get_recent_history(self.session_id, limit=20)
            self.display_history(history)

        elif cmd == "ask":
            question = parsed.get("question", original_input)
            history = db.get_recent_history(self.session_id, limit=6)
            with console.status("[bold cyan]Asking Gemini..."):
                if history:
                    answer = self.gemini.generate_with_memory(question, history)
                else:
                    answer = self.gemini.generate_response(question)
            console.print(Panel(answer, title="🤖 Gemini Says", border_style="cyan"))
            db.save_message(self.session_id, "assistant", answer[:500])

        elif cmd == "exit":
            raise SystemExit

        else:
            console.print(f"[yellow]Unknown command. Try rephrasing![/yellow]")

    # ─── Main Loop ───────────────────────────────────────────────────────────

    async def run(self):
        self.show_welcome()

        # Show last digest if exists
        last = db.get_last_digest()
        if last:
            console.print(f"\n[dim]💾 Last digest available from {last['timestamp'][:10]}. Type [bold]digest[/bold] to regenerate.[/dim]")

        while True:
            try:
                user_input = Prompt.ask("\n[bold green]➜[/bold green]")
                if user_input.lower() in ['exit', 'quit']:
                    console.print("[yellow]Goodbye! Keep building! 🚀[/yellow]")
                    break

                with console.status("[dim]Parsing intent...[/dim]"):
                    parsed = self.parse_intent(user_input)

                await self.execute_command(parsed, user_input)

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
