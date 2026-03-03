# Narad GitHub Agent 🚀🤖

### A Premium CLI & MCP Server Powered by Gemini 2.0 Flash

The **Narad GitHub Agent** is a next-generation, dual-mode intelligent agent engineered for seamless high-level interactions with GitHub. It can operate as an **interactive CLI chat agent** you talk to directly, or as a **Model Context Protocol (MCP) server** that integrates with AI-powered IDEs and tools.

Powered by **Gemini 2.0 Flash**, it transforms complex repository tasks into simple, conversational agentic interactions.

---

## ✨ Key Features

- **💬 Interactive CLI Mode**: Talk to the agent directly in your terminal. Ask questions, get commits, analyze repos — all in real time.
- **🌐 MCP Server Mode**: Seamlessly integrates with AI IDEs (like VS Code + Antigravity, Claude Desktop) via the Model Context Protocol.
- **⚡ Gemini 2.0 Flash**: State-of-the-art reasoning for summarizing codebases, analyzing project health, and interpreting repository data.
- **🛠️ Rich GitHub Toolbelt**:
  - Repository listing and discovery
  - Recent commit history analysis
  - AI-powered Repository Health Report
  - Read specific files from any branch
  - Search code across all of GitHub
  - List and manage branches
  - Create issues
- **🔐 Security First**: Strict `.gitignore` with `.env` isolation. Your tokens and API keys are never pushed to GitHub.
- **📦 Clean Architecture**: Pydantic Settings for validation, structured logging, and modular tool design.

---

## 🛠️ Tech Stack

| Technology | Role |
|---|---|
| **Gemini 2.0 Flash** | AI Reasoning & Analysis Engine |
| **FastMCP** | Model Context Protocol Server |
| **PyGitHub** | GitHub REST API Integration |
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
│       ├── tools/
│       │   └── github_tools.py  # All GitHub API interactions
│       └── agents/
│           └── gemini_agent.py  # Gemini 2.0 Flash Reasoning Engine
├── tests/                   # Quality assurance suite
├── .env                     # 🔒 Secrets (Ignored by git)
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
Run this to talk to Narad directly in your terminal:
```powershell
python src/main.py --cli
```

#### 🌐 MCP Server Mode (Connect to AI IDE)
Run this to expose Narad as an MCP server for tools like Claude Desktop or VS Code:
```powershell
python src/main.py
```

---

## 🧰 Available MCP Tools

| Tool | Description |
|---|---|
| `list_repositories` | List repos for you or any GitHub user |
| `get_commits` | Fetch recent commit history for a repo |
| `analyze_repository` | 🧠 AI-powered health & activity report |
| `read_file` | Read any file from any branch |
| `search_github_code` | Search code across all of GitHub |
| `list_repo_branches` | List all branches in a repository |
| `ask_gemini_github` | Ask Gemini any GitHub/dev question |

---

## 🔒 Security & Best Practices

- **Credentials are protected**: `.env` is git-ignored and can never be pushed.
- **Least Privilege**: Use only the GitHub token scopes you need (`repo` is enough to start).
- **Modular Design**: Tools are decoupled from the server — easy to extend.
- **Validated Config**: Pydantic Settings auto-validates all environment variables on startup.

---

## 🤝 About

**Narad GitHub Agent** — Re-engineered from the ground up with a focus on security, modularity, and AI-first design.

Built as part of the **Narad AI Ecosystem** — a family of modular, premium AI agents.

---
*© 2026 Edge-Explorer · Narad AI Ecosystem*
