"""
LangGraph workflow graph for the HelpDeskAI agent.

Graph flow:
  START
    ↓
  classify_issue          ← Understand & classify the IT issue
    ↓
  retrieve_knowledge      ← Search knowledge base for relevant info
    ↓
  ask_diagnostic_question ← Generate next diagnostic question
    ↓  (returns to frontend to wait for user reply)
  [USER RESPONDS]
    ↓
  process_user_response   ← Record diagnostic result & check resolution
    ↓
  ┌─────────────────────┐
  │                     │
resolved             unresolved
  │                     │
  ↓                     ↓
  done            create_ticket_node
                        ↓
                       done
"""
import json
import logging
import os
from typing import Literal

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from agent.state import AgentState
from agent.prompts import (
    CLASSIFY_PROMPT,
    DIAGNOSTIC_QUESTION_PROMPT,
    RECORD_AND_DECIDE_PROMPT,
)
from agent.tools import search_knowledge_base, record_diagnostic

logger = logging.getLogger(__name__)

MAX_DIAGNOSTIC_QUESTIONS = 5


def _get_llm():
    """Create the LLM instance."""
    api_key = os.getenv("LLM_API_KEY", "")
    model_name = os.getenv("MODEL_NAME", "gemini-1.5-flash")
    if not api_key:
        raise ValueError("LLM_API_KEY environment variable is not set.")
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0.2,
    )


