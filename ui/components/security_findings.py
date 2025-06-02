import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def render_security_findings(report_data):
    """
    Visualize detailed security findings and potential vulnerabilities
    
    Args:
        report_data (dict): Comprehensive test report data
    """
    st.header("🛡️ Security Findings Analysis")
    
    # Process results
    findings_data = []
    for strategy in report_data.get('testcases', []):
        strategy_name = strategy['strategy'].replace('_', ' ').title()
        for test in strategy['results']:
            response_data = test.get('response', {})
            findings_data.append({
                'Strategy': strategy_name,
                'Severity': test.get('severity', 'Moderate'),
                'Category': test.get('category', ''),
                'Success': test.get('evaluation', {}).get('passed', False),  # True if test failed
                'Mutation': test.get('mutation_technique', 'Unknown').replace('_', ' ').title(),
                'Description': test.get('description', 'No description'),
                'System Prompt': test.get('system_prompt', 'N/A'),
                'Attack Prompt': test.get('attack_prompt', 'N/A'),
                'Response': response_data.get('response', 'N/A') if response_data else 'N/A',
                'Evaluation': test.get('evaluation', {}).get('reason', 'No evaluation')
            })
    
    # Create DataFrame for analysis
    df = pd.DataFrame(findings_data)
    
    # Strategy to failures
    strategy_counts = df.groupby('Strategy').agg({
        'Success': 'sum',  # Count of failures
        'Severity': lambda x: (x == 'moderate').sum()  # Count of high severity
    }).reset_index()
    
    # Bar chart of failure counts
    fig_strategy_rates = go.Figure(data=[
        go.Bar(
            x=strategy_counts['Strategy'],
            y=strategy_counts['Success'],
            marker_color=[
                'red' if count >= 5 else 
                'orange' if count >= 3 else 
                'yellow' if count >= 1 else 
                'green' 
                for count in strategy_counts['Success']
            ]
        )
    ])
    fig_strategy_rates.update_layout(
        title='Breaches by Attack Strategy',
        xaxis_title='Attack Strategy',
        yaxis_title='Breaches'
    )
    
    # Layout for security findings
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.plotly_chart(fig_strategy_rates, use_container_width=True)
    
    with col2:
        # Summary Metrics
        total_tests = len(df)
        failed_tests = len(df[df['Success']])
        high_risk_tests = len(df[(df['Success']) & (df['Severity'] == 'high')])
        
        st.metric("Total Tests", total_tests)
        st.metric("Failed Tests", failed_tests, f"{failed_tests/total_tests*100:.1f}%")
        st.metric("High-Risk Failures", high_risk_tests, f"{high_risk_tests/total_tests*100:.1f}%")
        
        # Risk Color Indicator
        risk_color = 'red' if high_risk_tests > 0 else 'green'
        st.markdown(f"🚨 **Security Posture**: <span style='color:{risk_color}'>{'Requires Immediate Review' if high_risk_tests > 0 else 'Acceptable'}</span>", unsafe_allow_html=True)
    
    # Detailed Security Findings
    st.subheader("🔍 Detailed Security Findings")
    
    # Strategy-based analysis
    for strategy, group in df.groupby('Strategy'):
        formatted_strategy = ' '.join(word.capitalize() for word in strategy.split('_'))
        st.markdown(f"### {formatted_strategy} Strategy Analysis")
        
        # Strategy metrics
        col1, col2 = st.columns(2)
        with col1:
            failed_count = len(group[group['Success']])
            st.metric(
                "Failed Tests",
                failed_count,
                f"{failed_count/len(group)*100:.1f}%"
            )
        
        with col2:
            high_risk_count = len(group[(group['Success']) & (group['Severity'] == 'high')])
            st.metric(
                "High-Risk Failures",
                high_risk_count,
                f"{high_risk_count/len(group)*100:.1f}%"
            )
        
        # Show failed tests with details
        failed_tests = group[group['Success']]
        if not failed_tests.empty:
            st.markdown("**Failed Tests:**")
            for _, test in failed_tests.iterrows():
                # Create an expander for each test
                with st.expander(f"🔍 {test['Mutation']} (Severity: {test['Severity']})"):
                    col1, col2 = st.columns(2)
                    
                    # Left column - Basic Info
                    with col1:
                        st.write("**Attack Prompt:**", test['Attack Prompt'])
                        st.write("**Severity:**", test['Severity'])
                        st.write("**Mutation:**", test['Mutation'])
                        st.write("**System Prompt:**", test['System Prompt'])
                    
                    # Right column - Response and Evaluation
                    with col2:
                        st.write("**Response:**", test['Response'])
                        st.write("**Evaluation:**", test['Evaluation'])


