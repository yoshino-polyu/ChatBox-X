import streamlit as st
import requests
import toml

# =============================================================================
# Load configuration from the TOML settings file
# =============================================================================
# try:
#     credentials = toml.load("secrets")
# except Exception as e:
#     st.error(f"Error loading settings file: {e}")
#     st.stop()

# Extract API/access settings
api_key = st.secrets.get("api_key", "")
model_used = st.secrets.get("model_used", "o3-mini")
reasoning_effort = st.secrets.get("reasoning_effort", "high")
max_completion_tokens = st.secrets.get("max_completion_tokens", 45000)

st.title("ChatBox – Agent Powered by o3-mini with High Reasoning Effort")
"""
11.2.2025 by Simon, Xu
"""

# =============================================================================
# Session state initialization
# =============================================================================
if "messages" not in st.session_state:
    # This list holds the entire conversation.
    st.session_state["messages"] = []  # our conversation context

if "system_set" not in st.session_state:
    # Flag to indicate whether the system prompt has been provided.
    st.session_state["system_set"] = False

# =============================================================================
# Agent API call function
# =============================================================================
def fetch_chat_response(api_key, messages, model, reasoning_effort, max_completion_tokens):
    """
    Call the agent API with the provided conversation history.
    The API endpoint is https://aigptx.top/v1/chat/completions and the syntax
    (messages, model, etc.) is assumed to be the same as the OpenAI API.
    """
    url = "https://aigptx.top/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "messages": messages,
        "model": model,
        "reasoning_effort": reasoning_effort,
        "max_completion_tokens": max_completion_tokens
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        res = response.json()
        response_content = res["choices"][0]["message"]["content"]
        finish_reason = res["choices"][0]["finish_reason"]
        completion_tokens = res["usage"]["completion_tokens"]
        total_tokens = res["usage"]["total_tokens"]
        return (response_content, finish_reason, completion_tokens, total_tokens)
    except requests.RequestException as e:
        return (f"HTTP Request failed: {e}", "", 0, 0)
    except (KeyError, IndexError) as e:
        return (f"Unexpected response structure: {e}", "", 0, 0)

# =============================================================================
# System Prompt Setup (Input by User)
# =============================================================================
if not st.session_state["system_set"]:
    # Ask the user for the system prompt. (This part runs only until the prompt is set.)
    system_prompt_input = st.text_area(
        "Ststem Prompt",
        ""
    )
    if st.button("Set System Prompt"):
        st.session_state["system_set"] = True
        st.session_state["system_prompt"] = system_prompt_input
        # Insert the system prompt as the very first message in the context.
        st.session_state["messages"].insert(0, {"role": "developer", "content": system_prompt_input})
        # print("messages in session state: ", st.session_state["messages"])
        # temporarily show the system prompt
        if st.session_state.get("messages"):
          last_message = st.session_state["messages"][-1]
          with st.chat_message(last_message["role"]):
              st.markdown(last_message["content"])


# =============================================================================
# Chat Input – Accept new user messages if the system prompt is set.
# =============================================================================
if st.session_state["system_set"]:
    user_input = st.chat_input("Your message")
    if user_input:
        # Append the user message to conversation history.
        st.session_state["messages"].append({"role": "user", "content": user_input})
        # print("messages in session state: ", st.session_state["messages"])
        
        # st.markdown in this position will clear previous conversation. so everytime at this position, show the whole conversation history. 
        for message in st.session_state.get("messages", []):
            with st.chat_message(message["role"]):
                st.text(message["content"]) # single newlines are treated as a space in standard markdown. 
        
        # Call the agent API using the full conversation as context.
        response_data = fetch_chat_response(
            api_key,
            st.session_state["messages"],
            model_used,
            reasoning_effort,
            max_completion_tokens
        )
        assistant_response = response_data[0]
        
        # Append the assistant's reply to the conversation history.
        st.session_state["messages"].append({"role": "assistant", "content": assistant_response})
        # print("messages in session state: ", st.session_state["messages"])
        
        # By default ChatGPT outputs MarkDown syntax text. 
        # temporarily show the assistant's reply.
        with st.chat_message("assistant"):
            st.markdown(assistant_response)

        # Optionally, display additional debug info (finish reason, token count, etc.)
        st.write(f"Finish reason: {response_data[1]}, Completion tokens: {response_data[2]}, Total tokens: {response_data[3]}")