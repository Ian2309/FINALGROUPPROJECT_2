import streamlit as st
import requests
import os
import uuid
import websocket
import json

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="RTU Marketplace", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "messages" not in st.session_state:
    st.session_state.messages = []

def send_silent_intro(username, receiver_id, message_text):
    """Fires a one-off socket context hit from the Browse section click events"""
    try:
        ws_url = f"ws://127.0.0.1:8000/ws/chat/{username}"
        ws = websocket.create_connection(ws_url, timeout=2)
        payload = {"receiver_id": receiver_id, "message": message_text}
        ws.send(json.dumps(payload))
        ws.close()
    except Exception as e:
        pass

# --- AUTH SELECTION WINDOW ---
if not st.session_state.logged_in:
    st.title("RTU Marketplace")
    choice = st.selectbox("Action", ["Login", "Register"])

    if choice == "Register":
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Register"):
            res = requests.post(f"{API}/register", json={"username": username, "email": email, "password": password})
            data = res.json()
            if data.get("status") == "success":
                st.session_state.logged_in = True
                st.session_state.user = data["user"]
                st.rerun()
            else:
                st.error("Registration failed.")
    else:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            res = requests.post(f"{API}/login", json={"username": username, "password": password})
            if res.status_code == 200:
                data = res.json()
                st.session_state.logged_in = True
                st.session_state.user = data["user"]
                st.rerun()
            else:
                st.error("Invalid credentials.")

