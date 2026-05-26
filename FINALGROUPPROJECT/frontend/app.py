# app.py
import streamlit as st
import requests
import os
import uuid
from profile_components import user_header
from chat_panel import chat_panel
from cancel_panel import cancel_order
from ws_client import start_ws   

API = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="RTU Marketplace",
    layout="wide"
)

# ==========================================
# SESSION STATE
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "logout_confirm" not in st.session_state:
    st.session_state.logout_confirm = False


# ==========================================
# SAVE IMAGES FUNCTION
# ==========================================
def save_images(files):

    os.makedirs("uploads", exist_ok=True)

    names = []

    for f in files:

        filename = f"{uuid.uuid4()}_{f.name}"
        path = f"uploads/{filename}"

        with open(path, "wb") as file:
            file.write(f.getbuffer())

        names.append(filename)

    return ",".join(names)


# ==========================================
# AUTH PAGE
# ==========================================
if not st.session_state.logged_in:

    st.title("RTU Marketplace")

    choice = st.selectbox(
        "Action",
        ["Login", "Register"]
    )

    # ==========================================
    # REGISTER
    # ==========================================
    if choice == "Register":

        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Register"):

            res = requests.post(
                f"{API}/register",
                json={
                    "username": username,
                    "email": email,
                    "password": password
                }
            )

            data = res.json()

            if data["status"] == "success":

                st.session_state.logged_in = True
                st.session_state.user = data["user"]

                st.rerun()

            else:
                st.error(data["message"])

    # ==========================================
    # LOGIN
    # ==========================================
    else:

        username = st.text_input("Username")

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login"):

            res = requests.post(
                f"{API}/login",
                json={
                    "username": username,
                    "password": password
                }
            )

            data = res.json()

            if data["status"] == "success":

                st.session_state.logged_in = True
                st.session_state.user = data["user"]

                st.rerun()

            else:
                st.error(data["message"])


