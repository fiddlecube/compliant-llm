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
    st.header("🚨 Risk Severity Analysis")
    
    # Categorize risks
    risk_categories = {
        'Critical': [],
        'High': [],
        'Medium': [],
        'Low': []
    }
    
    # Process tests and categorize risks
    for test in report_data.get('tests', []):
        success = str(test.get('success', 'False')).lower() in ['true', '1', 'yes']
        strategy = test.get('strategy', 'Unknown')
        
        # Risk categorization logic
        if not success:
            if 'OWASP' in strategy or 'Injection' in strategy:
                risk_categories['Critical'].append(test)
            elif 'Prompt' in strategy or 'Context' in strategy:
                risk_categories['High'].append(test)
            elif 'Information' in strategy:
                risk_categories['Medium'].append(test)
            else:
                risk_categories['Low'].append(test)
    
    # Risk distribution pie chart
    risk_distribution = {
        category: len(risks) 
        for category, risks in risk_categories.items()
    }
    
    fig_risk_dist = go.Figure(data=[
        go.Pie(
            labels=list(risk_distribution.keys()),
            values=list(risk_distribution.values()),
            hole=0.3,
            marker_colors=['#FF4136', '#FF851B', '#FFDC00', '#2ECC40']
        )
    ])
    fig_risk_dist.update_layout(title='Risk Distribution by Severity')
    
    # Layout for risk visualization
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.plotly_chart(fig_risk_dist, use_container_width=True)
    
    with col2:
        # Risk Metrics
        st.metric("Total Vulnerabilities", 
                  sum(risk_distribution.values()), 
                  help="Total number of identified security risks")
        st.metric("Critical Risks", 
                  risk_distribution.get('Critical', 0), 
                  help="Vulnerabilities requiring immediate action")
        
        # Risk Tolerance Indicator
        risk_tolerance_color = 'red' if risk_distribution.get('Critical', 0) > 0 else 'green'
        st.markdown(f"🚨 **Risk Status**: <span style='color:{risk_tolerance_color}'>{'Requires Immediate Attention' if risk_distribution.get('Critical', 0) > 0 else 'Acceptable'}</span>", unsafe_allow_html=True)
    
    # Detailed Risk Findings
    with st.expander("🔍 Detailed Risk Breakdown"):
        for category, risks in risk_categories.items():
            if risks:
                st.subheader(f"{category} Risk Vulnerabilities")
                for risk in risks:
                    st.markdown(f"- **Strategy**: {risk.get('strategy', 'Unknown')}")
                    st.markdown(f"  **Details**: {risk.get('details', 'No additional details')}")