# --- ROUTED MAIN CONTEXT PANELS ---
else:
    st.sidebar.title("RTU Marketplace")
    menu = st.sidebar.radio("Navigation", ["Home", "Profile", "Selling", "Buying", "Chat", "Logout"])
    username = st.session_state.user["username"]

    # --- TAB: HOME FEED ---
    if menu == "Home":
        st.title(f"Welcome, {username} 👋")
        st.subheader("Recent Feed Listings")
        res = requests.get(f"{API}/products")
        if res.status_code == 200:
            for p in res.json()[::-1]:
                st.markdown(f"### {p['product_type']}")
                st.write(f"Owner: `{p['owner_username']}` | Price: **₱{p['price']}**")
                st.write(p["description"])
                st.divider()

    # --- TAB: PROFILE STATS ---
    elif menu == "Profile":
        st.title("User Profile Dashboard")
        t1, t2, t3 = st.tabs(["Active Listings", "Purchased Ledger", "Sales Revenue"])
        
        with t1:
            res = requests.get(f"{API}/my-products/{username}")
            if res.status_code == 200:
                for p in res.json():
                    status_lbl = "🔴 Sold" if p["is_sold"] else "🟢 Active"
                    st.write(f"**{p['product_type']}** - ₱{p['price']} ({status_lbl})")
        with t2:
            res = requests.get(f"{API}/my-transactions/{username}")
            if res.status_code == 200:
                for t in res.json():
                    if t["buyer_username"] == username:
                        st.write(f"Bought **{t['product_name']}** from `{t['seller_username']}` for ₱{t['price']}")
        with t3:
            res = requests.get(f"{API}/my-transactions/{username}")
            if res.status_code == 200:
                for t in res.json():
                    if t["seller_username"] == username:
                        st.write(f"Sold **{t['product_name']}** to `{t['buyer_username']}` for ₱{t['price']}")

    # --- TAB: SELLING POST ---
    elif menu == "Selling":
        st.title("Post a New Listing")
        product_type = st.selectbox("Product Type", ["Uniform", "Books", "Others"])
        description = st.text_area("Description")
        price = st.number_input("Price (₱)", min_value=0.0)
        uploaded_files = st.file_uploader("Upload Images", accept_multiple_files=True)

        if st.button("Post Product"):
            res = requests.post(f"{API}/add-product", json={
                "product_type": product_type,
                "description": description,
                "price": price,
                "owner_username": username,
                "images": ""
            })
            if res.status_code == 200:
                st.success("Listing published successfully!")
                st.rerun()

    # --- TAB: MARKETPLACE SELECTION ---
    elif menu == "Buying":
        st.title("🛍️ Browse Marketplace Products")
        res = requests.get(f"{API}/products")
        if res.status_code == 200:
            products = res.json()
            if not products:
                st.info("No products currently available.")
            for p in products:
                c1, c2 = st.columns([2, 1], gap="medium")
                with c1:
                    st.subheader(f"🏷️ {p['product_type']}")
                    st.write(f"**Seller:** `{p['owner_username']}` | **Price:** ₱{p['price']:.2f}")
                    st.write(p["description"])
                with c2:
                    if p["owner_username"] == username:
                        st.info("Your listing")
                    else:
                        if st.button("🛒 Buy Now", key=f"b_{p['id']}", use_container_width=True):
                            br = requests.post(f"{API}/buy-product", json={"product_id": int(p["id"]), "buyer_username": username})
                            if br.status_code == 200:
                                st.success("Item purchased!")
                                st.rerun()
                        if st.button("💬 Chat Seller", key=f"c_{p['id']}", use_container_width=True):
                            intro = f"Hi! I want to buy your '{p['product_type']}' for ₱{p['price']}."
                            send_silent_intro(username, p['owner_username'], intro)
                            st.info(f"Message sent! Go to the Chat panel to speak with {p['owner_username']}.")
                st.divider()

    # --- TAB: REAL-TIME WEBSOCKET CHAT ROOM ---
    elif menu == "Chat":
        st.title("💬 Live Chat Room")
        st.caption(f"Logged in as: **{username}**")
        
        receiver_id = st.text_input("Recipient Username (Leave blank to broadcast):").strip()
        
        # 1. Maintain or establish a single background connection block instance
        ws_url = f"ws://127.0.0.1:8000/ws/chat/{username}"
        if "ws_connection" not in st.session_state:
            try:
                st.session_state.ws_connection = websocket.create_connection(ws_url, timeout=1)
                st.session_state.messages = []  # Fresh session reload context sync
            except Exception as e:
                st.error(f"Could not connect to live chat stream channel: {e}")

        # 2. Continually read background buffer frames
        if "ws_connection" in st.session_state and st.session_state.ws_connection:
            try:
                st.session_state.ws_connection.settimeout(0.1)
                while True:
                    new_incoming = st.session_state.ws_connection.recv()
                    if new_incoming and new_incoming not in st.session_state.messages:
                        st.session_state.messages.append(new_incoming)
            except websocket.WebSocketTimeoutException:
                pass
            except Exception:
                st.session_state.ws_connection = None

        # 3. Print out complete conversation logs inside frame
        chat_container = st.container(height=320, border=True)
        with chat_container:
            if not st.session_state.messages:
                st.info("No active chat messages here yet.")
            for msg in st.session_state.messages:
                st.write(msg)
                
        # 4. Input forms send down to the persistent background loop
        with st.form("chat_form", clear_on_submit=True):
            txt = st.text_input("Type message...")
            if st.form_submit_button("Send Message") and txt:
                if "ws_connection" in st.session_state and st.session_state.ws_connection:
                    try:
                        payload = {
                            "receiver_id": receiver_id if receiver_id else None,
                            "message": txt
                        }
                        st.session_state.ws_connection.send(json.dumps(payload))
                        
                        # Add message directly to local session display
                        lbl = f"🔒 [Private to {receiver_id}]: {txt}" if receiver_id else f"💬 {username}: {txt}"
                        st.session_state.messages.append(lbl)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Message dropped: {e}")
                else:
                    st.error("Socket error. Reconnecting...")
                    st.session_state.pop("ws_connection", None)
                    st.rerun()

    # --- TAB: LOGOUT CLEANUP ---
    elif menu == "Logout":
        if "ws_connection" in st.session_state and st.session_state.ws_connection:
            try:
                st.session_state.ws_connection.close()
            except:
                pass
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.messages = []
        st.session_state.pop("ws_connection", None)
        st.rerun()