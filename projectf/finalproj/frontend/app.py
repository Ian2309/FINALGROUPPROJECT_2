import streamlit as st
import requests
import os
import uuid
import websocket
import json

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="RTU Marketplace", layout="wide")

# --- 1. INTIALIZE CORE APP SESSION STATES ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None

# Chat logs collection state
if "messages" not in st.session_state:
    st.session_state.messages = []


# --- 2. LIGHTWEIGHT WEBSOCKET SEND FUNCTION ---
def send_chat_message(username, receiver_id, message_text):
    """Opens a short-lived synchronous websocket connection to deliver the text payload"""
    try:
        ws_url = f"ws://127.0.0.1:8000/ws/chat/{username}"
        ws = websocket.create_connection(ws_url, timeout=3)
        
        payload = {
            "receiver_id": receiver_id if receiver_id else None,
            "message": message_text
        }
        ws.send(json.dumps(payload))
        
        # Immediately capture the echoed response from the server backend
        response = ws.recv()
        if response:
            st.session_state.messages.append(response)
            
        ws.close()
    except Exception as e:
        st.error(f"Chat delivery failed: {e}")


# --- 3. AUTHENTICATION SCREENS ---
if not st.session_state.logged_in:
    st.title("RTU Marketplace")
    choice = st.selectbox("Action", ["Login", "Register"])

    if choice == "Register":
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Register"):
            res = requests.post(f"{API}/register", json={
                "username": username,
                "email": email,
                "password": password
            })
            data = res.json()
            if data["status"] == "success":
                st.session_state.logged_in = True
                st.session_state.user = data["user"]
                st.rerun()
            else:
                st.error(data["message"])
    else:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            res = requests.post(f"{API}/login", json={
                "username": username,
                "password": password
            })
            data = res.json()
            if data["status"] == "success":
                st.session_state.logged_in = True
                st.session_state.user = data["user"]
                st.rerun()
            else:
                st.error(data["message"])


# --- 4. MAIN DASHBOARD PANELS ---
else:
    st.sidebar.title("RTU Marketplace")
    menu = st.sidebar.radio(
        "Navigation",
        ["Home", "Profile", "Selling", "Buying", "Chat", "Logout"]
    )

    username = st.session_state.user["username"]

    # --- TAB: HOME ---
    if menu == "Home":
        st.title(f"Welcome, {username}")
        st.subheader("Latest Products")
        res = requests.get(f"{API}/products")

        if res.status_code == 200:
            products = res.json()[::-1]
            for p in products:
                st.subheader(p["product_type"])
                st.write("Seller:", p["owner_username"])
                st.write("Price:", p["price"])
                st.write("Description:", p["description"])

                if p.get("images"):
                    for img in p["images"].split(","):
                        st.image(f"uploads/{img}", width=200)

                is_owner = p["owner_username"] == username
                if is_owner:
                    st.info("This is your product")
                else:
                    if st.button("Buy", key=f"buy_{p['id']}"):
                        buy_res = requests.post(f"{API}/buy-product", json={
                            "product_id": p["id"],
                            "buyer_username": username
                        })
                        if buy_res.status_code == 200:
                            st.success("Purchased successfully!")
                        else:
                            try:
                                st.error(buy_res.json().get("message"))
                            except:
                                st.error("Purchase failed")
                st.divider()

    # --- TAB: PROFILE ---
    elif menu == "Profile":
        st.title("Profile Center")
        tab1, tab2, tab3 = st.tabs(["My Listings", "My Purchases", "My Sales"])

        with tab1:
            st.subheader("My Products")
            res = requests.get(f"{API}/my-products/{username}")
            if res.status_code == 200:
                for p in res.json():
                    st.write("🛒", p["product_type"])
                    st.write("Price:", p["price"])
                    if p.get("images"):
                        for img in p["images"].split(","):
                            st.image(f"uploads/{img}", width=120)
                    st.divider()

        with tab2:
            st.subheader("Bought Items")
            res = requests.get(f"{API}/my-transactions/{username}")
            if res.status_code == 200:
                for t in res.json():
                    if t["buyer_username"] == username:
                        st.success("Purchased")
                        st.write("Product:", t["product_name"])
                        st.write("Seller:", t["seller_username"])
                        st.write("Price:", t["price"])
                        st.divider()

        with tab3:
            st.subheader("Sold Items")
            res = requests.get(f"{API}/my-transactions/{username}")
            if res.status_code == 200:
                for t in res.json():
                    if t["seller_username"] == username:
                        st.warning("Sold")
                        st.write("Product:", t["product_name"])
                        st.write("Buyer:", t["buyer_username"])
                        st.write("Price:", t["price"])
                        st.divider()

    # --- TAB: SELLING ---
    elif menu == "Selling":
        st.title("Selling Panel")
        product_type = st.selectbox("Product Type", ["Uniform", "Books", "Others"])
        description = st.text_area("Description")
        price = st.number_input("Price (₱)", min_value=0.0)
        uploaded_files = st.file_uploader("Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

        def save_images(files):
            os.makedirs("uploads", exist_ok=True)
            names = []
            for f in files:
                name = f"{uuid.uuid4()}_{f.name}"
                path = f"uploads/{name}"
                with open(path, "wb") as file:
                    file.write(f.getbuffer())
                names.append(name)
            return ",".join(names)

        if st.button("Post Product"):
            images = save_images(uploaded_files) if uploaded_files else ""
            res = requests.post(f"{API}/add-product", json={
                "product_type": product_type,
                "description": description,
                "price": price,
                "owner_username": username,
                "images": images,
                "uniform_type": "",
                "book_title": "",
                "product_name": product_type,
                "size": ""
            })
            if res.status_code == 200:
                st.success("Posted successfully!")
            else:
                st.error(res.text)

    # --- TAB: BUYING ---
    elif menu == "Buying":
        st.title("Browse Products")
        res = requests.get(f"{API}/products")
        if res.status_code == 200:
            for p in res.json():
                st.subheader(p["product_type"])
                st.write("Seller:", p["owner_username"])
                st.write("Price:", p["price"])
                if p.get("images"):
                    for img in p["images"].split(","):
                        st.image(f"uploads/{img}", width=200)
                st.divider()

    # --- TAB: CHAT ROOM ---
    elif menu == "Chat":
        st.title("💬 RTU Marketplace Chat Room")
        st.caption(f"Logged in as: **{username}**")
        st.markdown("---")
        
        receiver_id = st.text_input("Recipient Username (Leave blank to broadcast):", placeholder="e.g., JaneDoe").strip()
        
        st.subheader("Chat Log")
        chat_container = st.container(height=350, border=True)
        with chat_container:
            if not st.session_state.messages:
                st.info("No active messages in your history loop yet.")
            for msg in st.session_state.messages:
                st.write(msg)
                
        # Chat Input Form Layout
        with st.form("send_msg_form", clear_on_submit=True):
            input_message = st.text_input("Type message here...", placeholder="Is this available?")
            send_click = st.form_submit_button("Send Message")
            
            if send_click and input_message:
                # Delivers package securely via state-safe transmission pipeline
                send_chat_message(username, receiver_id, input_message)
                st.rerun()

    # --- TAB: LOGOUT ---
    elif menu == "Logout":
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.messages = []
        st.rerun()