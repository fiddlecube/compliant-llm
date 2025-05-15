


import streamlit as st
import pandas as pd

def render_strategy_table(report_data):
    # Detailed Test Results
    st.header("Detailed Test Results")
    detailed_results_df = pd.DataFrame(report_data['tests'])
    st.dataframe(detailed_results_df)