def _extract_text(content) -> str:
    """Normalize LLM response content to a plain string.

    Newer versions of langchain-google-genai return content as a list of
    dicts (e.g. [{'type': 'text', 'text': '...'}]) rather than a plain str.
    This helper handles both formats.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                parts.append(block.get("text", ""))
            elif isinstance(block, str):
                parts.append(block)
        return "".join(parts)
    return str(content)


def _parse_json_response(content) -> dict:
    """Safely parse JSON from LLM response, stripping markdown fences if present."""
    text = _extract_text(content).strip()
    # Remove markdown code fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first and last fence lines
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}\nRaw text: {text}")
        return {}


# --------------------------------------------------------------------------- #
# Node 1: Classify Issue                                                       #
# --------------------------------------------------------------------------- #
def classify_issue(state: AgentState) -> AgentState:
    """Classify the IT issue from the initial employee message."""
    activity = list(state.get("agent_activity", []))
    activity.append("⟳ Analyzing your issue...")

    # Get the latest human message
    messages = state.get("messages", [])
    last_human = ""
    for msg in reversed(messages):
        if hasattr(msg, "type") and msg.type == "human":
            last_human = msg.content
            break
        elif isinstance(msg, dict) and msg.get("role") == "human":
            last_human = msg.get("content", "")
            break

    issue_desc = state.get("issue_description", last_human)

    try:
        llm = _get_llm()
        prompt = CLASSIFY_PROMPT.format(message=issue_desc)
        response = llm.invoke(prompt)
        parsed = _parse_json_response(response.content)

        category = parsed.get("category", "Application")
        severity = parsed.get("severity", "Medium")
        description = parsed.get("description", issue_desc)

        activity.append(f"✓ Issue identified: {category} ({severity} priority)")
        logger.info(f"Classified issue: category={category}, severity={severity}")

        return {
            **state,
            "issue_category": category,
            "severity": severity,
            "issue_description": description,
            "workflow_stage": "retrieve",
            "agent_activity": activity,
            "awaiting_user_response": False,
        }
    except Exception as e:
        logger.error(f"Classification error: {e}")
        activity.append("⚠ Classification encountered an error, defaulting to general IT issue")
        return {
            **state,
            "issue_category": "Application",
            "severity": "Medium",
            "issue_description": issue_desc,
            "workflow_stage": "retrieve",
            "agent_activity": activity,
            "awaiting_user_response": False,
        }


# --------------------------------------------------------------------------- #
# Node 2: Retrieve Knowledge                                                   #
# --------------------------------------------------------------------------- #
def retrieve_knowledge(state: AgentState) -> AgentState:
    """Search the knowledge base for relevant troubleshooting information."""
    activity = list(state.get("agent_activity", []))
    category = state.get("issue_category", "")
    description = state.get("issue_description", "")

    activity.append(f"⟳ Retrieving {category} troubleshooting guide...")

    try:
        kb_content = search_knowledge_base(query=description, category=category)
        activity.append(f"✓ Retrieved {category} troubleshooting procedure")
        logger.info(f"KB content retrieved, length={len(kb_content)}")
    except Exception as e:
        logger.error(f"KB retrieval error: {e}")
        kb_content = "General IT troubleshooting: restart the device, check network, and verify credentials."
        activity.append("⚠ Could not load specific guide, using general procedure")

    return {
        **state,
        "knowledge_base_content": kb_content,
        "workflow_stage": "diagnose",
        "agent_activity": activity,
    }


# --------------------------------------------------------------------------- #
# Node 3: Ask Diagnostic Question                                              #
# --------------------------------------------------------------------------- #
def ask_diagnostic_question(state: AgentState) -> AgentState:
    """Generate the next diagnostic question for the employee."""
    activity = list(state.get("agent_activity", []))
    questions_asked = state.get("questions_asked", 0)

    activity.append("⟳ Determining next troubleshooting step...")

    # Build context from completed steps
    completed_steps = state.get("troubleshooting_steps", [])
    steps_text = "\n".join(
        [f"- {s['step']}: {s['result']}" for s in completed_steps]
    ) if completed_steps else "None yet."

    # Get last user message
    messages = state.get("messages", [])
    last_response = ""
    for msg in reversed(messages):
        if hasattr(msg, "type") and msg.type == "human":
            last_response = msg.content
            break
        elif isinstance(msg, dict) and msg.get("role") == "human":
            last_response = msg.get("content", "")
            break

    try:
        llm = _get_llm()
        prompt = DIAGNOSTIC_QUESTION_PROMPT.format(
            category=state.get("issue_category", "IT"),
            description=state.get("issue_description", ""),
            knowledge_base_content=state.get("knowledge_base_content", ""),
            completed_steps=steps_text,
            questions_asked=questions_asked,
            max_questions=MAX_DIAGNOSTIC_QUESTIONS,
            last_response=last_response,
        )
        response = llm.invoke(prompt)
        parsed = _parse_json_response(response.content)

        question = parsed.get("question", "Could you describe the exact error message you see?")
        is_resolved = parsed.get("is_resolved", False)
        should_escalate = parsed.get("should_escalate", False)
        step_name = parsed.get("diagnostic_step_name", f"Diagnostic step {questions_asked + 1}")

        if is_resolved:
            activity.append("✓ Issue appears to be resolved!")
            return {
                **state,
                "current_question": question,
                "resolved": True,
                "workflow_stage": "check_resolution",
                "agent_activity": activity,
                "awaiting_user_response": False,
            }

        if should_escalate or questions_asked >= MAX_DIAGNOSTIC_QUESTIONS:
            activity.append("✓ Troubleshooting steps exhausted — escalating to ticket")
            return {
                **state,
                "current_question": question,
                "resolved": False,
                "workflow_stage": "create_ticket",
                "agent_activity": activity,
                "awaiting_user_response": False,
            }

        activity.append(f"✓ {step_name}")
        return {
            **state,
            "current_question": question,
            "questions_asked": questions_asked + 1,
            "workflow_stage": "diagnose",
            "agent_activity": activity,
            "awaiting_user_response": True,
        }

    except Exception as e:
        logger.error(f"Diagnostic question error: {e}")
        fallback = "Could you please describe the exact error message or behavior you are seeing?"
        return {
            **state,
            "current_question": fallback,
            "questions_asked": questions_asked + 1,
            "workflow_stage": "diagnose",
            "agent_activity": activity,
            "awaiting_user_response": True,
        }


# --------------------------------------------------------------------------- #
# Node 4: Process User Response                                                #
# --------------------------------------------------------------------------- #
def process_user_response(state: AgentState) -> AgentState:
    """Record the user's response to the diagnostic question and decide next step."""
    activity = list(state.get("agent_activity", []))

    # Get last user message
    messages = state.get("messages", [])
    last_response = ""
    for msg in reversed(messages):
        if hasattr(msg, "type") and msg.type == "human":
            last_response = msg.content
            break
        elif isinstance(msg, dict) and msg.get("role") == "human":
            last_response = msg.get("content", "")
            break

    current_question = state.get("current_question", "")

    try:
        llm = _get_llm()
        prompt = RECORD_AND_DECIDE_PROMPT.format(
            description=state.get("issue_description", ""),
            category=state.get("issue_category", "IT"),
            step_name=current_question[:100],
            employee_response=last_response,
        )
        response = llm.invoke(prompt)
        parsed = _parse_json_response(response.content)

        resolved = parsed.get("resolved", False)
        step_result = parsed.get("step_result", last_response[:200])

        # Record diagnostic via tool
        updated_steps = record_diagnostic(
            step=current_question,
            result=step_result,
            current_steps=state.get("troubleshooting_steps", []),
        )

        activity.append("✓ Recorded diagnostic result")

        if resolved:
            activity.append("✓ Issue resolved!")
            return {
                **state,
                "troubleshooting_steps": updated_steps,
                "resolved": True,
                "workflow_stage": "check_resolution",
                "agent_activity": activity,
                "awaiting_user_response": False,
            }

        # Check if we've hit max questions
        questions_asked = state.get("questions_asked", 0)
        if questions_asked >= MAX_DIAGNOSTIC_QUESTIONS:
            activity.append("✓ Troubleshooting steps exhausted")
            return {
                **state,
                "troubleshooting_steps": updated_steps,
                "resolved": False,
                "workflow_stage": "create_ticket",
                "agent_activity": activity,
                "awaiting_user_response": False,
            }

        return {
            **state,
            "troubleshooting_steps": updated_steps,
            "resolved": False,
            "workflow_stage": "diagnose",
            "agent_activity": activity,
            "awaiting_user_response": False,
        }

    except Exception as e:
        logger.error(f"Process response error: {e}")
        updated_steps = record_diagnostic(
            step=current_question,
            result=last_response,
            current_steps=state.get("troubleshooting_steps", []),
        )
        return {
            **state,
            "troubleshooting_steps": updated_steps,
            "workflow_stage": "diagnose",
            "agent_activity": activity,
            "awaiting_user_response": False,
        }


