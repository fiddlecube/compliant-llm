import streamlit as st
import subprocess
import json
import os
import sys
from pathlib import Path
import webbrowser
import time
from datetime import datetime

# Add project root to Python path to access core modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Get reports directory
reports_dir = project_root / "reports"

# Function to get list of reports with timestamps
def get_reports():
    reports = []
    if reports_dir.exists():
        for file in reports_dir.glob("*.json"):
            try:
                # Get modification time
                mod_time = datetime.fromtimestamp(file.stat().st_mtime)
                reports.append({
                    "name": file.name,
                    "path": str(file),
                    "modified": mod_time.strftime("%Y-%m-%d %H:%M:%S")
                })
            except:
                continue
    return sorted(reports, key=lambda x: x["modified"], reverse=True)

# Function to open dashboard with specific report
def open_dashboard_with_report(report_path):
    dashboard_path = project_root / "ui" / "app.py"
    subprocess.Popen([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(dashboard_path),
        "--server.port",
        "8502",  # Use different port to avoid conflict
        "--server.baseUrlPath",
        "/report",
        "--",  # Pass additional arguments to dashboard
        "--report",
        report_path
    ])

# Set page configuration
st.set_page_config(
    page_title="Compliant LLM UI",
    page_icon="",
    layout="wide"
)

def get_available_strategies():
    """Get list of available strategies from the README"""
    strategies = [
        "prompt_injection",
        "jailbreak",
        "excessive_agency",
        "indirect_prompt_injection",
        "insecure_output_handling",
        "model_dos",
        "model_extraction",
        "sensitive_info_disclosure"
    ]
    return strategies

def run_test(prompt, selected_strategies):
    """Run the test command with selected parameters"""
    try:
        # Get the absolute path to the main.py
        main_path = project_root / "cli" / "main.py"
        
        # Format the command
        command = [
            sys.executable,
            "-m",
            "cli.main",
            "test",
            "--prompt",
            f"\"{prompt}\"",
            "--strategy",
            ",".join(selected_strategies)
        ]
        
        # Run the command and capture output
        result = subprocess.run(command, capture_output=True, text=True)
        
        return result.stdout, result.stderr
    except Exception as e:
        return "", str(e)

def create_app_ui():
    """Create and display the main UI components"""
    # Main UI
    st.title(" Compliant LLM UI")

    # Sidebar with report list
    with st.sidebar:
        st.header("Test Reports")
        reports = get_reports()
        
        if not reports:
            st.info("No reports found. Run a test to generate reports.")
        else:
            st.write("### Recent Reports")
            for report in reports:
                if st.button(f"{report['name']} (Last modified: {report['modified']})"):
                    open_dashboard_with_report(report['path'])

    # Prompt input section
    st.header("Run New Test")

    # Prompt input
    with st.form("test_form"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            prompt = st.text_area("Enter your prompt:", 
                                height=150,
                                placeholder="Enter your system prompt here...")
        
        with col2:
            st.write("### Select Testing Strategies")
            strategies = get_available_strategies()
            selected_strategies = st.multiselect(
                "Choose strategies to test",
                strategies,
                default=["prompt_injection", "jailbreak"]
            )
        
        submit_button = st.form_submit_button("Run Test")

    # Run test when button is clicked
    if submit_button:
        if not prompt:
            st.error("Please enter a prompt!")
            st.stop()
        
        if not selected_strategies:
            st.error("Please select at least one testing strategy!")
            st.stop()
        
        with st.spinner("Running tests..."):
            stdout, stderr = run_test(prompt, selected_strategies)
            
        # Display results
        st.subheader("Test Results")
        st.write("---")
        
        if stdout:
            st.success("Test Output:")
            st.code(stdout, language="bash")
        
        if stderr:
            st.error("Error Output:")
            st.code(stderr, language="bash")

# Add documentation link
st.sidebar.markdown("""
# Documentation
- [Full Documentation](./docs)
""")

def main():
    """Main entry point for the app"""
    create_app_ui()

if __name__ == "__main__":
    main()
