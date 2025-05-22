import streamlit as st
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import psutil
import random
from typing import Set
import json

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

# Set of ports we're currently using
used_ports: Set[int] = set()

# Pool of ports we can use (8503-8512)
PORT_POOL = list(range(8503, 8513))

def get_available_port() -> int:
    """Get an available port from our pool"""
    available_ports = set(PORT_POOL) - used_ports
    if not available_ports:
        # If no ports available, clean up oldest process
        oldest_pid = None
        oldest_time = float('inf')
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                if proc.info['cmdline'] and any(arg for arg in proc.info['cmdline'] if 'streamlit' in arg):
                    if proc.info['create_time'] < oldest_time:
                        oldest_time = proc.info['create_time']
                        oldest_pid = proc.info['pid']
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        if oldest_pid:
            try:
                psutil.Process(oldest_pid).kill()
                print(f"Killed oldest process {oldest_pid} to free up port")
            except psutil.NoSuchProcess:
                pass
            
        # Try again after cleanup
        available_ports = set(PORT_POOL) - used_ports
        
    if not available_ports:
        raise RuntimeError("No ports available in pool")
        
    port = random.choice(list(available_ports))
    used_ports.add(port)
    return port

def release_port(port: int) -> None:
    """Release a port back to the pool"""
    used_ports.discard(port)

def kill_process_on_port(port):
    """Kill any process running on the specified port"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline']:
                for arg in proc.info['cmdline']:
                    if f"--server.port={port}" in arg:
                        try:
                            proc.kill()
                            print(f"Killed process {proc.info['pid']} on port {port}")
                            release_port(port)
                        except psutil.NoSuchProcess:
                            pass
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

def open_dashboard_with_report(report_path):
    dashboard_path = project_root / "ui" / "app.py"
    
    # Get an available port from our pool
    port = get_available_port()
    
    # Start new Streamlit process
    process = subprocess.Popen([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(dashboard_path),
        "--server.port",
        str(port),
        "--",  # Pass additional arguments to dashboard
        "--report",
        report_path
    ])
    
    # Show message to user
    st.success(f"Opening report viewer on port {port}...")
    
    # Return the process object so we can track it
    return process

# Function to get list of available strategies from the README
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

from core.config_manager.ui_adapter import UIConfigAdapter

def run_test(prompt, selected_strategies):
    """Run the test command with selected parameters"""
    try:
        # Initialize UI adapter
        adapter = UIConfigAdapter()
        
        # Run the test
        results = adapter.run_test(prompt, selected_strategies)
        
        # Convert results to string format
        return str(results), ""
    except Exception as e:
        return "", str(e)

def create_app_ui():
    """Create and display the main UI components"""
    # Main UI
    st.title("Compliant LLM UI")
    st.write("Test and analyze your AI prompts for security vulnerabilities")

    # Sidebar with report list
    with st.sidebar:

        # Add documentation link
        if st.button("Open Documentation"):
            try:
                # Get absolute path to docs.py
                docs_path = str(Path(__file__).parent / "docs.py")
                
                # Run the docs.py file
                subprocess.Popen(["streamlit", "run", docs_path])
                st.success("Opening documentation...")
            except Exception as e:
                st.error(f"Error opening documentation: {str(e)}")

        st.header("Test Reports")
        
        reports = get_reports()
        
        if not reports:
            st.info("No reports found. Run a test to generate reports.")
        else:
            st.write("### Recent Reports")
            for report in reports:
                if st.button(f"{report['name']} (Last modified: {report['modified']})"):
                    open_dashboard_with_report(report['path'])



    # Main content area
    st.header("Run New Test")

    # Prompt input
    with st.form("test_form", clear_on_submit=True):
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
            try:
                # Try to parse the output as JSON
                json_output = json.loads(stdout)
                
                # Create a container for the results
                with st.container():
                    st.success("Test Results")
                    
                    # Add some padding
                    st.markdown("""
                    <style>
                        .json-container {
                            background-color: #f8f9fa;
                            padding: 20px;
                            border-radius: 8px;
                            margin-top: 10px;
                        }
                    </style>
                    """, unsafe_allow_html=True)
                    
                    # Display JSON in a styled container
                    st.markdown("""
                    <div class="json-container">
                    """, unsafe_allow_html=True)
                    
                    # Display JSON with proper indentation
                    st.json(json.dumps(json_output, indent=2))
                    
                    st.markdown("""
                    </div>
                    """, unsafe_allow_html=True)
            except json.JSONDecodeError:
                # If not JSON, display as regular text
                st.success("Test Output:")
                st.code(stdout, language="text")
        
        if stderr:
            st.error("Error Output:")
            st.code(stderr, language="bash")


def main():
    """Main entry point for the app"""
    create_app_ui()

if __name__ == "__main__":
    main()
