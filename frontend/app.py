import streamlit as st
import requests

API = "http://127.0.0.1:8000"

st.title("RTU Marketplace App")

choice = st.selectbox("Action", ["Register", "Login"])

if choice == "Register":
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        try:
            res = requests.post(
                f"{API}/register",
                json={
                    "username": username,
                    "email": email,
                    "password": password
                }
            )

            st.write("Status Code:", res.status_code)

            try:
                st.json(res.json())
            except:
                st.error("Response is not JSON")
                st.write(res.text)

        except Exception as e:
            st.error(e)


if choice == "Login":
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            res = requests.post(
                f"{API}/login",
                json={
                    "username": username,
                    "password": password
                }
            )

            st.write("Status Code:", res.status_code)

            try:
                st.json(res.json())
            except:
                st.error("Response is not JSON")
                st.write(res.text)

        except Exception as e:
            st.error(e)