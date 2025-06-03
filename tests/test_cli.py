#!/usr/bin/env python3
"""
Test script for Compliant LLM CLI commands.
Checks if the CLI can run attacks and generate reports for a single prompt.
"""
import os
import json
import subprocess
import pytest


@pytest.mark.skip(reason="Test disabled by user request")
def test_cli_commands():
    """Test the Compliant LLM CLI commands for running attacks and generating reports."""
    print("Starting Compliant LLM CLI test...")
    
    # Define our test report path - note the CLI uses the reports directory
    report_path = "reports/report.json"
    
    # Create a simple test prompt - direct input instead of file
    test_prompt = "You are a helpful assistant for a banking organization. Always be professional and courteous."
    
    try:
        # Test Step 1: Run the test command with direct prompt input
        print("\n1. Testing 'test' command with a direct prompt...")
        test_cmd = [
            "python", "-m", "cli.main", "test",
            "--prompt", test_prompt,  # Direct prompt content
            "--strategy", "prompt_injection,jailbreak",  # Using fewer strategies for quicker testing
            "--provider", "openai/gpt-3.5-turbo", 
            "--output", report_path,
            "--verbose"
        ]
        
        print(f"Running command: {' '.join(test_cmd)}")
        test_result = subprocess.run(test_cmd, capture_output=True, text=True)
        
        # Check if the command executed successfully
        if test_result.returncode != 0:
            print("ERROR: Test command failed!")
            print(f"Exit code: {test_result.returncode}")
            print(f"STDOUT: {test_result.stdout}")
            print(f"STDERR: {test_result.stderr}")
            return False
        
        print("Test command executed successfully!")
        print(f"Command output:\n{test_result.stdout}")
        
        # Test Step 2: Check if report was generated
        if not os.path.exists(report_path):
            print(f"ERROR: Report file not found at {report_path}")
            return False
        
        print(f"Report file found at {report_path}")
        
        # Test Step 3: Verify report structure
        try:
            with open(report_path, 'r') as f:
                report_data = json.load(f)
            
            # Check if report has expected structure
            if "metadata" not in report_data or "tests" not in report_data:
                print("ERROR: Report is missing expected structure (metadata and tests)")
                return False
            
            # Verify that tests were run
            test_count = len(report_data["tests"])
            if test_count == 0:
                print("ERROR: No tests were executed")
                return False
            
            print(f"Report contains {test_count} test results")
            print(f"Test strategies used: {report_data['metadata'].get('strategies', 'Unknown')}")
            
            # Test Step 4: Test the report command
            print("\n2. Testing 'report' command...")
            report_cmd = [
                "python", "-m", "cli.main", "report",
                report_path,  # Positional argument, not an option
                "--summary"
            ]
            
            print(f"Running command: {' '.join(report_cmd)}")
            report_result = subprocess.run(report_cmd, capture_output=True, text=True)
            
            if report_result.returncode != 0:
                print("ERROR: Report command failed!")
                print(f"Exit code: {report_result.returncode}")
                print(f"STDOUT: {report_result.stdout}")
                print(f"STDERR: {report_result.stderr}")
                assert False
            
            print("Report command executed successfully!")
            print(f"Command output:\n{report_result.stdout}")
            
            print("\nAll CLI tests passed successfully!")
            assert True
            
        except json.JSONDecodeError:
            print(f"ERROR: Report file {report_path} is not valid JSON")
            assert False
    
    finally:
        # Clean up temporary files
        try:
            if os.path.exists(report_path):
                os.unlink(report_path)
        except Exception as e:
            print(f"Warning: Error cleaning up temporary files: {e}")


if __name__ == "__main__":
    success = test_cli_commands()
    exit(0 if success else 1)
