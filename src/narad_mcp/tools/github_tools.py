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
        # Cache authenticated user from token — no need to pass username manually
        self._me = self.gh.get_user()

    def get_authenticated_username(self):
        """Return the GitHub login of the authenticated user."""
        return self._me.login

    def get_user_repositories(self, username=None):
        """List repositories. If no username given, uses the authenticated token owner."""
        try:
            if username:
                user = self.gh.get_user(username)
                repos = user.get_repos()
            else:
                # Use authenticated user — gets ALL repos including private
                repos = self._me.get_repos(affiliation='owner,collaborator,organization_member')
            
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

    def get_user_profile(self, username: str = None) -> dict:
        """
        Get a comprehensive profile overview of a GitHub user.
        Returns bio, stats, and top repos sorted by stars.
        """
        try:
            user = self.gh.get_user(username) if username else self._me
            repos = sorted(user.get_repos(), key=lambda r: r.stargazers_count, reverse=True)[:10]
            return {
                "login": user.login,
                "name": user.name,
                "bio": user.bio,
                "location": user.location,
                "public_repos": user.public_repos,
                "followers": user.followers,
                "following": user.following,
                "html_url": user.html_url,
                "top_repos": [
                    {
                        "name": r.full_name,
                        "stars": r.stargazers_count,
                        "language": r.language,
                        "description": r.description,
                    }
                    for r in repos
                ]
            }
        except GithubException as e:
            return f"GitHub Error: {e.data.get('message', str(e))}"
        except Exception as e:
            return f"Error fetching profile: {str(e)}"

    def get_pull_request_diff(self, full_repo_name: str, pr_number: int) -> dict:
        """Fetch a PR's metadata and its full diff for AI review."""
        try:
            repo = self.gh.get_repo(full_repo_name)
            pr = repo.get_pull(pr_number)
            files = pr.get_files()
            
            diff_summary = []
            for f in files:
                patch = f.patch if f.patch else "[Binary or too large]"
                diff_summary.append(f"### {f.filename} ({f.status})\n```diff\n{patch[:2000]}\n```")
            
            return {
                "number": pr.number,
                "title": pr.title,
                "author": pr.user.login,
                "state": pr.state,
                "body": pr.body or "No description.",
                "files_changed": pr.changed_files,
                "additions": pr.additions,
                "deletions": pr.deletions,
                "diff": "\n\n".join(diff_summary)
            }
        except GithubException as e:
            return {"error": f"GitHub Error: {e.data.get('message', str(e))}"}
        except Exception as e:
            return {"error": f"Error fetching PR: {str(e)}"}

    def list_open_prs(self, full_repo_name: str) -> list:
        """List open pull requests for a repository."""
        try:
            repo = self.gh.get_repo(full_repo_name)
            prs = repo.get_pulls(state='open')
            return [{"number": pr.number, "title": pr.title, "author": pr.user.login} for pr in prs]
        except GithubException as e:
            return f"GitHub Error: {e.data.get('message', str(e))}"
        except Exception as e:
            return f"Error fetching PRs: {str(e)}"

    def get_daily_digest_data(self) -> dict:
        """
        Aggregate recent activity across your most active repos for the Daily Digest.
        Returns commit activity and open PRs for your top repos.
        """
        try:
            repos = list(self._me.get_repos(affiliation='owner')[:10])
            digest_data = []
            for repo in repos:
                commits = list(repo.get_commits()[:3])
                prs = list(repo.get_pulls(state='open'))
                digest_data.append({
                    "repo": repo.full_name,
                    "stars": repo.stargazers_count,
                    "open_prs": len(prs),
                    "recent_commits": [
                        {"sha": c.sha[:7], "msg": c.commit.message.split('\n')[0]}
                        for c in commits
                    ]
                })
            return {"repos": digest_data, "username": self._me.login}
        except Exception as e:
            return {"error": str(e)}
