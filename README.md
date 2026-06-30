# 🔨 HackForge AI — Multi-Agent Hackathon Copilot

<div align="center">

**An AI-powered hackathon project co-pilot that deploys a team of 11 specialized AI agents to forge complete hackathon blueprints end-to-end.**

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal?style=for-the-badge&logo=fastapi)
![Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-Powered-orange?style=for-the-badge&logo=google)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

</div>

---

## 🚀 What is HackForge AI?

HackForge AI is a **multi-agent AI system** built on Google Gemini that takes your hackathon problem statement and autonomously produces a complete, competition-ready project blueprint in minutes.

### 11 Specialized AI Agents

| # | Agent | Role |
|---|-------|------|
| 1 | 🧭 **Planner** | Analyzes input & coordinates execution order |
| 2 | 💡 **Idea Generation** | Brainstorms 3+ ideas, scores by innovation & feasibility |
| 3 | 🔍 **Research** | Google Search-grounded competitor analysis |
| 4 | 🗃️ **Dataset Discovery** | Finds Kaggle/HuggingFace datasets & APIs |
| 5 | ⚙️ **Technology Advisor** | Recommends full-stack tech with rationale |
| 6 | 🏗️ **System Architecture** | Mermaid.js system diagrams + data flow |
| 7 | 📅 **Development Planner** | Milestone roadmap with hour estimates |
| 8 | 📄 **README Generator** | GitHub-ready README.md |
| 9 | 📣 **Pitch Generator** | Slides outline, demo script, elevator pitch |
| 10 | 🛡️ **Submission Reviewer** | Quality audit & consistency checks |
| 11 | 👔 **Project Manager** | Final unified blueprint + executive summary |

---

## 🏛️ Architecture

```
                    ┌──────────────────────────────────────────┐
                    │          HackForge AI System             │
                    │                                          │
  Browser ──────►   │  FastAPI Backend        SQLite DB        │
  (HTML/CSS/JS)     │    main.py         ◄─── db_manager.py    │
                    │       │                                  │
                    │       ▼                                  │
                    │  workflow.py (Orchestrator)              │
                    │       │                                  │
                    │  ┌────┴───────────────────────────────┐  │
                    │  │         Agent Pipeline             │  │
                    │  │                                    │  │
                    │  │  Planner ──► [Idea Gen + Research] │  │
                    │  │             ──► [Datasets + Tech   │  │
                    │  │                  + Pitch]          │  │
                    │  │                  ──► [Arch + Dev]  │  │
                    │  │                     ──► [README +  │  │
                    │  │                           Review]  │  │
                    │  │                          ──► PM    │  │
                    │  └────────────────────────────────────┘  │
                    │                                          │
                    │  All agents powered by Gemini 2.5 Flash  │
                    └──────────────────────────────────────────┘
```

### Parallel Execution

Agents are orchestrated using `asyncio.gather()` for maximum throughput:

- **Step 1** (sequential): Planner analyzes input
- **Step 2** (parallel): Idea Gen + Research
- **Step 3** (parallel): Datasets + Tech Advisor + Pitch Generator  
- **Step 4** (parallel): System Architecture + Dev Planner
- **Step 5** (parallel): README Generator + Submission Reviewer
- **Step 6** (sequential): Project Manager synthesizes everything

---

## 📦 Installation

### Prerequisites
- Python 3.11+
- A [Google Gemini API key](https://aistudio.google.com/)

### Setup

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd ClgMail

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
copy .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 5. Start the server
python run.py
```

### Open in Browser
Navigate to **http://127.0.0.1:8000**

---

## 🔑 API Key Configuration

You have two options for providing the Gemini API key:

**Option A — Environment Variable (recommended for server deployments):**
```bash
# In .env file:
GEMINI_API_KEY=your_key_here
```

**Option B — Browser Settings (recommended for shared deployments):**
1. Click the ⚙️ **Gemini Settings** button in the sidebar
2. Enter your Gemini API key
3. The key is stored only in your browser's LocalStorage (never on the server DB)

---

## 🖥️ Usage

1. **Forge New Project**: Click "Forge Project" in the sidebar
2. **Fill in Parameters**:
   - Hackathon Name (optional)
   - Theme/Domain (optional)
   - **Problem Statement** (required) — be descriptive!
   - Constraints (optional)
   - Preferred Technologies (optional)
3. **Watch Live Execution**: The workflow graph animates in real-time as each agent completes
4. **Review Blueprint**: Navigate through 11+ sections using the sidebar tabs

---

## 📁 Project Structure

```
ClgMail/
├── run.py                          # Entry point
├── .env.example                    # Environment template
├── requirements.txt                # Python dependencies
├── hackforge.db                    # SQLite database (auto-created)
├── backend/
│   ├── main.py                     # FastAPI app & routes
│   ├── agents/
│   │   ├── base_agent.py           # Base LLM wrapper (two-pass grounding)
│   │   ├── planner.py              # Planner Agent
│   │   ├── idea_gen.py             # Idea Generation Agent
│   │   ├── research.py             # Research Agent (Google Search grounded)
│   │   ├── dataset.py              # Dataset Discovery Agent
│   │   ├── tech_advisor.py         # Technology Advisor Agent
│   │   ├── architecture.py         # System Architecture Agent
│   │   ├── dev_planner.py          # Development Planner Agent
│   │   ├── readme_gen.py           # README Generator Agent
│   │   ├── pitch_gen.py            # Pitch Generator Agent
│   │   ├── reviewer.py             # Submission Review Agent
│   │   └── pm.py                   # Project Manager Agent
│   ├── orchestration/
│   │   └── workflow.py             # Async multi-agent orchestrator
│   └── db/
│       └── db_manager.py           # SQLite CRUD operations
└── static/
    ├── index.html                  # Single-page application
    ├── style.css                   # Dark glassmorphism theme
    └── app.js                      # Frontend logic & polling
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI + Uvicorn |
| **AI** | Google Gemini 2.5 Flash |
| **AI SDK** | google-genai Python SDK |
| **Database** | SQLite (via Python stdlib) |
| **Frontend** | Vanilla HTML/CSS/JavaScript |
| **Markdown** | marked.js |
| **Diagrams** | Mermaid.js |
| **Icons** | FontAwesome 6 |

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/projects` | List all projects |
| `POST` | `/api/projects` | Create & run new project |
| `GET` | `/api/projects/{id}` | Get project details + artifacts |
| `DELETE` | `/api/projects/{id}` | Delete a project |

### Create Project Request Body
```json
{
  "name": "My Hackathon",
  "theme": "Sustainability",
  "problem_statement": "Build an AI tool that monitors energy consumption...",
  "constraints": "Must run on mobile",
  "tech_preferences": "Python, React Native, Gemini API"
}
```

---

## 🧠 Key Design Decisions

### Two-Pass Grounding (Google Search + JSON Schema)
The Gemini API does **not** allow simultaneous use of Google Search grounding (tool use) AND structured JSON output (`response_mime_type=application/json`). HackForge AI solves this with a **two-pass approach**:
- **Pass 1**: Grounded search returns free-form text with real web results
- **Pass 2**: A second LLM call structures the grounded text into strict JSON schema

### Async Parallel Execution
Agents that have no dependencies on each other run in parallel via `asyncio.gather()`, cutting total execution time significantly versus a fully sequential pipeline.

---

## 📄 License

MIT License — feel free to use, modify, and distribute.
