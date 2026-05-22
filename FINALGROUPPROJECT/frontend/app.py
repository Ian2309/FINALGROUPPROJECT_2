#app.py
import streamlit as st
import requests
import os
import uuid

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="RTU Marketplace", layout="wide")

# =========================
# SESSION STATE
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None


# =========================
# AUTH PAGE
# =========================
if not st.session_state.logged_in:

    st.title("RTU Marketplace")

    choice = st.selectbox("Action", ["Login", "Register"])

    # REGISTER
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

    # LOGIN
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


# =========================
# DASHBOARD
# =========================
else:

    st.sidebar.title("RTU Marketplace")

    menu = st.sidebar.radio(
        "Navigation",
        ["Home", "Profile", "Selling", "Buying", "Chat", "Logout"]
    )

    username = st.session_state.user["username"]


    # =========================
    # HOME
    # =========================
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

                # images
                if p.get("images"):
                    for img in p["images"].split(","):
                        st.image(f"uploads/{img}", width=200)

                # BUY LOGIC
                is_owner = p["owner_username"] == username

                if is_owner:
                    st.info("This is your product")
                else:
                    if st.button("Buy", key=f"buy_{p['id']}"):

                        buy_res = requests.post(f"{API}/buy-product", json={
                            "product_id": p["id"]
                        })

                        if buy_res.status_code == 200:
                            st.success("Purchased successfully!")
                        else:
                            try:
                                st.error(buy_res.json().get("message"))
                            except:
                                st.error("Purchase failed")

                st.divider()


    # =========================
    # PROFILE
    # =========================
    elif menu == "Profile":

        st.title("Profile Center")

        tab1, tab2, tab3 = st.tabs([
            "My Listings",
            "My Purchases",
            "My Sales"
        ])

        # LISTINGS
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

        # PURCHASES
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

                        st.button(f"Chat Seller {t['id']}", key=f"cb_{t['id']}")

                    st.divider()

        # SALES
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

                        st.button(f"Chat Buyer {t['id']}", key=f"cs_{t['id']}")

                    st.divider()


    # =========================
    # SELLING
    # =========================
    elif menu == "Selling":

        st.title("Selling Panel")

        product_type = st.selectbox(
            "Product Type",
            ["Uniform", "Books", "Others"]
        )

        description = st.text_area("Description")

        price = st.number_input("Price (₱)", min_value=0.0)

        uploaded_files = st.file_uploader(
            "Images",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True
        )

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
                "images": images
            })

            if res.status_code == 200:
                st.success("Posted successfully!")
            else:
                st.error(res.text)


    # =========================
    # BUYING
    # =========================
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


    # =========================
    # CHAT
    # =========================
    elif menu == "Chat":
        st.title("Chat System")
        st.info("Chat system coming soon...")


    # =========================
    # LOGOUT
    # =========================
    elif menu == "Logout":
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()