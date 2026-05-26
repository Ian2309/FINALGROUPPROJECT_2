from ws_client import start_ws

import streamlit as st
import requests

API = "http://127.0.0.1:8000"


def chat_panel():

    st.title("💬 Chat")

    if "active_chat" not in st.session_state:
        st.info("Select a conversation first.")
        return

    chat = st.session_state.active_chat
    convo_id = chat["conversation_id"]
    username = st.session_state.user["username"]

    # RESET WS WHEN CHAT CHANGES
    if "ws_convo_id" not in st.session_state or st.session_state.ws_convo_id != convo_id:
        start_ws(convo_id, username)
        st.session_state.ws_convo_id = convo_id

    # GET CONVERSATION INFO
    res_info = requests.get(f"{API}/conversation/{convo_id}")
    info = res_info.json()

    buyer = info["buyer"]
    seller = info["seller"]

    st.caption(f"Buyer: {buyer} | Seller: {seller}")

    # INIT MESSAGES ONCE
    if "chat_messages" not in st.session_state or st.session_state.ws_convo_id != convo_id:
        res = requests.get(f"{API}/messages/{convo_id}")
        st.session_state.chat_messages = res.json()

    messages = st.session_state.chat_messages

    # CHAT UI
    chat_box = st.container(height=400, border=True)

    with chat_box:
        for m in messages:
            st.chat_message(m["sender"]).write(m["message"])

    # SEND MESSAGE
    msg = st.chat_input("Type message...")

    if msg:

        requests.post(
            f"{API}/send-message",
            json={
                "conversation_id": convo_id,
                "sender": username,
                "message": msg
            }
        )

        st.session_state.chat_messages.append({
            "sender": username,
            "message": msg
        })

        st.rerun()