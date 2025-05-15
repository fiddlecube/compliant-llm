import streamlit as st
import plotly.express as px
import pandas as pd

def calculate_category_compliance(report_data, category):
    """Calculate compliance score for a specific OWASP category"""
    category_tests = [
        test for test in report_data['tests'] 
        if category.lower().replace(' ', '_') in test.get('category', '').lower()
    ]
    
    if not category_tests:
        return 0
    
    passed_tests = [test for test in category_tests if test.get('passed', False)]
    return len(passed_tests) / len(category_tests) * 100

def render_owasp_compliance(report_data):
    st.header("OWASP Top 10 AI Security Compliance")
    
    # Prepare OWASP compliance data
    owasp_categories = [
        'Access Control', 'Cryptographic Failures', 'Injection', 
        'Insecure Design', 'Security Misconfiguration', 
        'Vulnerable Components', 'Authentication Failures'
    ]
    
    compliance_data = {
        'Category': owasp_categories,
        'Compliance Score': [
            calculate_category_compliance(report_data, category) 
            for category in owasp_categories
        ]
    }
    
    compliance_df = pd.DataFrame(compliance_data)
    
    # Color-coded compliance heatmap
    fig_compliance = px.bar(
        compliance_df, 
        x='Category', 
        y='Compliance Score',
        title='OWASP Top 10 AI Security Compliance Scores',
        color='Compliance Score',
        color_continuous_scale='RdYlGn'
    )
    st.plotly_chart(fig_compliance, use_container_width=True)
