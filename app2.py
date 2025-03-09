import streamlit as st
import requests
import json

# =============================================================================
# Load configuration from secrets
# =============================================================================
# api_key = st.secrets.get("api_key", "")
# model_used = st.secrets.get("model_used", "gpt-4o-mini")
# kb_id = st.secrets.get("kb_id", "")  # Add knowledge base ID to secrets
api_key = 'flo_c6cca60e3421694ac6c97fbaf9d810b96cf4e369c8e5e1d993a35b7673647b1d'
model_used = 'gpt-4o-mini'
kb_id = 'c0fe3f96-ab59-4345-bd19-99e0eb7cf053'

st.title("ChatBox – Knowledge-Enhanced Agent")
"""11.2.2025 by Simon, Xu"""

# =============================================================================
# Session state initialization
# =============================================================================
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "system_set" not in st.session_state:
    st.session_state["system_set"] = False

# =============================================================================
# Updated API call function with knowledge retrieval
# =============================================================================
def fetch_knowledge_response(api_key, messages, model, kb_list):
    """
    Calls the Knowledge Retrieval API and processes streaming response
    Returns tuple: (final_content, seeds, error)
    """
    url = "https://edge.flowith.net/external/use/seek-knowledge"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "messages": messages,
        "model": model,
        "stream": False,
        "kb_list": kb_list
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, stream=False)
        response.raise_for_status()
        
        seeds = []
        final_content = ""
        
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('data:'):
                    json_str = decoded_line[5:].strip()
                    try:
                        data = json.loads(json_str)
                        if data.get('tag') == 'seeds':
                            seeds.extend(data['content'])
                        elif data.get('tag') == 'final':
                            final_content = data['content']
                    except json.JSONDecodeError:
                        continue
        
        return (final_content, seeds, None)
        
    except requests.RequestException as e:
        return (None, [], f"API Request Error: {str(e)}")
    except Exception as e:
        return (None, [], f"Processing Error: {str(e)}")

# =============================================================================
# System Prompt Setup (Remains unchanged)
# =============================================================================
if not st.session_state["system_set"]:
    system_prompt_input = st.text_area("System Prompt", "")
    if st.button("Set System Prompt"):
        st.session_state["system_set"] = True
        st.session_state["system_prompt"] = system_prompt_input
        st.session_state["messages"].insert(0, 
            {"role": "developer", "content": system_prompt_input})

# =============================================================================
# Chat Interface with Knowledge Integration
# =============================================================================
if st.session_state["system_set"]:
    user_input = st.chat_input("Your message")
    if user_input:
        # Update conversation history
        st.session_state["messages"].append({"role": "user", "content": user_input})
        
        # Display conversation history
        for message in st.session_state["messages"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Get knowledge-enhanced response
        final_content, seeds, error = fetch_knowledge_response(
            api_key,
            st.session_state["messages"],
            model_used,
            [kb_id]  # Use knowledge base from secrets
        )
        
        if error:
            st.error(error)
        else:
            # Integrate seeds into response
            knowledge_snippets = "\n".join(
                [f"📚 Source {i+1}: {seed['content']}" 
                 for i, seed in enumerate(seeds)])
            
            full_response = f"{final_content}\n\n{knowledge_snippets}"
            
            # Update session state and display
            st.session_state["messages"].append(
                {"role": "assistant", "content": full_response})
            
            with st.chat_message("assistant"):
                st.markdown(full_response)
