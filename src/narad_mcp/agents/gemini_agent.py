from google import genai
from google.genai import types
from datetime import datetime
from narad_mcp.config import settings

class GeminiAgent:
    def __init__(self, api_key=None):
        api_key = api_key or settings.gemini_api_key.get_secret_value()
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in configuration")
        
        self.client = genai.Client(api_key=api_key)
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
        """Generate a response for a given prompt using Gemini 2.0 Flash."""
        instruction = system_instruction or self.base_system_instruction
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                config=types.GenerateContentConfig(system_instruction=instruction),
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Gemini API Error: {str(e)}"

    def generate_with_memory(self, user_message: str, history: list[dict]) -> str:
        """
        Generate a response that is aware of past conversation history.
        history = [{"role": "user"|"assistant", "message": "..."}]
        """
        context = "\n".join([
            f"{'User' if h['role'] == 'user' else 'Assistant'}: {h['message']}"
            for h in history
        ])
        prompt = f"""You have this conversation history with the user:
{context}

Now the user says: {user_message}

Respond naturally, referring to the conversation history where relevant."""
        return self.generate_response(prompt)

    def analyze_repo_health(self, repo_name: str, readme_content: str, commit_history: str) -> str:
        """AI health report for a repository."""
        prompt = f"""
        Analyze the health and quality of the repository '{repo_name}':
        
        README:
        {readme_content[:3000]}
        
        RECENT COMMITS:
        {commit_history}
        
        Evaluate project maturity, activity level, and documentation quality. Provide a score out of 10.
        """
        return self.generate_response(prompt)

    def review_pull_request(self, pr_data: dict) -> str:
        """
        Perform an expert AI code review of a pull request diff.
        """
        prompt = f"""
You are a senior software engineer performing a thorough code review.

## Pull Request: #{pr_data['number']} — {pr_data['title']}
**Author:** {pr_data['author']}  
**Description:** {pr_data.get('body', 'No description')}
**Stats:** +{pr_data['additions']} additions, -{pr_data['deletions']} deletions across {pr_data['files_changed']} files

## Code Changes:
{pr_data['diff'][:6000]}

---

Provide a professional code review covering:
1. ✅ **What's good** — Praise well-written code
2. 🐛 **Potential bugs** — Flag logical issues or edge cases
3. ⚡ **Performance** — Note any inefficiencies
4. 🔐 **Security** — Highlight any risks
5. 📝 **Suggestions** — Concrete improvements with examples
6. **Overall Rating**: X/10 with a brief verdict (Approve / Request Changes)
"""
        return self.generate_response(prompt, system_instruction="You are a senior code reviewer. Be direct, specific, and technically rigorous.")

    def generate_daily_digest(self, digest_data: dict) -> str:
        """
        Generate a formatted Daily Digest report from aggregated GitHub activity.
        """
        if "error" in digest_data:
            return f"Could not fetch digest data: {digest_data['error']}"

        repo_blocks = []
        for r in digest_data.get("repos", []):
            commits_str = "\n".join([
                f"  - [{c['sha']}] {c['msg']} ({c['date'][:10]})" 
                for c in r['recent_commits']
            ]) or "  No recent commits"
            repo_blocks.append(
                f"**{r['repo']}** ⭐{r['stars']} | 🔀 {r['open_prs']} open PRs\n{commits_str}"
            )

        prompt = f"""
Generate a concise and engaging **Daily GitHub Digest** for the developer @{digest_data['username']}.
TODAY'S DATE: {datetime.now().strftime('%Y-%m-%d %A')}

Here is their recent activity across their repositories:
{chr(10).join(repo_blocks)}

Instructions:
- Focus on activity from the **last 7 days**. If everything is older, summarize what was last touched.
- Start with a motivational one-liner.
- Summarize overall status in 2 sentences.
- Highlight the single most active repo this week.
- List any repos with open PRs needing attention.
- End with a task/tip for today based on the activity level (e.g., 'Quiet week, time to clean up tech debt!' or 'Heave push today, keep it up!').
"""
        return self.generate_response(prompt, system_instruction="You are a helpful daily standup assistant for developers. Be energetic, concise, and insightful.")

    def generate_user_summary(self, profile_data: dict) -> str:
        """
        Generate an AI-powered professional summary of a GitHub user based on their profile and top repos.
        """
        repos_str = "\n".join([
            f"- {r['name']} ({r['stars']} stars): {r['description'] or 'No description'}"
            for r in profile_data.get('top_repos', [])
        ])
        
        prompt = f"""
        Analyze the following GitHub profile and provide a professional summary of the developer's focus, 
        tech stack, and expertise:

        USER: {profile_data['login']}
        NAME: {profile_data.get('name', 'N/A')}
        BIO: {profile_data.get('bio', 'N/A')}
        LOCATION: {profile_data.get('location', 'N/A')}
        STATS: {profile_data['public_repos']} repos, {profile_data['followers']} followers

        TOP REPOSITORIES:
        {repos_str}

        Format:
        1. **Expertise Overview**: 2-3 sentences.
        2. **Core Tech Stack**: Based on their repos.
        3. **Notable Projects**: Highlight 1-2 key repos.
        4. **Verdict**: A friendly "developer persona" (e.g., 'The Backend Architect' or 'The Python Enthusiast').
        """
        return self.generate_response(prompt, system_instruction="You are a talent scout and technical analyst. Be professional, observant, and encouraging.")
