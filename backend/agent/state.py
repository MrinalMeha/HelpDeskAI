"""Agent state definition for the HelpDeskAI LangGraph workflow."""
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """Complete state maintained throughout the agent workflow."""
    # Conversation messages (LangChain messages)
    messages: Annotated[list, add_messages]
    
    # Idempotency
    last_processed_message_id: str

    # Issue details
    issue_description: str
    issue_category: str       # VPN, WiFi, Email, Password, Laptop, Application
    severity: str             # Low, Medium, High, Critical

    # Troubleshooting state
    completed_steps: list[dict]         # [{"step": ..., "result": ...}]
    attempted_steps: list[str]          # ["step1", "step2"]
    knowledge_base_content: str         # Relevant KB content retrieved
    current_step: str                   # The current diagnostic step being asked

    # Resolution state
    ticket_status: str                  # OPEN, IN_PROGRESS, WAITING_FOR_USER, RESOLVED, ESCALATED
    ticket_id: str | None

    # UI Activity log
    agent_activity: list[str]

    # Flow control
    workflow_stage: str                 # start | troubleshooting | resolved | escalated | error
