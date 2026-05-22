import streamlit as st
import requests

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="RTU Marketplace", layout="wide")

# -------------------------
# SESSION STATE
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

# -------------------------
# LOGIN / REGISTER PAGE
# -------------------------
if not st.session_state.logged_in:

    st.title("RTU Marketplace")

    choice = st.selectbox("Action", ["Login", "Register"])

    # REGISTER
    if choice == "Register":

        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Register"):

            res = requests.post(
                f"{API}/register",
                json={
                    "username": username,
                    "email": email,
                    "password": password
                }
            )

            st.json(res.json())

    # LOGIN
    elif choice == "Login":

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

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

# -------------------------
# DASHBOARD
# -------------------------
# -------------------------
# DASHBOARD
# -------------------------
# SELLING
# -------------------------
# DASHBOARD
# -------------------------
else:

    st.sidebar.title("RTU Marketplace")

    menu = st.sidebar.radio(
        "Navigation",
        ["Home", "Profile", "Selling", "Chat", "Logout"]
    )

    username = st.session_state.user["username"]

    # ---------------- HOME ----------------
    if menu == "Home":

        st.title(f"Welcome, {username}!")
        st.subheader("Latest Posts")

        res = requests.get(f"{API}/products")

        if res.status_code == 200:

            products = res.json()

            for p in products[::-1]:

                st.subheader(p["product_type"])

                st.write("Seller:", p["owner_username"])
                st.write("Price:", p["price"])
                st.write("Description:", p["description"])

                if p.get("images"):

                    image_list = p["images"].split(",")

                    for img in image_list:
                        st.image(f"uploads/{img}", width=200)

                st.divider()

    # ---------------- PROFILE ----------------
    elif menu == "Profile":

        st.title("Profile")

        st.write("Username:", username)
        st.write("Email:", st.session_state.user["email"])

    # ---------------- SELLING ----------------
    elif menu == "Selling":

        st.title("Selling Panel")

        product_type = st.selectbox(
            "Product Type",
            ["Select...", "Uniform", "Books", "Others"]
        )

        # ---------- UNIFORM ----------
        if product_type == "Uniform":

            uniform_type = st.selectbox(
                "Type of Uniform",
                ["University Uniform", "PE", "NSTP"]
            )

            size = st.selectbox(
                "Size",
                ["XS", "S", "M", "L", "XL", "2XL", "3XL"]
            )

            price = st.number_input(
                "Price (₱)",
                min_value=0.0,
                format="%.2f"
            )

            description = st.text_area("Description")

            uploaded_files = st.file_uploader(
                "Upload Product Images",
                type=["png", "jpg", "jpeg"],
                accept_multiple_files=True,
                key="uniform_images"
            )

            if st.button("Post Uniform"):

                import os

                os.makedirs("uploads", exist_ok=True)

                image_names = []

                if uploaded_files:

                    for file in uploaded_files:

                        file_path = f"uploads/{file.name}"

                        with open(file_path, "wb") as f:
                            f.write(file.getbuffer())

                        image_names.append(file.name)

                res = requests.post(
                    f"{API}/add-product",
                    json={
                        "product_type": "Uniform",
                        "uniform_type": uniform_type,
                        "size": size,
                        "price": str(price),
                        "description": description,
                        "owner_username": username,
                        "images": ",".join(image_names)
                    }
                )

                if res.status_code == 200:
                    st.success("Uniform posted!")
                else:
                    st.error(res.text)

        # ---------- BOOKS ----------
        elif product_type == "Books":

            book_title = st.text_input("Book Title")

            price = st.number_input(
                "Price (₱)",
                min_value=0.0,
                format="%.2f"
            )

            description = st.text_area("Description")

            uploaded_files = st.file_uploader(
                "Upload Product Images",
                type=["png", "jpg", "jpeg"],
                accept_multiple_files=True,
                key="book_images"
            )

            if st.button("Post Book"):

                import os

                os.makedirs("uploads", exist_ok=True)

                image_names = []

                if uploaded_files:

                    for file in uploaded_files:

                        file_path = f"uploads/{file.name}"

                        with open(file_path, "wb") as f:
                            f.write(file.getbuffer())

                        image_names.append(file.name)

                res = requests.post(
                    f"{API}/add-product",
                    json={
                        "product_type": "Books",
                        "book_title": book_title,
                        "size": "",
                        "price": str(price),
                        "description": description,
                        "owner_username": username,
                        "images": ",".join(image_names)
                    }
                )

                if res.status_code == 200:
                    st.success("Book posted!")
                else:
                    st.error(res.text)

        # ---------- OTHERS ----------
        elif product_type == "Others":

            product_name = st.text_input("Name of Product")

            price = st.number_input(
                "Price (₱)",
                min_value=0.0,
                format="%.2f"
            )

            description = st.text_area("Description")

            uploaded_files = st.file_uploader(
                "Upload Product Images",
                type=["png", "jpg", "jpeg"],
                accept_multiple_files=True,
                key="others_images"
            )

            if st.button("Post Product"):

                import os

                os.makedirs("uploads", exist_ok=True)

                image_names = []

                if uploaded_files:

                    for file in uploaded_files:

                        file_path = f"uploads/{file.name}"

                        with open(file_path, "wb") as f:
                            f.write(file.getbuffer())

                        image_names.append(file.name)

                res = requests.post(
                    f"{API}/add-product",
                    json={
                        "product_type": "Others",
                        "product_name": product_name,
                        "size": "",
                        "price": str(price),
                        "description": description,
                        "owner_username": username,
                        "images": ",".join(image_names)
                    }
                )

                if res.status_code == 200:
                    st.success("Product posted!")
                else:
                    st.error(res.text)

        # ---------- MY PRODUCTS ----------
        st.subheader("My Products")

        res = requests.get(f"{API}/my-products/{username}")

        if res.status_code == 200:

            products = res.json()

            for p in products:

                st.write("Type:", p["product_type"])

                if p.get("uniform_type"):
                    st.write("Uniform Type:", p["uniform_type"])

                if p.get("book_title"):
                    st.write("Book Title:", p["book_title"])

                if p.get("product_name"):
                    st.write("Product Name:", p["product_name"])

                if p.get("size"):
                    st.write("Size:", p["size"])

                st.write("Price:", p["price"])
                st.write("Description:", p["description"])

                if p.get("images"):

                    image_list = p["images"].split(",")

                    for img in image_list:
                        st.image(f"uploads/{img}", width=150)

                st.divider()

    # ---------------- BUYING ----------------
    elif menu == "Buying":

        st.title("All Products")

        res = requests.get(f"{API}/products")

        if res.status_code == 200:

            products = res.json()

            for p in products:

                st.subheader(p["product_type"])

                st.write("Seller:", p["owner_username"])
                st.write("Price:", p["price"])
                st.write("Description:", p["description"])

                if p.get("images"):

                    image_list = p["images"].split(",")

                    for img in image_list:
                        st.image(f"uploads/{img}", width=200)

                st.divider()

    # ---------------- LOGOUT ----------------
    elif menu == "Logout":

        st.session_state.logged_in = False
        st.session_state.user = None

        st.rerun()