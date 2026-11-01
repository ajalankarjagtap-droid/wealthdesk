"""
wealthdesk/nodes.py
-------------------
Node functions for the WealthDesk graph.

Session 2 upgrade: respond() now reads conversation history from state and
returns the updated history so the checkpointer can persist it.
"""
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from .config import SYSTEM_PROMPT
from .state import WealthDeskState
from .tools import llm


# ---------------------------------------------------------------------------
# TODO 2 of 4 -- update respond() to use history
# ---------------------------------------------------------------------------
# Upgrade respond() so it:
#
#   1. Reads history from state (default to empty list if not yet present):
#        history = state.get("history", [])
#
#   2. Builds a messages list starting with the system prompt, then replays
#      every past turn, then appends the current user message:
#        messages = [SystemMessage(content=SYSTEM_PROMPT)]
#        for turn in history:
#            if turn["role"] == "user":
#                messages.append(HumanMessage(content=turn["content"]))
#            else:
#                messages.append(AIMessage(content=turn["content"]))
#        messages.append(HumanMessage(content=state["customer_message"]))
#
#   3. Calls the LLM inside a try / except block (same as Session 1).
#
#   4. Appends both the user turn and the assistant turn to history and
#      returns the complete updated list alongside the response:
#        new_history = history + [
#            {"role": "user",      "content": state["customer_message"]},
#            {"role": "assistant", "content": response_text},
#        ]
#        return {"response": response_text, "history": new_history}
#
#   WHY return the full list?
#   LangGraph replaces the history field with whatever the node returns.
#   If you only returned the two new turns, history would shrink to 2 items
#   on every call. Returning the full updated list keeps everything.
#
# ---------------------------------------------------------------------------

def respond(state: WealthDeskState) -> dict:
    history = state.get("history", [])
    """Call the LLM and return the agent's reply."""
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    for turn in history:
            if turn["role"] == "user":
                messages.append(HumanMessage(content=turn["content"]))
            else:
                messages.append(AIMessage(content=turn["content"]))
    messages.append(HumanMessage(content=state["customer_message"]))
   
    try:
      result = llm.invoke(messages)
      llm_response = result.content;
      new_history = history + [
          {"role": "user", "content": state["customer_message"]},
          {"role": "assistant", "content": llm_response}
      ]
      return {"response": llm_response, "history": new_history}
    except Exception as e:
       print(f"Wealthdesk error: {e}")
       return {"response": "I am temporarily unavailable. Please try after some time."}
 
 