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
from dotenv import load_dotenv, set_key, get_key
import socket
from core.config_manager.ui_adapter import UIConfigAdapter

from rich.console import Console
from ui.constants.provider import PROVIDER_SETUP
from core.analytics.tracker import UsageEvent, InteractionType, ErrorEvent, analytics_tracker

console = Console()
load_dotenv()
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
        analytics_tracker.track(UsageEvent(
            name="test",
            interaction_type=InteractionType.DASHBOARD,
            command="run_test"
        ))
        return json.dumps(results), ""
    except Exception as e:
        analytics_tracker.track(ErrorEvent(
            name="test",
            interaction_type=InteractionType.DASHBOARD,
            command="run_test",
            error_msg=str(e)
        ))
        return "", str(e)

def render_beautiful_json_output(json_output):
    container = st.container(height=500, border=True)
    with container:
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
    

    # Form for entering keys
    with st.expander("Setup Configuration", expanded=True):
        has_all_keys = False
        if 'saved_config' not in st.session_state:
            st.session_state['saved_config'] = {}

        # Select provider outside the form so it reruns on change
        provider_name = st.selectbox(
            "Select Provider", [p["name"] for p in PROVIDER_SETUP],
            index=len(PROVIDER_SETUP) - 1
        )
        provider = next(p for p in PROVIDER_SETUP if p["name"] == provider_name)
        
        with st.form("provider_form", border=False):
            # Dynamically create input fields for the selected provider
            inputs = {}
            model = st.text_input(
                        "Enter Model", provider["default_model"]
                    )
            for key in provider:
                if key in ("name", "value", "default_model", "provider_name"):
                    continue
                label = key.replace("_", " ").title()
                env_key = f"{key.upper()}"
                default_val = os.getenv(env_key, "") or get_key(".env", env_key)
                if default_val is None:
                    has_all_keys = False
                else:
                    has_all_keys = True
                inputs[key] = st.text_input(label, value=default_val, type="password" if "API_KEY" in env_key else "default")

            submitted = st.form_submit_button("Setup Config")

            if submitted:
                if not provider_name:
                    st.error("Please select a provider")
                    return
                if not model:
                    st.error("Please select a model")
                    return
                
                empty_fields = [key for key, value in inputs.items() if not value.strip()]
                if empty_fields:
                    st.error(f"Please fill in all required fields: {', '.join(empty_fields)}")
                    return
                
                env_path = ".env"
                if not os.path.exists(env_path):
                    open(env_path, "w").close()

                config = {'provider_name': provider['provider_name'], 'model': model}

                for field, val in inputs.items():
                    
                    env_key = f"{field.upper()}"
                    set_key(env_path, env_key, val)
                    # Set in-process environment for immediate use
                    os.environ[env_key] = val
                    # st.success(f"Configuration for {provider_name} saved to .env and loaded into session")
                    config[field] = val

                st.session_state['saved_config'] = config
                st.write("Configuration saved successfully", config)
    
    # Form for running tests
    with st.expander("Run New Test", expanded=True):
        submit_button_disabled = True
        provider_config = st.session_state['saved_config']

        if provider_config or has_all_keys:
            submit_button_disabled = False
        with st.form("test_form", clear_on_submit=True, border=False):
            prompt = st.text_area("Enter your prompt:", height=150, placeholder="Enter your system prompt here...")
            st.write("### Select Testing Strategies")
            selected_strategies = st.multiselect("Choose strategies to test", get_available_strategies(), default=["prompt_injection", "jailbreak"])
            submit_button = st.form_submit_button(label="Run Test", type="primary", disabled=submit_button_disabled)

        if submit_button:
            if not prompt.strip():
                st.error("🚫 Please enter a prompt!")
                st.stop()
            if not selected_strategies:
                st.error("🚫 Please select at least one testing strategy!")
                st.stop()

            with st.spinner("🔍 Running tests..."):
                stdout, stderr = run_test(prompt, selected_strategies, provider_config)
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
