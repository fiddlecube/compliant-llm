import sys
import time
import psutil
import subprocess
from pathlib import Path
from datetime import datetime
import streamlit as st
import random
from typing import Set
import json
import os
from dotenv import load_dotenv, set_key
import socket
from core.config_manager.ui_adapter import UIConfigAdapter
from rich.console import Console
from ui.constants.provider import PROVIDERS, PROVIDER_SETUP

console = Console()

# Constants
BASE_DIR = Path(__file__).parent
REPORTS_DIR = Path.home() / ".compliant-llm" / "reports"
PORT_POOL = list(range(8503, 8513))
used_ports: Set[int] = set()

# Ensure reports directory exists
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0

def kill_process_on_port(port):
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline'] and any(f"--server.port={port}" in arg for arg in proc.info['cmdline']):
                print(f"Killing process {proc.info['pid']} using port {port}")
                proc.kill()
                release_port(port)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            print(f"Could not kill process on port {port}: {e}")

def get_available_port() -> int:
    for port in PORT_POOL:
        if not is_port_in_use(port):
            used_ports.add(port)
            return port

    # Try to free one
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
        try:
            if proc.info['cmdline'] and any('streamlit' in arg for arg in proc.info['cmdline']):
                print(f"Killing oldest streamlit process: PID {proc.info['pid']}")
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Retry after cleanup
    for port in PORT_POOL:
        if not is_port_in_use(port):
            used_ports.add(port)
            return port

    raise RuntimeError("No ports available in pool")

def release_port(port: int) -> None:
    used_ports.discard(port)

def get_reports():
    reports = []
    if REPORTS_DIR.exists():
        for file in REPORTS_DIR.glob("*.json"):
            try:
                mod_time = datetime.fromtimestamp(file.stat().st_mtime)
                with open(file, 'r') as f:
                    report_data = json.load(f)
                    metadata = report_data.get('metadata', {})
                    runtime_seconds = metadata.get('elapsed_seconds', 0)
                    runtime_minutes = runtime_seconds / 60

                name_ts = file.stem.replace('report_', '')
                try:
                    name_time = datetime.strptime(name_ts, "%Y%m%d_%H%M%S")
                except ValueError:
                    name_time = mod_time

                reports.append({
                    "name": file.name,
                    "path": str(file),
                    "modified": mod_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "timestamp": name_time,
                    "runtime": f"{runtime_minutes:.1f} min" if runtime_minutes >= 1 else f"{runtime_seconds:.1f} sec"
                })
            except Exception as e:
                console.print(f"Dashboard: Error processing file: {file}\n{e}")
    return sorted(reports, key=lambda x: x["timestamp"], reverse=True)

def open_dashboard_with_report(report_path):
    dashboard_path = BASE_DIR / "app.py"
    port = get_available_port()
    kill_process_on_port(port)  # Extra safety
    st.success(f"🔗 Opening latest report: {report_path}")
    subprocess.Popen([
        sys.executable, "-m", "streamlit", "run",
        str(dashboard_path), "--server.port", str(port), "--",
        "--report", report_path
    ])

def get_available_strategies():
    return [
        "prompt_injection", "jailbreak", "excessive_agency",
        "indirect_prompt_injection", "insecure_output_handling",
        "model_dos", "model_extraction", "sensitive_info_disclosure",
        "context_manipulation"
    ]

def run_test(prompt, selected_strategies, config):
    try:
        adapter = UIConfigAdapter()
        # adapter.update_config(config)
        results = adapter.run_test(prompt, selected_strategies, config)
        return json.dumps(results), ""
    except Exception as e:
        return "", str(e)

def render_beautiful_json_output(json_output):
    with st.expander("🔍 View JSON"):
        st.code(json.dumps(json_output, indent=2), language="json")

def create_app_ui():
    st.title("Compliant LLM UI")
    st.write("Test and analyze your AI prompts for security vulnerabilities")

    # sidebar of main page
    with st.sidebar:
        if st.button("Open Documentation"):
            try:
                subprocess.Popen(["streamlit", "run", str(BASE_DIR / "docs.py")])
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
                formatted_time = report['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                if st.button(
                    f"Report {i+1}. (Runtime: {report['runtime']}, Run at: {formatted_time})",
                    key=f"report_{report['name']}"):
                    selected_report_path = report['path']
                    st.session_state['selected_report'] = selected_report_path
                    st.rerun()

    if 'selected_report' in st.session_state:
        open_dashboard_with_report(st.session_state['selected_report'])
        del st.session_state['selected_report']

    # Variable to control submit button state
    submit_disabled = True
    
    # configuration payload
    config = {}
    
    # main content
    st.header("Setup Configuration")
    
    # Configuration form
    # Initialize session state for saved config
    if 'saved_config' not in st.session_state:
        st.session_state['saved_config'] = {}

    # Select provider outside the form so it reruns on change
    provider_name = st.selectbox(
        "Select Provider", [p["name"] for p in PROVIDER_SETUP]
    )
    provider = next(p for p in PROVIDER_SETUP if p["name"] == provider_name)

    # Form for entering keys
    with st.form("provider_form"):
        # Dynamically create input fields for the selected provider
        inputs = {}
        for key in provider:
            if key in ("name", "value"):
                continue
            label = key.replace("_", " ").title()
            env_key = f"{provider['value'].upper()}_{key.upper()}"
            default_val = os.getenv(env_key, "")
            inputs[key] = st.text_input(label, value=default_val)

        submitted = st.form_submit_button("Save Config")

        if submitted:
            env_path = ".env"
            if not os.path.exists(env_path):
                open(env_path, "w").close()

            config = {'provider': provider['value']}
            for field, val in inputs.items():
                env_key = f"{provider['value'].upper()}_{field.upper()}"
                set_key(env_path, env_key, val)
                # Set in-process environment for immediate use
                os.environ[env_key] = val
                st.success(f"Configuration for {provider_name} saved to .env and loaded into session")
                config[field] = val
    st.write(config)
    # st.session_state['saved_config'] = config
    

    st.header("Run New Test")
    with st.form("test_form", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            prompt = st.text_area("Enter your prompt:", height=150, placeholder="Enter your system prompt here...")
        with col2:
            st.write("### Select Testing Strategies")
            selected_strategies = st.multiselect("Choose strategies to test", get_available_strategies(), default=["prompt_injection", "jailbreak"])
        submit_button = st.form_submit_button(label="Run Test", type="primary", disabled=submit_disabled)

    if submit_button:
        if not prompt.strip():
            st.error("🚫 Please enter a prompt!")
            st.stop()
        if not selected_strategies:
            st.error("🚫 Please select at least one testing strategy!")
            st.stop()

        with st.spinner("🔍 Running tests..."):
            stdout, stderr = run_test(prompt, selected_strategies, config)
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

        if reports:
            latest_report = reports[0]
            open_dashboard_with_report(latest_report["path"])

def main():
    create_app_ui()

if __name__ == "__main__":
    main()
