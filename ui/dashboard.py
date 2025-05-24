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

# Constants
BASE_DIR = Path(__file__).parent
REPORTS_DIR = Path.home() / ".compliant-llm" / "reports"
PORT_POOL = list(range(8503, 8513))
used_ports: Set[int] = set()

# Ensure reports directory exists
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

@st.cache_data(show_spinner=False)
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

def get_available_port() -> int:
    available_ports = set(PORT_POOL) - used_ports
    if not available_ports:
        oldest_pid = None
        oldest_time = float('inf')
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                if proc.info['cmdline'] and any('streamlit' in arg for arg in proc.info['cmdline']):
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
        available_ports = set(PORT_POOL) - used_ports

    if not available_ports:
        raise RuntimeError("No ports available in pool")

    port = random.choice(list(available_ports))
    used_ports.add(port)
    return port

def release_port(port: int) -> None:
    used_ports.discard(port)

def kill_process_on_port(port):
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline'] and any(f"--server.port={port}" in arg for arg in proc.info['cmdline']):
                proc.kill()
                release_port(port)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

def open_dashboard_with_report(report_path):
    dashboard_path = BASE_DIR / "app.py"
    port = get_available_port()
    subprocess.Popen([
        sys.executable, "-m", "streamlit", "run",
        str(dashboard_path), "--server.port", str(port), "--",
        "--report", report_path
    ])
    st.success(f"Opening report viewer on port {port}...")

def get_available_strategies():
    return [
        "prompt_injection", "jailbreak", "excessive_agency",
        "indirect_prompt_injection", "insecure_output_handling",
        "model_dos", "model_extraction", "sensitive_info_disclosure"
    ]

def run_test(prompt, selected_strategies):
    try:
        adapter = UIConfigAdapter()
        results = adapter.run_test(prompt, selected_strategies)
        return json.dumps(results), ""
    except Exception as e:
        return "", str(e)

def render_beautiful_json_output(json_output):
    with st.expander("🔍 View JSON"):
        st.code(json.dumps(json_output, indent=2), language="json")

def create_app_ui():
    st.title("Compliant LLM UI")
    st.write("Test and analyze your AI prompts for security vulnerabilities")

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
                    open_dashboard_with_report(report['path'])

    st.header("Run New Test")
    with st.form("test_form", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            prompt = st.text_area("Enter your prompt:", height=150, placeholder="Enter your system prompt here...")
        with col2:
            st.write("### Select Testing Strategies")
            selected_strategies = st.multiselect("Choose strategies to test", get_available_strategies(), default=["prompt_injection", "jailbreak"])
        submit_button = st.form_submit_button("Run Test")

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

        if reports:
            latest_report = reports[0]
            st.success(f"🔗 Opening latest report: `{latest_report['name']}`")
            open_dashboard_with_report(latest_report["path"])

def main():
    create_app_ui()

if __name__ == "__main__":
    main()
