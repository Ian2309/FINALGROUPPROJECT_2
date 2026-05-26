#frontend/ws_client.py
import websocket
import threading
import json
import streamlit as st

def start_ws(conversation_id, username):

    def on_message(ws, message):
        data = json.loads(message)

        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []

        st.session_state.chat_messages.append(data)

    def run():
        ws = websocket.WebSocketApp(
            f"ws://127.0.0.1:8000/chat/ws/{conversation_id}",
            on_message=on_message
        )
        ws.run_forever()

    thread = threading.Thread(target=run, daemon=True)
    thread.start()