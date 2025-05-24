import streamlit as st
import json
import os
import sys
from pathlib import Path
from ui.components.compliance_report import render_compliance_report
from utils.report_loader import load_report
from components.risk_severity import render_risk_severity
from components.security_findings import render_security_findings
from components.strategy_table import render_strategy_table

def get_report_path_from_args():
    if "--report" in sys.argv:
        report_index = sys.argv.index("--report") + 1
        if report_index < len(sys.argv):
            return sys.argv[report_index]
    return None

def create_dashboard():
    st.set_page_config(
        page_title="AI Security Risk Dashboard", 
        page_icon=":shield:", 
        layout="wide"
    )
    
    st.title("🛡️ AI Security Risk Assessment")

    # Determine which report to load
    report_path = get_report_path_from_args()

    if report_path and os.path.exists(report_path):
        default_report_path = report_path
    else:
        # Default report path
        user_home = Path.home()
        report_dir = user_home / ".compliant-llm" / "reports"
        
        if os.path.exists(report_dir):
            # Find all report files with timestamp format
            report_files = [f for f in os.listdir(report_dir) 
                          if f.startswith("report_") and 
                          f.endswith(".json") and
                          len(f) == len("report_YYYYMMDD_HHMMSS.json")]
            if report_files:
                # Sort by timestamp (which is in the filename)
                latest_file = sorted(report_files)[-1]
                default_report_path = os.path.join(report_dir, latest_file)
            else:
                default_report_path = None

    try:
        report_data = load_report(default_report_path)
    except:
        st.warning("No default report found. Please run a test first.")
        return
    
    if not report_data:
        st.error("Unable to load report data")
        return
    
    # # Sidebar for risk configuration
    # st.sidebar.header("Risk Configuration")
    # risk_tolerance = st.sidebar.slider("Risk Tolerance", 0, 100, 30)
    
    # Main dashboard sections
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Tests Ran", report_data['metadata']['test_count'], 
                  help="Number of security assessments performed")
    with col2:
        st.metric("Tests breached successfully", report_data['metadata']['success_count'], 
                  help="Tests that passed security checks")
    with col3:
        st.metric("Tests unsuccessful", report_data['metadata']['failure_count'], 
                  help="Tests that failed security checks")
    
    # Render dashboard components
    render_compliance_report(report_data)
    render_strategy_table(report_data)
    # render_risk_severity(report_data)
    render_security_findings(report_data)

def main():
    create_dashboard()

if __name__ == "__main__":
    main()
