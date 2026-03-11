# Narad GitHub Agent 🚀🤖

### A Premium CLI & MCP Server Powered by Gemini 2.0 Flash

The **Narad GitHub Agent** is a next-generation, dual-mode intelligent agent engineered for seamless high-level interactions with GitHub. It operates as an **interactive CLI chat agent** you can talk to directly, or as a **Model Context Protocol (MCP) server** that integrates with AI-powered IDEs and tools.

Powered by **Gemini 2.0 Flash**, it transforms complex repository tasks into simple conversational interactions — with **conversation memory**, **AI code reviews**, and a **daily digest** of your GitHub activity.

> **Fully Dynamic**: The agent uses whoever's `GITHUB_TOKEN` is in `.env`. Clone it, put your own token in, and it works 100% for your account — no code changes needed.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| **💬 Interactive CLI Mode** | Chat with the agent directly in your terminal using natural language |
| **🌐 MCP Server Mode** | Integrate with AI IDEs (VS Code + Antigravity, Claude Desktop) via MCP |
| **🧠 Conversation Memory** | Every session is stored in a local SQLite DB — Gemini remembers context |
| **🔥 PR Code Reviewer** | Fetch a PR's diff and get an expert AI code review (bugs, security, rating) |
| **🌅 Daily Digest** | AI-written morning report of activity across all your repos |
| **👤 Profile Overview** | View any GitHub user's bio, stats, and top repos with an **AI Developer Summary** |
| **⚡ Gemini 2.0 Flash** | Reasoning engine for repo health, code analysis, and GitHub Q&A |
| **🔐 Security First** | `.env` is git-ignored. Your token is never pushed to GitHub |
| **📦 Clean Architecture** | Pydantic Settings, structured logging, modular tool design |

---

## 🛠️ Tech Stack

| Technology | Role |
|---|---|
| **Gemini 2.0 Flash** | AI Reasoning & Analysis Engine |
| **FastMCP** | Model Context Protocol Server |
| **PyGitHub** | GitHub REST API Integration |
| **SQLite (stdlib)** | Local DB for conversation memory, PR reviews & digests |
| **Pydantic Settings** | Config Management & Validation |
| **Rich** | Beautiful Terminal UI/CLI |
| **Python 3.10+** | Core Language |
| **venv** | Isolated Dependency Management |

---

## 📁 Project Structure

```text
Narad-GitHub-Agent/
├── src/
│   ├── main.py              # Dual entry point: CLI or MCP Server
│   └── narad_mcp/
│       ├── config.py        # Pydantic Settings & Config
│       ├── server.py        # FastMCP Server with all tools
│       ├── cli.py           # Rich Interactive CLI Agent
│       ├── database.py      # SQLite layer (memory, PR reviews, digests)
│       ├── tools/
│       │   └── github_tools.py  # All GitHub API interactions
│       └── agents/
│           └── gemini_agent.py  # Gemini 2.0 Flash Reasoning Engine
├── tests/                   # Quality assurance suite
├── narad_agent.db           # 🔒 Local SQLite DB (auto-created, git-ignored)
├── .env                     # 🔒 Secrets (git-ignored, never pushed)
├── .env.example             # Credential Template for setup
├── .gitignore               # Strict security rules
└── requirements.txt         # Modern dependencies
```

---

## 🚀 Quick Start

### 1. Prerequisites
Ensure you have **Python 3.10+** installed and your API keys ready.

### 2. Clone & Setup Environment
```powershell
# Clone the repo
git clone https://github.com/Edge-Explorer/Narad-GitHub-Agent.git
cd Narad-GitHub-Agent

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Credentials
Create a `.env` file by copying the example:
```powershell
copy .env.example .env
```
Then fill in your keys:
```env
GITHUB_TOKEN="your_github_personal_access_token"
GEMINI_API_KEY="your_gemini_api_key"
```

> **Getting a GitHub Token**: Go to [GitHub Settings → Developer Settings → Personal Access Tokens](https://github.com/settings/tokens) and create a token with **`repo`** scope.
>
> **Getting a Gemini API Key**: Visit [Google AI Studio](https://aistudio.google.com/) to generate your free Gemini API key.

### 4. Run the Agent

#### 💬 Interactive CLI Mode (Chat with the Agent)
```powershell
python src/main.py --cli
```

#### 🌐 MCP Server Mode (Connect to AI IDE)
```powershell
python src/main.py
```

---

## 🧰 CLI Commands

You can type **natural language** or use the keywords below:

| Command | What it does |
|---|---|
| `repos` | List **your** repositories (auto-detected from token) |
| `repos <username>` | List any GitHub user's public repos |
| `profile` | Your full GitHub profile: bio, stats, top repos |
| `profile <username>` | Any user's full profile & top repos |
| `commits <owner/repo>` | Recent commit history for a repo |
| `branches <owner/repo>` | List all branches |
| `prs <owner/repo>` | List open Pull Requests |
| `review pr <owner/repo> <#>` | 🔥 AI Code Review of a specific PR |
| `analyze <owner/repo>` | 🧠 AI repo health report + score out of 10 |
| `digest` | 🌅 Generate today's Daily GitHub Digest |
| `history` | View your current session's conversation history |
| `ask <question>` | Ask Gemini any GitHub or coding question |
| `exit` | Quit the agent |

### Natural Language Examples
```
show me my repos
give me commits from Edge-Explorer/Narad-GitHub-Agent
analyze my Narad project
what are the open PRs in Edge-Explorer/Narad-MCP-Server
review pr Edge-Explorer/my-project 3
give me today's digest
what is a pull request?
```

---

## 🗄️ Local SQLite Database

The agent automatically creates `narad_agent.db` to persist data locally:

| Table | Stores |
|---|---|
| `conversation_history` | All questions & answers per session (with session ID) |
| `pr_reviews` | Full AI code reviews with repo, PR number & timestamp |
| `daily_digests` | All generated daily digests, so you can compare over time |

> The database file is **git-ignored** and stays only on your machine.

---

## 🔒 Security & Best Practices

- **Your token is 100% dynamic**: The agent reads `GITHUB_TOKEN` from `.env` at startup. If you change the token, it uses the new one automatically. No code changes needed.
- **Token never leaks**: `.env` and `*.db` are strictly in `.gitignore` — they will never be pushed to GitHub.
- **Anyone can clone this**: A new user clones the repo, adds their own `.env` with their credentials, and the agent will work for their GitHub account — not yours.
- **Least Privilege**: Only the GitHub token scopes you need (`repo` is enough for all features).
- **Validated Config**: Pydantic Settings validates all environment variables on startup — it fails fast with a clear error if a key is missing.

---

## 🧰 MCP Tools (Server Mode)

When running as an MCP Server, these tools are exposed to your AI IDE:

| Tool | Description |
|---|---|
| `list_repositories` | List repos for you or any GitHub user |
| `get_commits` | Fetch recent commit history |
| `analyze_repository` | AI-powered health & activity report |
| `read_file` | Read any file from any branch |
| `search_github_code` | Search code across all of GitHub |
| `list_repo_branches` | List all branches |
| `ask_gemini_github` | Ask Gemini any GitHub/dev question |

---

## 🤝 About

**Narad GitHub Agent** — Re-engineered from the ground up with a focus on security, modularity, AI-first design, and genuine day-to-day developer utility.

Built as part of the **Narad AI Ecosystem** — a family of modular, premium AI agents.

---

## 📜 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---
*© 2026 Edge-Explorer · Narad AI Ecosystem*