# ==========================================
# DASHBOARD
# ==========================================
else:

    st.sidebar.title("RTU Marketplace")

    menu = st.sidebar.radio(
        "Navigation",
        ["Home", "Profile", "Selling", "Buying", "Chat"]
    )
    
    st.sidebar.divider()
    
    # ==========================================
    # LOGOUT INTERACTION LAYER (WITH CONFIRMATION)
    # ==========================================
    if not st.session_state.logout_confirm:
        if st.sidebar.button("🔓 Log Out", use_container_width=True):
            st.session_state.logout_confirm = True
            st.rerun()
    else:
        st.sidebar.warning("Are you sure you want to log out?")
        col_yes, col_no = st.sidebar.columns(2)
        
        with col_yes:
            if st.button("Yes", type="primary", use_container_width=True):
                username_to_logout = st.session_state.user["username"]
                try:
                    # Notify backend framework
                    requests.post(f"{API}/logout?username={username_to_logout}")
                except Exception:
                    pass

                # Reset authorization footprints
                st.session_state.logged_in = False
                st.session_state.user = None
                st.session_state.logout_confirm = False
                st.rerun()
                
        with col_no:
            if st.button("No", use_container_width=True):
                st.session_state.logout_confirm = False
                st.rerun()

    username = st.session_state.user["username"]

    # ==========================================
    # HOME
    # ==========================================
    if menu == "Home":

        st.title(f"Welcome, {username}")
        st.subheader("Latest Products")

        res = requests.get(f"{API}/products")

        if res.status_code == 200:

            products = res.json()[::-1]

            for p in products:

                st.subheader(p["product_type"])

                # ==========================================
                # PRODUCT DETAILS
                # ==========================================
                if p["product_type"] == "Uniform":

                    st.write(
                        "Uniform Type:",
                        p.get("uniform_type", "")
                    )

                    st.write(
                        "Size:",
                        p.get("size", "")
                    )

                elif p["product_type"] == "Books":

                    st.write(
                        "Book Name:",
                        p.get("book_title", "")
                    )

                elif p["product_type"] == "Others":

                    st.write(
                        "Product Name:",
                        p.get("product_name", "")
                    )

                st.write("Seller:", p["owner_username"])
                st.write("Price: ₱", p["price"])

                if p.get("is_sold", "No") == "Yes":
                    st.error("SOLD")
                else:
                    st.success("AVAILABLE")

                st.write("Description:", p["description"])

                # ==========================================
                # IMAGES
                # ==========================================
                if p.get("images"):

                    for img in p["images"].split(","):

                        if img.strip():

                            st.image(
                                f"uploads/{img}",
                                width=200
                            )

                # ==========================================
                # BUY LOGIC
                # ==========================================
                is_owner = p["owner_username"] == username

                if is_owner:

                    st.info("This is your product")

                elif p.get("is_sold", "No") == "Yes":

                    st.error("Already Sold")

                else:

                    if st.button(
                        "Buy",
                        key=f"buy_{p['id']}"
                    ):

                        buy_res = requests.post(
                            f"{API}/buy-product",
                            json={
                                "product_id": p["id"],
                                "buyer_username": username
                            }
                        )

                        data = buy_res.json()

                        if data["status"] == "success":

                            st.success(
                                "Purchased successfully!"
                            )

                            st.rerun()

                        else:
                            st.error(data["message"])

                st.divider()

    # ==========================================
    # PROFILE
    # ==========================================
    elif menu == "Profile":
        st.title("My Profile")
        user_header(username)

        st.divider()

        tab1, tab2, tab3 = st.tabs([
            "My Listings",
            "My Purchases",
            "My Sales"
        ])

        # ==========================================
        # MY LISTINGS
        # ==========================================
        with tab1:

            st.subheader("My Products")

            res = requests.get(
                f"{API}/my-products/{username}"
            )

            if res.status_code == 200:

                products = res.json()

                if not products:
                    st.info("No products yet.")

                for p in products:

                    st.write("🛒", p["product_type"])

                    if p["product_type"] == "Uniform":

                        st.write(
                            "Uniform Type:",
                            p.get("uniform_type", "")
                        )

                        st.write(
                            "Size:",
                            p.get("size", "")
                        )

                    elif p["product_type"] == "Books":

                        st.write(
                            "Book Name:",
                            p.get("book_title", "")
                        )

                    elif p["product_type"] == "Others":

                        st.write(
                            "Product Name:",
                            p.get("product_name", "")
                        )

                    st.write("Price: ₱", p["price"])

                    if p.get("images"):

                        for img in p["images"].split(","):

                            if img.strip():

                                st.image(
                                    f"uploads/{img}",
                                    width=120
                                )

                    st.divider()

        # ==========================================
        # MY PURCHASES
        # ==========================================
        with tab2:

            st.subheader("Buyer Transactions")

            res = requests.get(
                f"{API}/my-transactions/{username}"
            )

            if res.status_code == 200:

                transactions = res.json()

                buyer_transactions = [
                    t for t in transactions
                    if t["buyer_username"] == username
                ]

                if not buyer_transactions:
                    st.info("No purchases yet.")

                for t in buyer_transactions:

                    col1, col2, col3, col4, col5, col6 = st.columns(
                        [2, 2, 2, 2, 1, 1]
                    )

                    with col1:
                        st.write("📦", t["product_name"])

                    with col2:
                        st.write("Role: Buyer")

                    with col3:
                        st.write(
                            "Seller:",
                            t["seller_username"]
                        )

                    with col4:
                        st.write("₱", t["price"])

                    with col5:
                        if st.button("💬", key=f"buyer_chat_{t['id']}"):

                            res = requests.post(
                                f"{API}/chat/open",
                                json={
                                    "buyer": t["buyer_username"],
                                    "seller": t["seller_username"],
                                    "product_id": t["product_id"]
                                }
                            )

                            data = res.json()

                            st.session_state.active_chat = {
                                "conversation_id": data["conversation_id"],
                                "seller": t["seller_username"],
                                "buyer": t["buyer_username"]
                            }
                            st.rerun()
                    with col6:
                        try:
                            if st.button("❌", key=f"cancel_buyer_{t['id']}"):
                                cancel_order(t["id"])
                                st.rerun()
                        except Exception as e:
                            st.error(str(e))  

        # ==========================================
        # MY SALES
        # ==========================================
        with tab3:

            st.subheader("Seller Transactions")

            res = requests.get(
                f"{API}/my-transactions/{username}"
            )

            if res.status_code == 200:

                transactions = res.json()

                seller_transactions = [
                    t for t in transactions
                    if t["seller_username"] == username
                ]

                if not seller_transactions:
                    st.info("No sales yet.")

                for t in seller_transactions:

                    col1, col2, col3, col4, col5, col6 = st.columns(
                        [2, 2, 2, 2, 1, 1]
                    )

                    with col1:
                        st.write("📦", t["product_name"])

                    with col2:
                        st.write("Role: Seller")

                    with col3:
                        st.write(
                            "Buyer:",
                            t["buyer_username"]
                        )

                    with col4:
                        st.write("₱", t["price"])

                    with col5:
                        if st.button("💬", key=f"seller_chat_{t['id']}"):

                            res = requests.post(
                                f"{API}/chat/open",
                                json={
                                    "buyer": t["buyer_username"],
                                    "seller": t["seller_username"],
                                    "product_id": t["product_id"]
                                }
                            )
    
                            data = res.json()

                            st.session_state.active_chat = {
                                "conversation_id": data["conversation_id"],
                                "seller": t["seller_username"],
                                "buyer": t["buyer_username"]
                            }
                            st.rerun()

                    with col6:
                        try:
                            if st.button("❌", key=f"cancel_seller_{t['id']}"):
                                cancel_order(t["id"])
                                st.rerun()
                        except Exception as e:
                            st.error(str(e))

    # ==========================================
    # SELLING
    # ==========================================
    elif menu == "Selling":

        st.title("Selling Panel")

        product_type = st.selectbox(
            "Product Type",
            ["Uniform", "Books", "Others"]
        )

        # ==========================================
        # UNIFORM
        # ==========================================
        if product_type == "Uniform":

            uniform_type = st.selectbox(
                "Uniform Type",
                ["University Uniform", "PE", "NSTP"]
            )

            size = st.selectbox(
                "Size",
                ["XS", "S", "M", "L", "XL", "2XL", "3XL"]
            )

            price = st.number_input(
                "Price (₱)",
                min_value=0.0,
                key="uniform_price"
            )

            description = st.text_area(
                "Description",
                key="uniform_desc"
            )

            uploaded_files = st.file_uploader(
                "Upload Images",
                type=["png", "jpg", "jpeg"],
                accept_multiple_files=True,
                key="uniform_upload"
            )

            if st.button("Post Uniform"):

                images = (
                    save_images(uploaded_files)
                    if uploaded_files else ""
                )

                res = requests.post(
                    f"{API}/add-product",
                    json={
                        "product_type": "Uniform",
                        "uniform_type": uniform_type,
                        "book_title": "",
                        "product_name": "",
                        "size": size,
                        "price": price,
                        "description": description,
                        "owner_username": username,
                        "images": images
                    }
                )

                if res.status_code == 200:
                    st.success(
                        "Uniform posted successfully!"
                    )
                else:
                    st.error(res.text)

        # ==========================================
        # BOOKS
        # ==========================================
        elif product_type == "Books":

            book_title = st.text_input(
                "Book Name"
            )

            price = st.number_input(
                "Price (₱)",
                min_value=0.0,
                key="book_price"
            )

            description = st.text_area(
                "Description",
                key="book_desc"
            )

            uploaded_files = st.file_uploader(
                "Upload Images",
                type=["png", "jpg", "jpeg"],
                accept_multiple_files=True,
                key="book_upload"
            )

            if st.button("Post Book"):

                images = (
                    save_images(uploaded_files)
                    if uploaded_files else ""
                )

                res = requests.post(
                    f"{API}/add-product",
                    json={
                        "product_type": "Books",
                        "uniform_type": "",
                        "book_title": book_title,
                        "product_name": "",
                        "size": "",
                        "price": price,
                        "description": description,
                        "owner_username": username,
                        "images": images
                    }
                )

                if res.status_code == 200:
                    st.success(
                        "Book posted successfully!"
                    )
                else:
                    st.error(res.text)

        # ==========================================
        # OTHERS
        # ==========================================
        elif product_type == "Others":

            product_name = st.text_input(
                "Product Name"
            )

            price = st.number_input(
                "Price (₱)",
                min_value=0.0,
                key="other_price"
            )

            description = st.text_area(
                "Description",
                key="other_desc"
            )

            uploaded_files = st.file_uploader(
                "Upload Images",
                type=["png", "jpg", "jpeg"],
                accept_multiple_files=True,
                key="other_upload"
            )

            if st.button("Post Product"):

                images = (
                    save_images(uploaded_files)
                    if uploaded_files else ""
                )

                res = requests.post(
                    f"{API}/add-product",
                    json={
                        "product_type": "Others",
                        "uniform_type": "",
                        "book_title": "",
                        "product_name": product_name,
                        "size": "",
                        "price": price,
                        "description": description,
                        "owner_username": username,
                        "images": images
                    }
                )

                if res.status_code == 200:
                    st.success(
                        "Product posted successfully!"
                    )
                else:
                    st.error(res.text)

    # ==========================================
    # BUYING
    # ==========================================
    elif menu == "Buying":

        st.title("Browse Products")

        res = requests.get(f"{API}/products")

        if res.status_code == 200:

            for p in res.json():

                st.subheader(p["product_type"])

                st.write(
                    "Seller:",
                    p["owner_username"]
                )

                st.write(
                    "Price:",
                    p["price"]
                )

                if p.get("images"):

                    for img in p["images"].split(","):

                        if img.strip():

                            st.image(
                                f"uploads/{img}",
                                width=200
                            )

                st.divider()

    # ==========================================
    # CHAT
    # ==========================================
    elif menu == "Chat":
        chat_panel()