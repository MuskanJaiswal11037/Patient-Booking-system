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
from .tools import execute_sql_query, insert_update_appointment_status, insert_feedback, insert_update_doctor_availability, insert_medical_record, resolve_user_identity, retrieve_medical_records, get_today_date, retrieve_all_users, check_doctor_availability, get_waiting_time, get_doctor_available_slots
logger = logging.getLogger(__name__)


#Initialize LLM model.
llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=settings.OPENAI_API_KEY,
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
    tools = [execute_sql_query, insert_update_appointment_status, insert_feedback, insert_update_doctor_availability, insert_medical_record, retrieve_medical_records, insert_medical_record, retrieve_medical_records, resolve_user_identity, get_today_date, retrieve_all_users, check_doctor_availability, get_waiting_time, get_doctor_available_slots]
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
        
        # Check if this is the first message by looking at the checkpoint state
        thread_config = {"configurable": {"thread_id": user_email}}
        
        # Try to get existing state to determine if it's the first message
        is_first_message = True
        try:
            # Get the checkpoint state to see if there are existing messages
            existing_state = agent.get_state(thread_config)
            if existing_state and existing_state.values and "messages" in existing_state.values:
                if len(existing_state.values["messages"]) > 0:
                    is_first_message = False
        except Exception as e:
            logger.debug(f"Could not check checkpoint state: {e}")
            is_first_message = True
        
        # If it's the first message, automatically retrieve all users
        if is_first_message:
            logger.info(f"First message detected from {user_email}, retrieving all users...")
            try:
                from .tools import retrieve_all_users as retrieve_users_func
                users_data = retrieve_users_func()
                logger.info(f"Retrieved {users_data.get('total_users', 0)} users")
            except Exception as e:
                logger.warning(f"Could not retrieve users on first message: {e}")
        
        messages = [{"role": "user", "content": user_message}]

        response = agent.invoke(
            {"messages": messages},
            config=thread_config
        )

        print("Agent Response:", response)
        logger.info("Agent response: %s", response)
        return {
            "success": True,
            "reply": response["messages"][-1].content,
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

