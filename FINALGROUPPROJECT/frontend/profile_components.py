#frontend/profile_components.py
import streamlit as st
import requests

API = "http://127.0.0.1:8000"

def user_header(username):

    try:
        res = requests.get(f"{API}/user/{username}")

        if res.status_code == 200:
            user = res.json()

            col1, col2 = st.columns([1, 4])

            with col1:
                st.image(
                    "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
                    width=100
                )

            with col2:
                st.title(user["username"])
                st.write("📧", user["email"])

        else:
            st.error("Failed to load user profile")

    except Exception:
        st.error("Cannot connect to server")