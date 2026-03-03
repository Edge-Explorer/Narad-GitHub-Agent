import os
from github import Github
from dotenv import load_dotenv

load_dotenv()

class GitHubTools:
    def __init__(self, token=None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GITHUB_TOKEN not found in environment")
        self.gh = Github(self.token)

    def get_user_repositories(self, username=None):
        """List repositories for a user. If username is None, lists repos for the authenticated user."""
        try:
            if username:
                user = self.gh.get_user(username)
                repos = user.get_repos()
            else:
                user = self.gh.get_user()
                repos = user.get_repos()
            
            return [repo.full_name for repo in repos]
        except Exception as e:
            return f"Error fetching repositories: {str(e)}"

    def get_recent_commits(self, full_repo_name, limit=5):
        """Fetch recent commits for a repository."""
        try:
            repo = self.gh.get_repo(full_repo_name)
            commits = repo.get_commits()[:limit]
            result = []
            for commit in commits:
                result.append({
                    "sha": commit.sha[:7],
                    "author": commit.commit.author.name,
                    "date": commit.commit.author.date.isoformat(),
                    "message": commit.commit.message
                })
            return result
        except Exception as e:
            return f"Error fetching commits: {str(e)}"

    def create_issue(self, full_repo_name, title, body=""):
        """Create a new issue in a repository."""
        try:
            repo = self.gh.get_repo(full_repo_name)
            issue = repo.create_issue(title=title, body=body)
            return {"number": issue.number, "url": issue.html_url}
        except Exception as e:
            return f"Error creating issue: {str(e)}"

    def get_repo_readme(self, full_repo_name):
        """Get the README content of a repository."""
        try:
            repo = self.gh.get_repo(full_repo_name)
            readme = repo.get_readme()
            return readme.decoded_content.decode("utf-8")
        except Exception as e:
            return f"Error fetching README: {str(e)}"
