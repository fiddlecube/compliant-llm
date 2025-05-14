# Installation Guide

This guide provides instructions for installing FC Prompt Tester on your system.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Access to at least one LLM provider API (OpenAI, Anthropic, or Google)

## Installation Methods

### Installing from PyPI (Recommended)

The simplest way to install FC Prompt Tester is using pip:

```bash
pip install fc-prompt-tester
```

### Installing from Source

For the latest development version or to contribute to the project, you can install from source:

```bash
# Clone the repository
git clone https://github.com/yourusername/fc-prompt-tester.git
cd fc-prompt-tester

# Install in development mode
pip install -e .
```

### Development Installation

#### Install in development mode from the project directory
`pip install -e .`

#### After installation, you should be able to use these commands:
`fc-test test --prompt "You are a helpful assistant."`
`fc-test report`
`fc-test generate config --output configs/my_config.yaml`
`fc-test config --list`

## Verifying Installation

To verify that FC Prompt Tester is correctly installed, run:

```bash
python -m cli.main --version
```

This should display the version number of FC Prompt Tester.

## API Key Setup

FC Prompt Tester requires API keys for the LLM providers you want to use. Set these as environment variables:

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

## Installing Optional Dependencies

### For Development

If you want to contribute to FC Prompt Tester or run tests, install the development dependencies:

```bash
pip install -e ".[dev]"
```

### For Visualization Features

For enhanced report visualization:

```bash
pip install -e ".[viz]"
```

## Troubleshooting

### Common Installation Issues

#### Missing Dependencies

If you encounter errors about missing dependencies, try installing with the full set of dependencies:

```bash
pip install -e ".[all]"
```

#### Permission Errors

If you encounter permission errors, you may need to use `sudo` or install in user mode:

```bash
pip install --user fc-prompt-tester
```

#### API Connection Issues

If the tests run but fail to connect to the API:

1. Verify your API key is correct
2. Check your internet connection
3. Ensure the API service is available
4. Check for any rate limiting or quota issues

## Next Steps

After installation, proceed to the [Quick Start Guide](quickstart.md) to begin using FC Prompt Tester.
