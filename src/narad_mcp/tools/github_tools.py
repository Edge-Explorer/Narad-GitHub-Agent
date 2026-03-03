import os
import logging
from github import Github, GithubException
from narad_mcp.config import settings

# Configure logging
logger = logging.getLogger(__name__)

class GitHubTools:
    def __init__(self, token=None):
        self.token = token or settings.github_token
        if not self.token:
            raise ValueError("GITHUB_TOKEN not found in configuration")
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
        except GithubException as e:
            logger.error(f"GitHub Error: {e.data.get('message', str(e))}")
            return f"GitHub Error: {e.data.get('message', str(e))}"
        except Exception as e:
            logger.error(f"Unexpected Error: {str(e)}")
            return f"Error fetching repositories: {str(e)}"

    def get_recent_commits(self, full_repo_name, limit=None):
        """Fetch recent commits for a repository."""
        limit = limit or settings.default_commit_limit
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
        except GithubException as e:
            return f"GitHub Error: {e.data.get('message', str(e))}"
        except Exception as e:
            return f"Error fetching commits: {str(e)}"

    def create_issue(self, full_repo_name, title, body=""):
        """Create a new issue in a repository."""
        try:
            repo = self.gh.get_repo(full_repo_name)
            issue = repo.create_issue(title=title, body=body)
            return {"number": issue.number, "url": issue.html_url}
        except GithubException as e:
            return f"GitHub Error: {e.data.get('message', str(e))}"
        except Exception as e:
            return f"Error creating issue: {str(e)}"

    def get_repo_readme(self, full_repo_name):
        """Get the README content of a repository."""
        try:
            repo = self.gh.get_repo(full_repo_name)
            readme = repo.get_readme()
            return readme.decoded_content.decode("utf-8")
        except GithubException as e:
            return f"GitHub Error: {e.data.get('message', str(e))}"
        except Exception as e:
            return f"Error fetching README: {str(e)}"

    def get_file_content(self, full_repo_name, file_path, branch="main"):
        """Read the content of a specific file."""
        try:
            repo = self.gh.get_repo(full_repo_name)
            content = repo.get_contents(file_path, ref=branch)
            return content.decoded_content.decode("utf-8")
        except GithubException as e:
            return f"GitHub Error: {e.data.get('message', str(e))}"
        except Exception as e:
            return f"Error fetching file: {str(e)}"

    def list_branches(self, full_repo_name):
        """List all branches in a repository."""
        try:
            repo = self.gh.get_repo(full_repo_name)
            branches = repo.get_branches()
            return [b.name for b in branches]
        except GithubException as e:
            return f"GitHub Error: {e.data.get('message', str(e))}"
        except Exception as e:
            return f"Error fetching branches: {str(e)}"

    def search_code(self, query):
        """Search code across GitHub."""
        try:
            results = self.gh.search_code(query=query)
            return [f"{res.repository.full_name}: {res.path}" for res in results[:10]]
        except GithubException as e:
            return f"GitHub Error: {e.data.get('message', str(e))}"
        except Exception as e:
            return f"Error searching code: {str(e)}"
