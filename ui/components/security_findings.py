import streamlit as st
import plotly.graph_objects as go

def render_security_findings(report_data):
    """
    Visualize detailed security findings and potential vulnerabilities
    
    Args:
        report_data (dict): Comprehensive test report data
    """
    st.header("🕵️ Security Findings Breakdown")
    
    # Categorize findings by attack strategy
    strategy_findings = {}
    for test in report_data.get('tests', []):
        strategy = test.get('strategy', 'Unknown')
        success = str(test.get('success', 'False')).lower() in ['true', '1', 'yes']
        
        if strategy not in strategy_findings:
            strategy_findings[strategy] = {
                'total_tests': 0,
                'failed_tests': 0,
                'vulnerabilities': []
            }
        
        strategy_findings[strategy]['total_tests'] += 1
        if not success:
            strategy_findings[strategy]['failed_tests'] += 1
            strategy_findings[strategy]['vulnerabilities'].append(test)
    
    # Prepare data for visualization
    strategies = list(strategy_findings.keys())
    failure_rates = [
        (findings['failed_tests'] / findings['total_tests'] * 100) 
        if findings['total_tests'] > 0 else 0 
        for strategy, findings in strategy_findings.items()
    ]
    
    # Bar chart of strategy vulnerability rates
    fig_strategy_vulnerabilities = go.Figure(data=[
        go.Bar(
            x=strategies, 
            y=failure_rates, 
            marker_color=[
                'red' if rate > 50 else 
                'orange' if rate > 25 else 
                'yellow' if rate > 10 else 
                'green' 
                for rate in failure_rates
            ]
        )
    ])
    fig_strategy_vulnerabilities.update_layout(
        title='Vulnerability Rates by Attack Strategy',
        xaxis_title='Attack Strategy',
        yaxis_title='Failure Rate (%)'
    )
    
    # Layout for security findings
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.plotly_chart(fig_strategy_vulnerabilities, use_container_width=True)
    
    with col2:
        # Summary Metrics
        total_strategies = len(strategies)
        high_risk_strategies = sum(1 for strategy, findings in strategy_findings.items() 
                                   if (findings['failed_tests'] / findings['total_tests']) > 0.5)
        
        st.metric("Total Strategies Tested", total_strategies)
        st.metric("High-Risk Strategies", high_risk_strategies)
        
        # Risk Color Indicator
        risk_color = 'red' if high_risk_strategies > 0 else 'green'
        st.markdown(f"🚨 **Security Posture**: <span style='color:{risk_color}'>{'Requires Immediate Review' if high_risk_strategies > 0 else 'Acceptable'}</span>", unsafe_allow_html=True)
    
    # Detailed Vulnerability Findings
    with st.expander("🔬 Detailed Vulnerability Analysis"):
        for strategy, findings in strategy_findings.items():
            if findings['vulnerabilities']:
                st.subheader(f"{strategy} Vulnerabilities")
                vulnerability_table = []
                for vuln in findings['vulnerabilities']:
                    vulnerability_table.append({
                        'Test Details': vuln.get('details', 'No details'),
                        'Prompt': vuln.get('user_prompt', 'N/A'),
                        'Response': vuln.get('llm_response', 'N/A')
                    })
                
                st.table(vulnerability_table)
