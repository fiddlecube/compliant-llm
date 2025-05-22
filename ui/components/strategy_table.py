


import streamlit as st
import pandas as pd

def render_strategy_table(report_data):
    """Render strategy-based test results with filtering"""
    st.header("Security Strategies Overview")
    
    # Get strategy summaries
    strategy_summaries = report_data['strategy_summaries']
    
    # Create strategy overview table
    strategy_df = pd.DataFrame(strategy_summaries)
    
    # Add search and filter
    search_term = st.text_input("🔍 Search Strategies", "")
    filtered_df = strategy_df[
        strategy_df['strategy'].str.contains(search_term, case=False, na=False)
    ].drop(columns=['success_rate', 'breached_tests'], errors='ignore')
    
    st.dataframe(
        filtered_df,
        column_config={
            'strategy': st.column_config.TextColumn("Strategy"),
            'test_count': st.column_config.NumberColumn("Total Tests"),
            'success_count': st.column_config.NumberColumn("Passed"),
            'failure_count': st.column_config.NumberColumn("Failed"),
            # 'success_rate': st.column_config.ProgressColumn(
            #     "Pass Rate",
            #     help="Percentage of tests passed",
            #     format="%f%%",
            #     min_value=0,
            #     max_value=100,
            # ),
            'runtime_in_seconds': st.column_config.NumberColumn(
                "Runtime (s)",
                format="%.2f"
            ),
            'prompt_mutations': st.column_config.TextColumn("Mutations")
        },
        hide_index=True,
    )
                