# 🤖 HelpDeskAI

> An AI-powered internal IT Support Agent — a portfolio/demo project demonstrating agentic AI, LangGraph workflows, FastAPI, React, and SQLite.

---

## 📋 Problem

Internal IT teams spend significant time triaging and routing support tickets for common, repetitive issues. Employees waste time waiting for responses to issues that could be resolved with guided self-service troubleshooting.

## 💡 Solution

HelpDeskAI is an AI agent that:
1. Understands employee-reported IT issues in natural language
2. Classifies the issue category and severity automatically
3. Searches a local knowledge base for relevant troubleshooting procedures
4. Asks targeted diagnostic questions one at a time
5. Records diagnostic steps and outcomes
6. Determines if the issue is resolved
7. If unresolved, **automatically creates a real IT support ticket** in the database
8. Allows employees to track their ticket history

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   React + Vite Frontend              │
│  ChatInterface │ AgentActivity │ TicketPanel         │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP (REST API)
                       ▼
┌─────────────────────────────────────────────────────┐
│                 FastAPI Backend                      │
│  POST /api/chat  │  GET /api/tickets                 │
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │           LangGraph Agent Workflow             │  │
│  │                                                │  │
│  │  classify_issue → retrieve_knowledge           │  │
│  │       → ask_diagnostic_question               │  │
│  │       → process_user_response                 │  │
│  │       → [resolved | create_ticket]            │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  Tools: search_kb | record_diagnostic | create_ticket│
└──────────────────────┬──────────────────────────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
      SQLite DB   Knowledge Base  Gemini API
      (tickets)   (Markdown files) (LLM)
```

---

## 🔄 Agent Workflow

```
START
  ↓
classify_issue         ← LLM classifies category + severity
  ↓
retrieve_knowledge     ← Loads matching .md troubleshooting guide
  ↓
ask_diagnostic_question ← LLM generates targeted question
  ↓ (waits for user reply)
process_user_response  ← Records diagnostic, checks resolution
  ↓
  ┌──────────────────────┐
  │                      │
Resolved           Unresolved (max 5 attempts)
  │                      │
  ↓                      ↓
"Issue resolved!"   create_ticket (SQLite)
                         ↓
                    Returns IT-XXXX ticket ID
```

---

## 🛠️ Tools

| Tool | Description |
|------|-------------|
| `search_knowledge_base(query, category)` | Searches local `.md` troubleshooting docs, returns relevant content |
| `record_diagnostic(step, result, steps)` | Records a diagnostic step and its outcome in agent state |
| `create_ticket(...)` | Persists an IT ticket to SQLite, returns `IT-XXXX` ID |
| `get_ticket(ticket_id)` | Fetches a ticket from SQLite by ID |
| `get_user_tickets(employee_id)` | Returns all tickets for a user |

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, Vanilla CSS |
| Backend | Python 3.11+, FastAPI, Uvicorn |
| AI Agent | LangChain, LangGraph |
| LLM | Google Gemini (`gemini-1.5-flash`) via free API |
| Database | SQLite + SQLAlchemy |
| Knowledge Base | Local Markdown files |

---

## 📁 Project Structure

```
HelpDeskAI/
├── backend/
│   ├── main.py                   # FastAPI application + all endpoints
│   ├── agent/
│   │   ├── graph.py              # LangGraph workflow definition
│   │   ├── state.py              # AgentState TypedDict
│   │   ├── prompts.py            # LLM prompt templates
│   │   └── tools.py              # Tool implementations
│   ├── database/
│   │   ├── database.py           # SQLAlchemy setup + session
│   │   └── models.py             # Ticket model
│   ├── knowledge_base/
│   │   ├── vpn.md
│   │   ├── wifi.md
│   │   ├── email.md
│   │   ├── password.md
│   │   ├── laptop.md
│   │   └── application.md
│   ├── requirements.txt
│   ├── .env.example
│   └── .env                      # Your actual env file (create from .env.example)
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx  # Chat UI with message bubbles
│   │   │   ├── AgentActivity.jsx  # Real-time agent activity timeline
│   │   │   ├── TicketPanel.jsx    # Current ticket display
│   │   │   ├── MyTickets.jsx      # Tickets history list
│   │   │   └── StatusBadge.jsx    # Status/priority badges
│   │   ├── pages/
│   │   │   └── Dashboard.jsx      # Main dashboard layout
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css              # Global design system
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
│
└── README.md
```

---

## ⚙️ Environment Variables

Create `backend/.env` (copy from `backend/.env.example`):

```env
LLM_API_KEY=your_gemini_api_key_here
MODEL_NAME=gemini-1.5-flash
```

### Getting a Free Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click **"Get API key"** → **"Create API key"**
4. Copy the key into your `backend/.env` file

---

## 🚀 Local Setup

### Prerequisites
- Python 3.11+ (`python --version`)
- Node.js 18+ (`node --version`)
- A Gemini API key (free)

---

## 🖥️ Running the Backend

```bash
# 1. Navigate to the backend directory
cd backend

# 2. Create a Python virtual environment
python -m venv venv

# 3. Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create your .env file
copy .env.example .env       # Windows
# cp .env.example .env       # macOS/Linux

# 6. Add your Gemini API key to .env
# Edit .env and set LLM_API_KEY=your_actual_key

# 7. Start the FastAPI server
uvicorn main:app --reload --port 8000
```

The backend will be available at: **http://localhost:8000**

API documentation (Swagger UI): **http://localhost:8000/docs**

---

## 🌐 Running the Frontend

Open a **new terminal window**:

```bash
# 1. Navigate to the frontend directory
cd frontend

# 2. Install dependencies (first time only)
npm install

