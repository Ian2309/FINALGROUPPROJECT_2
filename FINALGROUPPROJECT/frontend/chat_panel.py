#frontend/chat_panel.py
import streamlit as st
import requests

from ws_client import start_ws

API = "http://127.0.0.1:8000"


def chat_panel():

    st.title("💬 Chat")

    # CHECK ACTIVE CHAT
    if "active_chat" not in st.session_state:
        st.info("Select a conversation first.")
        return

    chat = st.session_state.active_chat
    convo_id = chat.get("conversation_id")
    username = st.session_state.user.get("username")

    if not convo_id:
        st.error("Invalid conversation.")
        return

    # =========================
    # WEBSOCKET INIT (ON CHANGE ONLY)
    # =========================
    if (
        "ws_convo_id" not in st.session_state
        or st.session_state.ws_convo_id != convo_id
    ):
        start_ws(convo_id, username)
        st.session_state.ws_convo_id = convo_id

    # =========================
    # GET CONVERSATION INFO
    # =========================
    try:
        res_info = requests.get(f"{API}/chat/conversation/{convo_id}")
        info = res_info.json()
    except Exception as e:
        st.error("Failed to connect to server")
        st.write(str(e))
        return

    # SAFE RESPONSE CHECK
    if info.get("status") != "success":
        st.error(info.get("message", "Failed to load conversation"))
        st.write(info)
        return

    buyer = info.get("buyer", "")
    seller = info.get("seller", "")

    st.caption(f"Buyer: {buyer} | Seller: {seller}")

    # =========================
    # INIT MESSAGES
    # =========================
    if (
        "chat_messages" not in st.session_state
        or st.session_state.ws_convo_id != convo_id
    ):
        try:
            res = requests.get(f"{API}/messages/{convo_id}")
            st.session_state.chat_messages = res.json()
        except Exception:
            st.session_state.chat_messages = []

    messages = st.session_state.chat_messages

    # =========================
    # CHAT DISPLAY
    # =========================
    chat_box = st.container(height=400, border=True)

    with chat_box:
        for m in messages:
            st.chat_message(m.get("sender", "unknown")).write(
                m.get("message", "")
            )

    # =========================
    # SEND MESSAGE
    # =========================
    msg = st.chat_input("Type message...")

    if msg:

        try:
            requests.post(
                f"{API}/send-message",
                json={
                    "conversation_id": convo_id,
                    "sender": username,
                    "message": msg
                }
            )
        except Exception:
            st.error("Failed to send message")
            return

        st.session_state.chat_messages.append({
            "sender": username,
            "message": msg
        })

        st.rerun()