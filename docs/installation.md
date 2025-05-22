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

# Activate the uv venv.
# Install uv if you don't have it
uv venv .venv
source .venv/bin/activate

# Install the package from source
uv pip install -e .

# This installs the compliant-llm package in the current venv
```

### After installation, you should be able to use these commands:
`compliant-llm test --prompt "You are a helpful assistant."`
`compliant-llm report`
`compliant-llm generate config --output configs/config.yaml`
`compliant-llm config --list`

## Verifying Installation

To verify that Compliant LLM is correctly installed, run:

```bash
compliant-llm --version
```

This should display the version number of Compliant LLM.

## API Key Setup

Compliant LLM requires API keys for the LLM providers you want to use. Set these as environment variables:

### OpenAI API Key

```bash
export OPENAI_API_KEY=your-api-key-here
```

### Anthropic API Key (Optional)

```bash
export ANTHROPIC_API_KEY=your-anthropic-key
```

### Google API Key (Optional)

```bash
export GOOGLE_API_KEY=your-google-key
```

You can also create a `.env` file in your project root with these variables.


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

After installation, proceed to the [Quick Start Guide](quickstart.md) to begin using Compliant LLM.