# 3. Start the Vite development server
npm run dev
```

The frontend will be available at: **http://localhost:5173**

---

## 🔌 API Reference

### `POST /api/chat`
Send a message to the AI agent.

**Request:**
```json
{
  "message": "My VPN isn't connecting",
  "session_id": "demo-session"
}
```

**Response (diagnosing):**
```json
{
  "message": "I've identified this as a VPN issue. Let's troubleshoot...",
  "status": "diagnosing",
  "issue_category": "VPN",
  "severity": "Medium",
  "agent_activity": ["✓ Issue identified: VPN", "✓ Retrieved VPN troubleshooting procedure"],
  "ticket_id": null,
  "session_id": "demo-session"
}
```

**Response (ticket created):**
```json
{
  "message": "I've created an IT support ticket...\n\nTicket ID: IT-1001",
  "status": "ticket_created",
  "issue_category": "VPN",
  "agent_activity": ["✓ IT ticket created: IT-1001"],
  "ticket_id": "IT-1001",
  "ticket_details": { ... }
}
```

### `GET /api/tickets`
Returns all tickets for the demo user (EMP001).

### `GET /api/tickets/{ticket_id}`
Returns a specific ticket by ID (e.g., `IT-1001`).

### `DELETE /api/session/{session_id}`
Resets a conversation session.

### `GET /api/health`
Health check endpoint.

---

## 💬 Example Demo Conversation

```
Employee: My VPN isn't connecting.

AI: I've identified this as a VPN issue. Let's troubleshoot it together.
    Can you access normal websites right now (e.g., google.com)?

Employee: Yes, I can browse the internet fine.

AI: Are you seeing any specific error message in the VPN client?
    For example, "Authentication Failed" or "Cannot reach server"?

Employee: Yes, it says "Authentication Failed"

AI: Please verify your company credentials are correct — try logging 
    into Outlook Web (outlook.office.com) with the same username and 
    password. Did that login work?

Employee: No, that didn't work either.

AI: It sounds like your password may have expired. Please visit 
    reset.company.com to reset your password. After resetting, try 
    the VPN again. Did the password reset resolve the issue?

Employee: No, still not working.

AI: I've exhausted the standard troubleshooting steps for your VPN 
    issue without resolving it. I've created an IT support ticket.

    **Ticket ID:** IT-1001
    **Priority:** Medium
    **Description:** Employee's VPN is failing with "Authentication Failed"...

    Our IT team will review and contact you.
```

---

## ☁️ Deployment

### Option 1: Deploy to Railway (Recommended — Free Tier)

#### Backend
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
cd backend
railway init
railway up

# Set environment variables in Railway dashboard:
# LLM_API_KEY = your_gemini_key
# MODEL_NAME = gemini-1.5-flash
```

#### Frontend
```bash
cd frontend
npm run build

# Deploy 'dist/' folder to Vercel or Netlify:
npx vercel deploy dist/
# or drag-drop dist/ to https://app.netlify.com/drop

# Set environment variable:
# VITE_API_BASE = https://your-railway-backend-url.up.railway.app
```

### Option 2: Deploy to Render (Free Tier)

**Backend:**
1. Connect GitHub repo to [render.com](https://render.com)
2. New → Web Service → select `backend/` directory
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add env vars: `LLM_API_KEY`, `MODEL_NAME`

**Frontend:**
1. New → Static Site → select `frontend/` directory
2. Build command: `npm install && npm run build`
3. Publish directory: `dist`
4. Add env var: `VITE_API_BASE=https://your-render-backend.onrender.com`

### Option 3: Docker (Local or Cloud)

```bash
# Backend Dockerfile (create in backend/)
# FROM python:3.11-slim
# WORKDIR /app
# COPY requirements.txt .
# RUN pip install -r requirements.txt
# COPY . .
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

docker build -t helpdesk-backend ./backend
docker run -p 8000:8000 -e LLM_API_KEY=your_key helpdesk-backend

# Frontend
cd frontend && npm run build
# Serve dist/ with nginx or any static server
```

---

## 🎯 Key Design Decisions

1. **LangGraph over simple LLM calls**: The workflow is a proper state machine — not a chatbot. Each turn progresses through defined nodes (classify → retrieve → diagnose → resolve/ticket).

2. **Local Markdown knowledge base**: No vector database needed. Simple keyword + category matching is sufficient for 6 issue types and is faster to run.

3. **In-memory session store**: For demo purposes, sessions are stored in Python dict (no Redis needed). For production, swap with a database-backed session store.

4. **Structured LLM outputs**: All LLM calls return JSON objects parsed server-side. The UI never trusts raw LLM text for critical actions like ticket creation.

5. **Tool safety**: `create_ticket()` only reports success after the SQLite commit succeeds. If the DB write fails, the user is told the ticket was NOT created.

---

## 🔧 Troubleshooting Setup Issues

| Issue | Fix |
|-------|-----|
| `LLM_API_KEY is not set` | Edit `backend/.env` and add your Gemini key |
| `CORS error in browser` | Make sure backend is running on port 8000 |
| `Module not found` | Run `pip install -r requirements.txt` in the venv |
| `npm: command not found` | Install Node.js from [nodejs.org](https://nodejs.org) |
| `uvicorn: command not found` | Activate venv first: `venv\Scripts\activate` |

---

## 📊 Supported Issue Categories

| Category | Knowledge Base File |
|----------|-------------------|
| VPN Connectivity | `vpn.md` |
| Wi-Fi Connectivity | `wifi.md` |
| Email / Outlook | `email.md` |
| Password / Account | `password.md` |
| Slow Laptop | `laptop.md` |
| Application Access | `application.md` |

---

*Built as a portfolio project demonstrating: LangGraph agentic workflows, FastAPI backend design, React frontend, SQLite persistence, and tool-calling patterns.*
