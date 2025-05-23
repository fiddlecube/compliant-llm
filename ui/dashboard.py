import streamlit as st
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import psutil
import random
from typing import Set
import json
import os
from core.config_manager.ui_adapter import UIConfigAdapter

from rich.console import Console
console = Console()

# Get user's home directory for storing reports
user_home = Path.home()
reports_dir = user_home / ".compliant-llm" / "reports"

# Create reports directory if it doesn't exist
reports_dir.mkdir(parents=True, exist_ok=True)

# Function to get list of reports with timestamps
def get_reports():
    reports = []
    if reports_dir.exists():
        for file in reports_dir.glob("*.json"):
            try:
                # Get modification time
                mod_time = datetime.fromtimestamp(file.stat().st_mtime)
                
                # Read report file to get runtime information
                with open(file, 'r') as f:
                    report_data = json.load(f)
                    metadata = report_data.get('metadata', {})
                    runtime_seconds = metadata.get('elapsed_seconds', 0)
                    runtime_minutes = runtime_seconds / 60
                    
                reports.append({
                    "name": file.name,
                    "path": str(file),
                    "modified": mod_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "runtime": f"{runtime_minutes:.1f} min" if runtime_minutes >= 1 else f"{runtime_seconds:.1f} sec"
                })
            except Exception as e:
                console.print(f"Dashboard: Error processing file: {file}")
                console.print(f"Dashboard: Error: {e}")
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
    # Get the directory where the current script is installed
    current_dir = Path(__file__).parent
    dashboard_path = current_dir / "app.py"
    
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


def run_test(prompt, selected_strategies):
    """Run the test command with selected parameters"""
    try:
        # Initialize UI adapter
        adapter = UIConfigAdapter()
        
        # Run the test
        results = adapter.run_test(prompt, selected_strategies)
        
 # Convert results to proper JSON string
        return json.dumps(results), ""
    except Exception as e:
        return "", str(e)



def render_beautiful_json_output(json_output):

    with st.expander("🔍 View JSON"):
        st.code(json.dumps(json_output, indent=2), language="json")

    def render_nested_json(data, level=0):
        if isinstance(data, dict):
            for k, v in data.items():
                with st.expander(f"{'  ' * level}🔑 {k}"):
                    render_nested_json(v, level + 1)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                with st.expander(f"{'  ' * level}📄 Item {i+1}"):
                    render_nested_json(item, level + 1)
        else:
            st.markdown(f"**Value:** `{data}`")


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
            for i, report in enumerate(reports):
                # Extract timestamp from filename
                timestamp_str = report['name'].replace('report_', '').replace('.json', '')
                timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                formatted_time = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                
                report_button = st.button(
                    f"Report {i+1}. (Runtime: {report['runtime']}, Run at: {formatted_time})",
                    key=f"report_{report['name']}"
                )
                if report_button:
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
        if not prompt.strip():
            st.error("🚫 Please enter a prompt!")
            st.stop()

        if not selected_strategies:
            st.error("🚫 Please select at least one testing strategy!")
            st.stop()

        with st.spinner("🔍 Running tests..."):
            stdout, stderr = run_test(prompt, selected_strategies)
            reports = get_reports()

        st.subheader("✅ Test Results")
        st.write("---")

        if stdout:
            try:
                json_output = json.loads(stdout)
                render_beautiful_json_output(json_output)
            except json.JSONDecodeError:
                st.warning("⚠️ Output is not valid JSON. Showing raw output instead:")
                st.code(stdout, language="text")
        else:
            st.info("ℹ️ No test output received.")

        if stderr:
            st.error("❌ Error Output:")
            st.code(stderr, language="bash")



def main():
    """Main entry point for the app"""
    create_app_ui()

if __name__ == "__main__":
    main()
