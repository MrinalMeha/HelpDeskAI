"""
HelpDeskAI FastAPI Backend
--------------------------
An AI-powered IT support agent backend using LangGraph + Gemini + SQLite.
"""
import logging
import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from database.database import get_db, init_db
from database.models import Ticket
from agent.tools import (
    create_ticket as tool_create_ticket,
    get_ticket as tool_get_ticket,
    get_user_tickets as tool_get_user_tickets,
)
from agent.prompts import TICKET_SUMMARY_PROMPT
from agent.graph import process_agent_turn, _parse_json_response
from agent.tools import update_ticket_status
from langchain_google_genai import ChatGoogleGenerativeAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# App setup                                                                    #
# --------------------------------------------------------------------------- #
app = FastAPI(
    title="HelpDeskAI API",
    description="AI-powered IT Support Agent",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Init DB on startup
@app.on_event("startup")
def startup():
    init_db()
    logger.info("Database initialized")


# --------------------------------------------------------------------------- #
# In-memory session store                                                      #
# (For demo: stores conversation state per session_id)                        #
# --------------------------------------------------------------------------- #
SESSION_STORE: dict[str, dict] = {}

DEMO_USER = {
    "employee_id": "EMP001",
    "name": "Demo Employee",
    "department": "Engineering",
}


# --------------------------------------------------------------------------- #
# Pydantic models                                                              #
# --------------------------------------------------------------------------- #
class ChatRequest(BaseModel):
    message: str
    session_id: str = "demo-session"
    message_id: str = "" 


class ChatResponse(BaseModel):
    message: str
    status: str  # "greeting" | "classifying" | "diagnosing" | "resolved" | "ticket_created" | "error"
    issue_category: Optional[str] = None
    severity: Optional[str] = None
    agent_activity: list[str] = []
    ticket_id: Optional[str] = None
    ticket_details: Optional[dict] = None
    session_id: str


class TicketResponse(BaseModel):
    ticket_id: str
    employee_id: str
    category: str
    priority: str
    status: str
    description: str
    diagnostics: list
    created_at: Optional[str] = None


# --------------------------------------------------------------------------- #
# Helper: get or init session state                                            #
# --------------------------------------------------------------------------- #
def get_session(session_id: str) -> dict:
    if session_id not in SESSION_STORE:
        SESSION_STORE[session_id] = {
            "messages": [],
            "last_processed_message_id": "",
            "issue_description": "",
            "issue_category": "",
            "severity": "",
            "completed_steps": [],
            "attempted_steps": [],
            "knowledge_base_content": "",
            "current_step": "",
            "ticket_status": "OPEN",
            "ticket_id": None,
            "agent_activity": [],
            "workflow_stage": "start",
        }
    return SESSION_STORE[session_id]


def save_session(session_id: str, state: dict):
    SESSION_STORE[session_id] = state


# --------------------------------------------------------------------------- #
# POST /api/chat                                                               #
# --------------------------------------------------------------------------- #
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    session_id = request.session_id
    message_id = request.message_id
    user_message = request.message.strip()

    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # Check for API key
    if not os.getenv("LLM_API_KEY"):
        return ChatResponse(
            message="⚠️ LLM_API_KEY is not configured. Please set it in your .env file.",
            status="error",
            session_id=session_id,
            agent_activity=["⚠ Missing API key configuration"],
        )

    state = get_session(session_id)
    
    # Idempotency check
    if message_id and state.get("last_processed_message_id") == message_id:
        # Return the last state without re-processing
        last_msg = state["messages"][-1].content if state["messages"] else "Processing..."
        return ChatResponse(
            message=last_msg,
            status=state["workflow_stage"] if state["workflow_stage"] in ["error", "resolved", "start"] else "diagnosing",
            issue_category=state.get("issue_category"),
            severity=state.get("severity"),
            agent_activity=state.get("agent_activity", []),
            ticket_id=state.get("ticket_id"),
            session_id=session_id,
        )

    # If ticket was already created or resolved and user sends new msg, reset
    if state.get("ticket_id") or state.get("workflow_stage") in ("resolved", "done"):
        state = {
            "messages": [],
            "last_processed_message_id": message_id,
            "issue_description": "",
            "issue_category": "",
            "severity": "",
            "completed_steps": [],
            "attempted_steps": [],
            "knowledge_base_content": "",
            "current_step": "",
            "ticket_status": "OPEN",
            "ticket_id": None,
            "agent_activity": [],
            "workflow_stage": "start",
        }
        SESSION_STORE[session_id] = state

    # Process Agent Turn
    try:
        state["last_processed_message_id"] = message_id
        state = process_agent_turn(state, user_message)
        
        # Check output state
        if state["workflow_stage"] == "escalated":
            return await _create_ticket_response(state, session_id, db)
        elif state["workflow_stage"] == "resolved":
            # Update ticket if exists
            if state.get("ticket_id"):
                update_ticket_status(db, state["ticket_id"], "RESOLVED")
            return _resolved_response(state, session_id)
        
        # Default: troubleshooting continues
        last_ai_msg = state["messages"][-1].content
        save_session(session_id, state)
        return ChatResponse(
            message=last_ai_msg,
            status="diagnosing",
            issue_category=state.get("issue_category"),
            severity=state.get("severity"),
            agent_activity=state.get("agent_activity", []),
            ticket_id=state.get("ticket_id"),
            session_id=session_id,
        )

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        return ChatResponse(
            message=f"I encountered an unexpected error. Please try again. (Error: {str(e)[:100]})",
            status="error",
            session_id=session_id,
            agent_activity=state.get("agent_activity", []) + [f"⚠ Error: {str(e)[:60]}"],
        )

# Remove old unused routes / block logic

async def _create_ticket_response(state: dict, session_id: str, db: Session) -> ChatResponse:
    activity = list(state.get("agent_activity", []))
    activity.append("⟳ Generating ticket summary...")

    # Generate ticket summary via LLM
    diagnostics = state.get("completed_steps", [])
    diag_text = "\n".join(
        [f"- {s['step']}: {s['result']}" for s in diagnostics]
    ) if diagnostics else "No specific diagnostics recorded."

    try:
        llm = ChatGoogleGenerativeAI(
            model=os.getenv("MODEL_NAME", "gemini-1.5-flash"),
            google_api_key=os.getenv("LLM_API_KEY", ""),
            temperature=0.2,
        )
        prompt = TICKET_SUMMARY_PROMPT.format(
            category=state.get("issue_category", "IT"),
            description=state.get("issue_description", ""),
            severity=state.get("severity", "Medium"),
            diagnostics=diag_text,
        )
        response = llm.invoke(prompt)
        parsed = _parse_json_response(response.content)
        ticket_description = parsed.get("ticket_description", state.get("issue_description", ""))
        priority = parsed.get("priority", state.get("severity", "Medium"))
    except Exception as e:
        logger.error(f"Ticket summary LLM error: {e}")
        ticket_description = state.get("issue_description", "IT issue requiring support")
        priority = state.get("severity", "Medium")

    # Actually create the ticket in the database
    result = tool_create_ticket(
        db=db,
        category=state.get("issue_category", "IT"),
        priority=priority,
        description=ticket_description,
        diagnostics=diagnostics,
        session_id=session_id,
        employee_id=DEMO_USER["employee_id"],
    )

    if not result.get("success"):
        activity.append("⚠ Ticket creation failed — please contact IT directly")
        response_msg = (
            "I wasn't able to create a support ticket at this time due to a system error. "
            "Please contact IT support directly. I apologize for the inconvenience."
        )
        state["agent_activity"] = activity
        state["workflow_stage"] = "error"
        save_session(session_id, state)

        return ChatResponse(
            message=response_msg,
            status="error",
            issue_category=state.get("issue_category"),
            agent_activity=activity,
            session_id=session_id,
        )

    ticket_id = result["ticket_id"]
    activity.append("✓ Troubleshooting completed")
    activity.append("✓ Issue unresolved after diagnostics")
    activity.append(f"✓ IT ticket created: {ticket_id}")

    response_msg = (
        f"I've exhausted the standard troubleshooting steps for your {state.get('issue_category', 'IT')} issue "
        f"without resolving it. I've created an IT support ticket for you.\n\n"
        f"**Ticket ID:** {ticket_id}\n"
        f"**Priority:** {priority}\n"
        f"**Description:** {ticket_description}\n\n"
        f"Our IT team will review and contact you. You can track your ticket status in the 'My Tickets' section."
    )

    state["ticket_id"] = ticket_id
    state["agent_activity"] = activity
    state["workflow_stage"] = "done"
    state["messages"].append(AIMessage(content=response_msg))
    save_session(session_id, state)

    return ChatResponse(
        message=response_msg,
        status="ticket_created",
        issue_category=state.get("issue_category"),
        severity=state.get("severity"),
        agent_activity=activity,
        ticket_id=ticket_id,
        ticket_details=result,
        session_id=session_id,
    )


def _resolved_response(state: dict, session_id: str) -> ChatResponse:
    activity = list(state.get("agent_activity", []))
    activity.append("✓ Issue successfully resolved!")

    response_msg = (
        "Great news! It looks like we've resolved your issue. "
        "If the problem comes back, don't hesitate to reach out again. "
        "Is there anything else I can help you with?"
    )

    state["agent_activity"] = activity
    state["workflow_stage"] = "done"
    state["messages"].append(AIMessage(content=response_msg))
    save_session(session_id, state)

    return ChatResponse(
        message=response_msg,
        status="resolved",
        issue_category=state.get("issue_category"),
        severity=state.get("severity"),
        agent_activity=activity,
        session_id=session_id,
    )


# --------------------------------------------------------------------------- #
# GET /api/tickets                                                             #
# --------------------------------------------------------------------------- #
@app.get("/api/tickets", response_model=list[TicketResponse])
def list_tickets(db: Session = Depends(get_db)):
    """Return all tickets for the demo user."""
    tickets = tool_get_user_tickets(db=db, employee_id=DEMO_USER["employee_id"])
    return [
        TicketResponse(
            ticket_id=t["ticket_id"],
            employee_id=t["employee_id"],
            category=t["category"],
            priority=t["priority"],
            status=t["status"],
            description=t["description"],
            diagnostics=t["diagnostics"],
            created_at=t["created_at"],
        )
        for t in tickets
    ]


# --------------------------------------------------------------------------- #
# GET /api/tickets/{ticket_id}                                                #
# --------------------------------------------------------------------------- #
@app.get("/api/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket_endpoint(ticket_id: str, db: Session = Depends(get_db)):
    """Retrieve a specific ticket by ID."""
    ticket = tool_get_ticket(db=db, ticket_id=ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found.")
    return TicketResponse(**ticket)


# --------------------------------------------------------------------------- #
# DELETE /api/session/{session_id}  (utility for reset)                       #
# --------------------------------------------------------------------------- #
@app.delete("/api/session/{session_id}")
def reset_session(session_id: str):
    """Reset a session (start fresh conversation)."""
    if session_id in SESSION_STORE:
        del SESSION_STORE[session_id]
    return {"message": f"Session {session_id} reset successfully."}


# --------------------------------------------------------------------------- #
# GET /api/health                                                              #
# --------------------------------------------------------------------------- #
@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "model": os.getenv("MODEL_NAME", "gemini-1.5-flash"),
        "api_key_set": bool(os.getenv("LLM_API_KEY")),
        "timestamp": datetime.utcnow().isoformat(),
    }


# --------------------------------------------------------------------------- #
# GET /api/user                                                                #
# --------------------------------------------------------------------------- #
@app.get("/api/user")
def get_user():
    return DEMO_USER
