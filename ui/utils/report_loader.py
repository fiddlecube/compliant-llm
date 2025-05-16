import streamlit as st
import json

def load_report(file_path):
    """Load JSON report file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading report: {e}")
        return None
