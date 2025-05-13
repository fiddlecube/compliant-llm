import streamlit as st
import json

def start_ui():
    st.title("Prompt Test Dashboard")
    try:
        with open("report.json") as f:
            report = json.load(f)
        st.json(report)
    except FileNotFoundError:
        st.warning("No report found. Run CLI first.")

if __name__ == "__main__":
    start_ui()