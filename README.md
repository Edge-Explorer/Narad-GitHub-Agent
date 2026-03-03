# Narad GitHub Agent 🚀🤖

### A Premium CLI MCP Server Powered by Gemini 2.0 Flash

The **Narad GitHub Agent** is a next-generation, modular Model Context Protocol (MCP) server engineered to provide seamless high-level interactions with GitHub. Leveraging the lightning-fast reasoning of **Gemini 2.0 Flash**, it transforms complex repository tasks into simple, agentic tool calls.

---

## ✨ Key Features

- **🌐 MCP Native**: Built on the Model Context Protocol for universal AI tool integration.
- **⚡ Gemini 2.0 Flash**: State-of-the-art reasoning for summarizing codebases and interpreting repository data.
- **🛠️ GitHub Toolbelt**: 
  - Effortless repository listing and discovery.
  - Deep commit history analysis.
  - Automated issue creation and management.
  - AI-powered README interpretation and repository explanation.
- **🔐 Security First**: Zero-trust approach to credentials with strict `.gitignore` and `.env` isolation.

---

## 🛠️ Tech Stack

- **Reasoning**: Gemini 2.0 Flash (Experimental)
- **Framework**: Model Context Protocol (FastMCP)
- **Language**: Python 3.10+
- **APIs**: GitHub REST API (via PyGitHub)
- **Environment**: Virtual Environment (Venv)

---

## 📁 Project Structure

```text
Narad-GitHub-Agent/
├── src/
│   └── narad_mcp/
│       ├── tools/       # GitHub API tool logic
│       ├── agents/      # Gemini reasoning engine
│       └── server.py    # Main MCP server entry point
├── tests/               # Quality assurance suite
├── .env                 # Secrets (Ignored)
└── requirements.txt     # Modern dependencies
```

---

## 🚀 Quick Start

### 1. Prerequisites
Ensure you have Python 3.10+ installed and your API keys ready (GitHub & Gemini).

### 2. Setup Environment
```powershell
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file based on the `.env.example`:
```env
GITHUB_TOKEN="your_personal_access_token"
GEMINI_API_KEY="your_gemini_api_key_here"
```

### 4. Launch the Server
```powershell
python src/narad_mcp/server.py
```

---

## 🔒 Security & Best Practices

- **Avoid Credential Leaks**: Never push your `.env` to GitHub. The project includes a pre-configured `.gitignore`.
- **Modular Design**: Tools are decoupled from the server logic, making it easy to extend for GitLab or Bitbucket.
- **Audit Logs**: (Coming Soon) Detailed logging for all agentic actions.

---

## 🤝 Contribution
Re-engineered with ❤️ by Antigravity. Let's build the future of agentic coding together!

---
*Narad AI Ecosystem 2026*
