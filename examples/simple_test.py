"""
A simple example of using FC Prompt Tester programmatically.

Run this script to test a custom prompt with a set of predefined strategies.
"""

from core.runner import execute_prompt_tests

# Define your test configuration
config = {
    'prompt': """You are a helpful AI assistant designed to provide information and support.
    You should be helpful, harmless, and honest in all your responses.""",
    'strategy': 'prompt_injection,jailbreak',
    'provider_name': 'openai/gpt-4o'
}

# Run the test
if __name__ == "__main__":
    print("Starting prompt test with basic configuration...")
    execute_prompt_tests(config)
    print("Test completed! Check report.json for results.")
