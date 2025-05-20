import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def render_risk_severity(report_data):
    """
    Visualize risk severity and potential impact of security vulnerabilities
    
    Args:
        report_data (dict): Comprehensive test report data
    """
    st.header("🛡️ Security Risk Analysis Dashboard")
    
    # Process results and categorize risks
    risk_data = []
    for strategy in report_data.get('results', []):
        strategy_name = strategy['strategy']
        for test in strategy['results']:
            severity = test.get('severity', 'unknown')
            category = test['category']
            success = not test['success']  # True if test failed
            
            risk_data.append({
                'Strategy': strategy_name,
                'Severity': severity,
                'Category': category,
                'Success': success,
                'Mutation': test.get('mutation_technique', 'Unknown'),
                'Description': test.get('description', 'No description available')
            })
    
    # Create DataFrame for analysis
    df = pd.DataFrame(risk_data)
    
    # Risk distribution by severity
    severity_counts = df['Severity'].value_counts()
    
    # Strategy-based risk distribution
    strategy_risks = df.groupby(['Strategy', 'Severity']).size().reset_index(name='Count')
    
    # Create visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Severity Distribution Chart
        fig_severity = px.pie(
            names=severity_counts.index,
            values=severity_counts.values,
            title='Risk Distribution by Severity',
            color_discrete_sequence=['#FF4136', '#FF851B', '#FFDC00', '#2ECC40']
        )
        st.plotly_chart(fig_severity, use_container_width=True)
    
    with col2:
        # Strategy Risk Distribution
        fig_strategy = px.bar(
            strategy_risks,
            x='Strategy',
            y='Count',
            color='Severity',
            title='Risk Distribution by Strategy',
            color_discrete_sequence=['#FF4136', '#FF851B', '#FFDC00', '#2ECC40']
        )
        st.plotly_chart(fig_strategy, use_container_width=True)

    
    # Risk Patterns
    st.subheader("🔍 Risk Patterns")
    
    # Mutation Techniques Distribution
    mutation_dist = df['Mutation'].value_counts()
    fig_mutation = px.bar(
        x=mutation_dist.index,
        y=mutation_dist.values,
        title='Mutation Techniques Distribution',
        labels={'x': 'Mutation Technique', 'y': 'Count'}
    )
    st.plotly_chart(fig_mutation, use_container_width=True)
    
