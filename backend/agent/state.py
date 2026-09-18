"""Agent state definition for the HelpDeskAI LangGraph workflow."""
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """Complete state maintained throughout the agent workflow."""
    # Conversation messages (LangChain messages)
    messages: Annotated[list, add_messages]

    # Issue details
    issue_description: str
    issue_category: str       # VPN, WiFi, Email, Password, Laptop, Application
    severity: str             # Low, Medium, High, Critical

    # Troubleshooting state
    troubleshooting_steps: list[dict]   # [{"step": ..., "result": ...}]
    knowledge_base_content: str         # Relevant KB content retrieved
    current_question: str               # The current diagnostic question asked
    questions_asked: int                # Count of questions asked

    # Resolution state
    resolved: bool
    resolution_attempts: int
    max_attempts: int

    # Ticket
    ticket_id: str | None

    # UI Activity log
    agent_activity: list[str]

    # Flow control
    workflow_stage: str  # classify | retrieve | diagnose | check_resolution | create_ticket | done
    awaiting_user_response: bool
