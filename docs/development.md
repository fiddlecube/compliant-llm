# Development Guide

## Setting up the development environment

```bash
uv venv .venv
source .venv/bin/activate
uv pip install -e .
uv pip install -e ".[dev]"
```

## Running Commands

```bash
compliant-llm test --prompt "You are a helpful assistant who can only respond ethically" --strategy "prompt_injection,jailbreak"
compliant-llm dashboard
compliant-llm report --summary
```

## Running Tests

```bash
pytest
```

