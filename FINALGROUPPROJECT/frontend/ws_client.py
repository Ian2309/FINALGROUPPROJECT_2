import websocket
import threading
import json
import streamlit as st


def start_ws(conversation_id, username):

    # ensure session state exists
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    def on_message(ws, message):
        try:
            data = json.loads(message)

            st.session_state.chat_messages.append(data)

        except Exception as e:
            print("WS message error:", e)

    def on_open(ws):
        # optional: send user info on connect
        ws.send(json.dumps({
            "type": "join",
            "conversation_id": conversation_id,
            "username": username
        }))

    ws_url = f"ws://192.168.100.17:8000/chat/ws/{conversation_id}"

    ws = websocket.WebSocketApp(
        ws_url,
        on_message=on_message,
        on_open=on_open
    )

    thread = threading.Thread(target=ws.run_forever, daemon=True)
    thread.start()

    return ws