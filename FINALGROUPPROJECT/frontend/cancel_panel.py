#frontend/cancel_panel.py
import streamlit as st
import requests

API = "http://127.0.0.1:8000"


def cancel_order(transaction_id):

    try:
        res = requests.post(f"{API}/cancel-order/{transaction_id}")

        if res.status_code != 200:
            st.error(f"HTTP ERROR: {res.text}")
            return

        try:
            data = res.json()
        except:
            st.error("Invalid JSON response from server")
            return

        if data.get("status") == "success":
            st.success("Order cancelled")
        else:
            st.error(data.get("message", "Unknown error"))

    except Exception as e:
        st.error(f"Request failed: {e}")