# Installation Guide

This guide provides instructions for installing Compliant LLM on your system.

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Access to at least one LLM provider API (OpenAI, Anthropic, or Google)

## Installation Methods

### Installing from PyPI (Recommended)

The simplest way to install Compliant LLM is using pip:

```bash
pip install compliant-llm
```

### Installing from Source

For the latest development version or to contribute to the project, you can install from source:

```bash
# Clone the repository
git clone https://github.com/fiddlecube/compliant-llm.git
cd compliant-llm

# Install the package from source
pip install -e .
```

## Run the dashboard

```bash
compliant-llm dashboard
```

Connect to your LLM provider and run attacks against your prompts.

## Verifying Installation

To verify that Compliant LLM is correctly installed, run:

```bash
compliant-llm --version
```

#### Missing Dependencies

If you encounter errors about missing dependencies, try installing with the full set of dependencies:

```bash
pip install -e ".[all]"
```

#### Permission Errors

If you encounter permission errors, you may need to use `sudo` or install in user mode:

```bash
pip install compliant-llm
```

#### API Connection Issues

If the tests run but fail to connect to the API:

1. Verify your API key is correct
2. Check your internet connection
3. Ensure the API service is available
4. Check for any rate limiting or quota issues

## Next Steps

After installation, proceed to the [Getting Started Guide](getting_started.md) to begin using Compliant LLM.
