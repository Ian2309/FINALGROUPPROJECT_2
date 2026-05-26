#frontend/cancel_panel.py
import streamlit as st
import requests

API = "http://127.0.0.1:8000"


def cancel_order(transaction_id):

    try:
        res = requests.post(
            f"{API}/cancel-order/{transaction_id}"
        )

        data = res.json()

        if data["status"] == "success":
            st.success("Order cancelled")
        else:
            st.error(data["message"])

    except Exception as e:
        st.error(f"Error: {str(e)}")