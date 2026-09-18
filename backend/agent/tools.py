"""Tools used by the HelpDeskAI agent."""
import json
import re
import logging
from pathlib import Path
from sqlalchemy.orm import Session
from database.models import Ticket

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Knowledge-base path                                                          #
# --------------------------------------------------------------------------- #
KB_DIR = Path(__file__).parent.parent / "knowledge_base"

CATEGORY_TO_FILE = {
    "VPN": "vpn.md",
    "WiFi": "wifi.md",
    "Email": "email.md",
    "Password": "password.md",
    "Laptop": "laptop.md",
    "Application": "application.md",
}


# --------------------------------------------------------------------------- #
# Tool 1: Search Knowledge Base                                                #
# --------------------------------------------------------------------------- #
def search_knowledge_base(query: str, category: str = "") -> str:
    """
    Search local markdown troubleshooting documents for relevant content.
    Returns the content of the best matching document(s).
    """
    results = []

    # If we have a category, load the matching file first
    if category and category in CATEGORY_TO_FILE:
        filename = CATEGORY_TO_FILE[category]
        filepath = KB_DIR / filename
        if filepath.exists():
            content = filepath.read_text(encoding="utf-8")
            results.append(f"[{category} Troubleshooting Guide]\n{content}")

    # Also do keyword search across all files for additional context
    query_lower = query.lower()
    keywords = query_lower.split()

    for filename in KB_DIR.glob("*.md"):
        # Skip the one we already loaded
        if category and filename.name == CATEGORY_TO_FILE.get(category, ""):
            continue
        try:
            content = filename.read_text(encoding="utf-8")
            content_lower = content.lower()
            # Score: count keyword hits
            score = sum(kw in content_lower for kw in keywords)
            if score >= 2:
                results.append(f"[{filename.stem.upper()} Guide - additional context]\n{content[:1500]}")
        except Exception as e:
            logger.warning(f"Could not read {filename}: {e}")

    if not results:
        return "No specific troubleshooting guide found. Use general IT best practices."

    return "\n\n---\n\n".join(results[:2])  # Return top 2 results max


# --------------------------------------------------------------------------- #
# Tool 2: Record Diagnostic                                                    #
# --------------------------------------------------------------------------- #
def record_diagnostic(step: str, result: str, current_steps: list) -> list:
    """
    Record a diagnostic step and its result.
    Returns the updated list of diagnostic steps.
    """
    updated_steps = list(current_steps)
    updated_steps.append({
        "step": step,
        "result": result,
    })
    logger.info(f"Diagnostic recorded - Step: '{step}', Result: '{result}'")
    return updated_steps


# --------------------------------------------------------------------------- #
# Tool 3: Create Ticket                                                        #
# --------------------------------------------------------------------------- #
def create_ticket(
    db: Session,
    category: str,
    priority: str,
    description: str,
    diagnostics: list[dict],
    session_id: str = "demo-session",
    employee_id: str = "EMP001",
) -> dict:
    """
    Create a real IT support ticket in SQLite.
    Returns ticket details including the generated ticket ID.
    """
    try:
        # Generate ticket ID: IT-XXXX (auto-increment from 1001)
        last_ticket = (
            db.query(Ticket)
            .order_by(Ticket.id.desc())
            .first()
        )
        if last_ticket:
            # Extract the number part
            match = re.search(r"IT-(\d+)", last_ticket.ticket_id)
            if match:
                next_num = int(match.group(1)) + 1
            else:
                next_num = 1001
        else:
            next_num = 1001

        ticket_id = f"IT-{next_num}"

        # Serialize diagnostics to JSON string
        diagnostics_json = json.dumps(diagnostics, indent=2)

        ticket = Ticket(
            ticket_id=ticket_id,
            employee_id=employee_id,
            category=category,
            priority=priority,
            status="Open",
            description=description,
            diagnostics=diagnostics_json,
            session_id=session_id,
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        logger.info(f"Ticket created: {ticket_id} for session {session_id}")

        return {
            "success": True,
            "ticket_id": ticket_id,
            "category": category,
            "priority": priority,
            "status": "Open",
            "description": description,
            "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
        }
    except Exception as e:
        logger.error(f"Failed to create ticket: {e}")
        db.rollback()
        return {
            "success": False,
            "error": str(e),
        }


# --------------------------------------------------------------------------- #
# Tool 4: Get Ticket                                                           #
# --------------------------------------------------------------------------- #
def get_ticket(db: Session, ticket_id: str) -> dict | None:
    """Retrieve a ticket from the database by ticket ID."""
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if not ticket:
        return None
    return {
        "ticket_id": ticket.ticket_id,
        "employee_id": ticket.employee_id,
        "category": ticket.category,
        "priority": ticket.priority,
        "status": ticket.status,
        "description": ticket.description,
        "diagnostics": json.loads(ticket.diagnostics) if ticket.diagnostics else [],
        "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
    }


# --------------------------------------------------------------------------- #
# Tool 5: Get User Tickets                                                     #
# --------------------------------------------------------------------------- #
def get_user_tickets(db: Session, employee_id: str = "EMP001") -> list[dict]:
    """Return all tickets created by the demo user."""
    tickets = (
        db.query(Ticket)
        .filter(Ticket.employee_id == employee_id)
        .order_by(Ticket.created_at.desc())
        .all()
    )
    result = []
    for t in tickets:
        result.append({
            "ticket_id": t.ticket_id,
            "employee_id": t.employee_id,
            "category": t.category,
            "priority": t.priority,
            "status": t.status,
            "description": t.description,
            "diagnostics": json.loads(t.diagnostics) if t.diagnostics else [],
            "created_at": t.created_at.isoformat() if t.created_at else None,
        })
    return result
