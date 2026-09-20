"""
Agent logic for the HelpDeskAI agent.
"""
import json
import logging
import os
from typing import Literal

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage

from agent.state import AgentState
from agent.prompts import CLASSIFY_PROMPT
from agent.tools import search_knowledge_base

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
    text = _extract_text(content).strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}\nRaw text: {text}")
        return {}

def classify_issue(issue_desc: str) -> dict:
    """Classify the IT issue."""
    try:
        llm = _get_llm()
        prompt = CLASSIFY_PROMPT.format(message=issue_desc)
        response = llm.invoke(prompt)
        parsed = _parse_json_response(response.content)

        category = parsed.get("category", "Application")
        severity = parsed.get("severity", "Medium")
        description = parsed.get("description", issue_desc)
        return {"category": category, "severity": severity, "description": description}
    except Exception as e:
        logger.error(f"Classification error: {e}")
        return {"category": "Application", "severity": "Medium", "description": issue_desc}

def retrieve_knowledge(category: str, description: str) -> str:
    """Search the knowledge base."""
    try:
        return search_knowledge_base(query=description, category=category)
    except Exception as e:
        logger.error(f"KB retrieval error: {e}")
        return "General IT troubleshooting: restart the device, check network, and verify credentials."

def process_agent_turn(state: AgentState, user_message: str) -> AgentState:
    """Process a single turn of conversation using a structured LLM call."""
    activity = list(state.get("agent_activity", []))
    
    # 1. If first turn, classify and retrieve
    if state["workflow_stage"] == "start":
        activity.append("⟳ Analyzing your issue...")
        classification = classify_issue(user_message)
        state["issue_category"] = classification["category"]
        state["severity"] = classification["severity"]
        state["issue_description"] = classification["description"]
        activity.append(f"✓ Issue identified: {state['issue_category']} ({state['severity']} priority)")
        
        activity.append(f"⟳ Retrieving {state['issue_category']} troubleshooting guide...")
        state["knowledge_base_content"] = retrieve_knowledge(state["issue_category"], state["issue_description"])
        activity.append(f"✓ Retrieved {state['issue_category']} troubleshooting procedure")
        state["workflow_stage"] = "troubleshooting"

    # 2. Record the result of the previous step if applicable
    if state["current_step"] and user_message:
        state["completed_steps"].append({
            "step": state["current_step"],
            "result": user_message
        })

    # 3. Ask LLM for the next action
    activity.append("⟳ Determining next step...")
    
    completed_steps_text = "\n".join(
        [f"- {s['step']}: {s['result']}" for s in state.get("completed_steps", [])]
    ) if state.get("completed_steps") else "None yet."
    
    attempted_steps_text = ", ".join(state.get("attempted_steps", [])) if state.get("attempted_steps") else "None"

    AGENT_PROMPT = f"""You are an expert IT HelpDesk AI agent.
Issue Category: {state['issue_category']}
Issue Description: {state['issue_description']}

Knowledge Base Guidelines:
{state['knowledge_base_content']}

Steps already completed by the user and their results:
{completed_steps_text}

Steps already attempted (do NOT suggest these again):
{attempted_steps_text}

Last user message:
{user_message}

Based on the conversation history, decide the next best action.
If the user indicates the problem is fixed (e.g., "Yes that fixed it", "it works", "thank you"), mark intent as "RESOLVED".
If you have tried multiple steps and it's still not working, mark intent as "ESCALATED".
Otherwise, provide the NEXT troubleshooting step or question (intent: "ASK_USER"). Do not repeat steps already attempted.

Respond ONLY with a JSON object in this format:
{{
  "intent": "ASK_USER" | "RESOLVED" | "ESCALATED",
  "message": "The conversational message to show to the user",
  "step_name": "A short summary of the step you are suggesting (if ASK_USER)"
}}"""

    try:
        llm = _get_llm()
        response = llm.invoke(AGENT_PROMPT)
        parsed = _parse_json_response(response.content)
        
        intent = parsed.get("intent", "ASK_USER")
        message = parsed.get("message", "Could you provide more details?")
        step_name = parsed.get("step_name", "Diagnostic step")
        
        if intent == "RESOLVED":
            state["workflow_stage"] = "resolved"
            state["ticket_status"] = "RESOLVED"
            activity.append("✓ Issue successfully resolved!")
            state["messages"].append(AIMessage(content=message))
        elif intent == "ESCALATED" or len(state["completed_steps"]) >= MAX_DIAGNOSTIC_QUESTIONS:
            state["workflow_stage"] = "escalated"
            state["ticket_status"] = "ESCALATED"
            activity.append("✓ Troubleshooting steps exhausted — escalating to ticket")
            message = parsed.get("message", "I will escalate this to a ticket.")
            state["messages"].append(AIMessage(content=message))
        else:
            state["workflow_stage"] = "troubleshooting"
            state["current_step"] = step_name
            if step_name not in state["attempted_steps"]:
                state["attempted_steps"].append(step_name)
            activity.append(f"✓ {step_name}")
            state["messages"].append(AIMessage(content=message))
            
    except Exception as e:
        logger.error(f"Agent turn error: {e}")
        state["messages"].append(AIMessage(content="I encountered an error. Could you describe the issue again?"))

    state["agent_activity"] = activity
    return state
