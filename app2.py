import streamlit as st
import requests

# =============================================================================
# Load configuration from secrets
# =============================================================================
# api_key = st.secrets.get("api_key", "")
# model_used = st.secrets.get("model_used", "gpt-4o-mini")
# kb_list = st.secrets.get("kb_list", ["<knowledge_base_id>"])  # List of KB IDs
api_key = 'flo_c6cca60e3421694ac6c97fbaf9d810b96cf4e369c8e5e1d993a35b7673647b1d'
model_used = 'gpt-4o-mini'
kb_list = 'c0fe3f96-ab59-4345-bd19-99e0eb7cf053'

st.title("Flowith Knowledge Chat Interface")
"""
Updated for Flowith Knowledge Retrieval API (Non-Streaming)
"""

# =============================================================================
# Session state initialization
# =============================================================================
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "system_set" not in st.session_state:
    st.session_state["system_set"] = False

# =============================================================================
# Updated API call function for Flowith
# =============================================================================
def fetch_knowledge_response(api_key, messages, model, kb_list):
    """
    Calls Flowith Knowledge Retrieval API (Non-Streaming)
    """
    url = "https://edge.flowith.net/external/use/seek-knowledge"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Host": "edge.flowith.net"
    }
    payload = {
        "messages": messages,
        "model": model,
        "stream": False,
        "kb_list": kb_list
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        res = response.json()
        
        if res.get("tag") == "final":
            return res.get("content", "No content found in response")
        else:
            return "Unexpected response format from API"
            
    except requests.RequestException as e:
        return f"API Request failed: {str(e)}"
    except Exception as e:
        return f"Error processing response: {str(e)}"

# =============================================================================
# System Prompt Setup
# =============================================================================
# if not st.session_state["system_set"]:
#     system_prompt_input = st.text_area("System Prompt", "You are a helpful assistant that uses knowledge base content")
#     if st.button("Initialize System"):
#         st.session_state["system_set"] = True
#         st.session_state["messages"].insert(0, {
#             "role": "system",
#             "content": system_prompt_input
#         })

# =============================================================================
# Chat Interface
# =============================================================================
# if st.session_state["system_set"]:
user_input = st.chat_input("Type your message")

if user_input:
    # Add user message to history
    st.session_state["messages"].append({"role": "user", "content": user_input})
    
    # Display conversation history
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Get API response
    response = fetch_knowledge_response(
        api_key=api_key,
        messages=st.session_state["messages"],
        model=model_used,
        kb_list=[kb_list]
    )
    
    # Add assistant response to history
    st.session_state["messages"].append({"role": "assistant", "content": response})
    
    # Display new response
    with st.chat_message("assistant"):
        st.markdown(response)