# --------------------------------------------------------------------------- #
# Routing Functions                                                            #
# --------------------------------------------------------------------------- #
def route_after_classify(state: AgentState) -> Literal["retrieve_knowledge"]:
    return "retrieve_knowledge"


def route_after_retrieve(state: AgentState) -> Literal["ask_diagnostic_question"]:
    return "ask_diagnostic_question"


def route_after_diagnostic(
    state: AgentState,
) -> Literal["done", "create_ticket_node", "ask_diagnostic_question"]:
    stage = state.get("workflow_stage", "diagnose")
    if state.get("resolved"):
        return "done"
    if stage == "create_ticket":
        return "create_ticket_node"
    # awaiting user response — the graph stops here (interrupt)
    return "done"


def route_after_process(
    state: AgentState,
) -> Literal["done", "create_ticket_node", "ask_diagnostic_question"]:
    stage = state.get("workflow_stage", "diagnose")
    if state.get("resolved"):
        return "done"
    if stage == "create_ticket":
        return "create_ticket_node"
    return "ask_diagnostic_question"


# --------------------------------------------------------------------------- #
# Ticket creation node (called from outside graph with db session)            #
# --------------------------------------------------------------------------- #
def prepare_ticket_creation(state: AgentState) -> AgentState:
    """Prepare the state for ticket creation — the actual DB call is in main.py."""
    activity = list(state.get("agent_activity", []))
    activity.append("⟳ Creating IT support ticket...")
    return {
        **state,
        "workflow_stage": "create_ticket",
        "agent_activity": activity,
        "awaiting_user_response": False,
    }


# --------------------------------------------------------------------------- #
# Build the Graph                                                              #
# --------------------------------------------------------------------------- #
def build_graph():
    """Build and compile the LangGraph workflow."""
    builder = StateGraph(AgentState)

    # Add nodes
    builder.add_node("classify_issue", classify_issue)
    builder.add_node("retrieve_knowledge", retrieve_knowledge)
    builder.add_node("ask_diagnostic_question", ask_diagnostic_question)
    builder.add_node("process_user_response", process_user_response)
    builder.add_node("create_ticket_node", prepare_ticket_creation)

    # Set entry point
    builder.set_entry_point("classify_issue")

    # Add edges
    builder.add_edge("classify_issue", "retrieve_knowledge")
    builder.add_edge("retrieve_knowledge", "ask_diagnostic_question")

    builder.add_conditional_edges(
        "ask_diagnostic_question",
        route_after_diagnostic,
        {
            "done": END,
            "create_ticket_node": "create_ticket_node",
            "ask_diagnostic_question": "ask_diagnostic_question",
        },
    )

    builder.add_edge("process_user_response", "ask_diagnostic_question")
    builder.add_edge("create_ticket_node", END)

    return builder.compile()


# Global compiled graph instance
graph = build_graph()
