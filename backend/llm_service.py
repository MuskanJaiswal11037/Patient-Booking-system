"""
LLM Service with LangChain Deep Agent for Hospital Management System.

This module creates a Deep Agent that:
- Understands the database schema
- Uses execute_sql_query tool to query data
- Generates appropriate SQL queries based on user requests
"""

import atexit
from datetime import datetime
import logging
from typing import Optional, Any, Dict, List
import json
import uuid
from langchain.tools import tool
from deepagents import create_deep_agent
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langgraph import func
from backend.config import settings
from .utils import DatabaseHandler, DatabaseException
from .utils.prompts import get_system_prompt
from langgraph.checkpoint.postgres import PostgresSaver
from .tools import execute_sql_query, insert_update_appointment_status, insert_feedback, insert_update_doctor_availability, insert_medical_record, resolve_user_identity, retrieve_medical_records
logger = logging.getLogger(__name__)
from langchain_google_genai import ChatGoogleGenerativeAI


def _normalize_llm_text(content: Any) -> str:
    """Convert LangChain / Gemini message content to plain text."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        chunks = []
        for item in content:
            if isinstance(item, dict):
                if 'text' in item and item['text']:
                    chunks.append(str(item['text']))
                elif 'content' in item and item['content']:
                    chunks.append(_normalize_llm_text(item['content']))
                else:
                    chunks.append(str(item))
            elif hasattr(item, 'text') and item.text:
                chunks.append(str(item.text))
            else:
                chunks.append(str(item))
        return "\n".join(part for part in chunks if part)
    if isinstance(content, dict):
        for key in ("text", "content"):
            if key in content and content[key] is not None:
                return _normalize_llm_text(content[key])
        return json.dumps(content, ensure_ascii=False)
    return str(content)


SUPPORTED_GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]


def get_gemini_model_name() -> str:
    requested_model = getattr(settings, "GEMINI_MODEL", None) or "gemini-2.5-flash"
    if requested_model in SUPPORTED_GEMINI_MODELS:
        return requested_model

    if requested_model == "gemini-pro":
        return "gemini-1.5-flash"

    return "gemini-2.5-flash"


#Initialize LLM model.
llm = ChatGoogleGenerativeAI(
        model=get_gemini_model_name(),
        temperature=0,
        google_api_key=settings.GEMINI_API_KEY
    )

user_role = ""

# ══════════════════════════════════════════════════════════════════
# SQL QUERY TOOL
# ══════════════════════════════════════════════════════════════════

# lanchain_pg_conn = DatabaseHandler(settings.DATABASE_URL).get_connection()

lanchain_checkpoint_creator = PostgresSaver.from_conn_string(settings.LANGCHAIN_PG_URL)
lanchain_checkpoint = lanchain_checkpoint_creator.__enter__()
atexit.register(lanchain_checkpoint_creator.__exit__, None, None, None)  # Ensure connection is closed on exit



# ══════════════════════════════════════════════════════════════════
# DEEP AGENT
# ══════════════════════════════════════════════════════════════════


def create_deep_agent_for_hospital(user_email: str = "test_user@test.com", user_role: str = "patient"):
    """
    Create Deep Agent with database schema knowledge.
    
    Parameters
    ----------
    user_email : str
        Email of the user interacting with the agent
    user_role : str
        Role of the user interacting with the agent (e.g., "patient", "doctor", "nurse", "admin")
    """
    tools = [execute_sql_query, insert_update_appointment_status, insert_feedback, insert_update_doctor_availability, insert_medical_record, retrieve_medical_records, insert_medical_record, retrieve_medical_records, resolve_user_identity]
    print("++++++++++++++++++++++++++++++++++++++++++   " + user_role  )
    system_prompt = "System Prompt: " +  get_system_prompt(user_role, user_email)
    lanchain_checkpoint.setup()  # Create tables if they don't exist
    agent = create_deep_agent(
        tools=tools,
        system_prompt=system_prompt,
        model=llm,
        checkpointer=lanchain_checkpoint
    )
    return agent


# ══════════════════════════════════════════════════════════════════
# CHAT INTERFACE
# ══════════════════════════════════════════════════════════════════


def chat_with_deep_agent(user_message: str, user_email: str = "test_user@test.com", user_role: str = "patient") -> Dict[str, Any]:
    """
    Chat with the Deep Agent for hospital queries.

    Args:
        user_message: User's query
        user_email: Email of the user interacting with the agent
        role: Role of the user

    Returns:
        Dictionary with response and metadata
    """
    try:
        agent = create_deep_agent_for_hospital(user_email=user_email, user_role=user_role)
        messages = [{"role": "user", "content": user_message}]

        response = agent.invoke(
            {"messages": messages},
            config={
                "configurable": {
                    "thread_id": user_email
                },
            }
        )

        print("Agent Response:", response)
        logger.info("Agent response: %s", response)

        reply = response.get("messages", [])[-1].content if response.get("messages") else ""
        return {
            "success": True,
            "reply": _normalize_llm_text(reply),
            "used_tool": True,
        }
    
    except Exception as e:
        error_message = str(e)
        print(error_message)
        logger.error(f"Error in chat_with_deep_agent: {error_message}")

        return {
            "success": False,
            "reply": f"Error: {error_message}",
            "used_tool": False,
        }


if __name__ == "__main__":
    # Example usage
    user_query = "I am having fever. Can u suggeest me some good doctors"
    # user_query = "Hi"
    result = chat_with_deep_agent(user_query)
    print(json.dumps(result, indent=2))

