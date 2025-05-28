import streamlit as st
import pandas as pd
# import plotly.express as px
import plotly.graph_objects as go

def render_compliance_report(report_data):
    """
    Visualize NIST compliance metrics and risk scores
    
    Args:
        report_data (dict): Comprehensive test report data
    """
    st.header("🛡️ NIST Compliance Report")
    
    # Extract compliance data
    compliance_data = []
    for strategy in report_data.get('testcases', []):
        for test in strategy['results']:
            if 'compliance' in test:
                compliance = test['compliance']
                if 'nist' in compliance:
                    nist = compliance['nist']
                    risk_score = nist.get('risk_score', {})
                    
                    compliance_data.append({
                        'Strategy': strategy['strategy'].replace('_', ' ').title(),
                        'Numerical Score': risk_score.get('numerical_score', 0),
                        'Qualitative Score': risk_score.get('qualitative_score', 'unknown'),
                        'Likelihood': risk_score.get('likelihood', 'unknown'),
                        'Impact': risk_score.get('impact', 'unknown'),
                        'FIPS Impact': risk_score.get('fips_impact', 'unknown'),
                        'FIPS Version': risk_score.get('fips_version', 'unknown'),
                        'Test Success': not test['success']  # True if test failed
                    })
    
    if not compliance_data:
        st.warning("No compliance data found in the report")
        return
    
    # Create DataFrame
    df = pd.DataFrame(compliance_data)
    
    # Show tested controls
    st.subheader("Tested Controls")
    controls = []
    for strategy in report_data.get('testcases', []):
        for test in strategy['results']:
            if 'compliance' in test and 'nist' in test['compliance']:
                for control in test['compliance']['nist'].get('tested_controls', []):
                    controls.append({
                        'Strategy': strategy['strategy'],
                        'Family': control.get('family', 'Unknown'),
                        'Control ID': control.get('control_id', 'Unknown'),
                        'Title': control.get('title', 'Unknown'),
                        'Description': control.get('description', 'Unknown'),
                        'Version': control.get('version', 'Unknown'),
                        'Breach Successful': test.get('evaluation', {}).get('passed', False)
                    })
    
    # Create DataFrame for analysis
    df = pd.DataFrame(controls)
    
    # Aggregate breaches by Control ID and filter out controls with no breaches
    control_breaches = df.groupby('Control ID').agg({
        'Breach Successful': 'sum'  # Count of successful breaches
    }).reset_index()
    
    # Filter out controls with no breaches
    control_breaches = control_breaches[control_breaches['Breach Successful'] > 0]
    
    # Sort by number of breaches
    control_breaches = control_breaches.sort_values('Breach Successful', ascending=True)
    
    if not control_breaches.empty:
        # Create bar chart of breaches by control
        fig_control_breaches = go.Figure(data=[
            go.Bar(
                x=control_breaches['Control ID'],
                y=control_breaches['Breach Successful'],
                orientation='v',  # Horizontal bars
                marker_color=[
                    'red' if count >= 3 else
                    'orange' if count >= 2 else
                    'yellow' if count >= 1 else
                    'green'
                    for count in control_breaches['Breach Successful']
                ]
            )
        ])
        
        fig_control_breaches.update_layout(
            title='NIST Controls Breaches',
            xaxis_title='Control ID',
            yaxis_title='Number of Successful Breaches',
            height=max(350, len(control_breaches) * 30)  # Dynamic height based on number of controls
        )
        
        # Display the plot
        st.plotly_chart(fig_control_breaches, use_container_width=True)
    else:
        st.info("No controls with breaches found!")

    ##-------------------------------------------------------------------------
    
    
    # group the dataframe by 'Family' and display them as table
    st.subheader("Grouped Tested Controls")
    controls_df = pd.DataFrame(controls)
    controls_df = controls_df.groupby('Family').agg({
        'Control ID': 'count',
        'Breach Successful': 'sum'
    }).reset_index()
    st.dataframe(
        controls_df,
        column_config={
            'Family': st.column_config.TextColumn("Control Family"),
            'Control ID': st.column_config.NumberColumn("Number of Controls"),
            'Breach Successful': st.column_config.NumberColumn("Number of Breaches")
        },
        hide_index=True
    )
    
    
    st.subheader("Detailed Tested Controls")
    if controls:
        controls_df = pd.DataFrame(controls)
        
        # Sort by Breach Successful, putting True values first
        controls_df = controls_df.sort_values(by='Breach Successful', ascending=False)
        
        # Add a filter to let users see only breached controls if desired
        breach_filter = st.checkbox("Show only breached controls", value=False)
        if breach_filter:
            controls_df = controls_df[controls_df['Breach Successful'] == True]
        
        st.dataframe(
            controls_df,
            column_config={
                'Strategy': st.column_config.TextColumn("Strategy"),
                'Family': st.column_config.TextColumn("Control Family"),
                'Control ID': st.column_config.TextColumn("Control ID"),
                'Title': st.column_config.TextColumn("Control Title"),
                'Description': st.column_config.TextColumn("Description"),
                'Version': st.column_config.TextColumn("Version"),
                'Breach Successful': st.column_config.TextColumn("Breach Successful")
            },
            hide_index=True
        )

