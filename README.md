# README.md
# FC Prompt Tester

Run tests on system prompts using CLI or UI dashboard.

# Create a virtualenv
pyenv virtualenv 3.11.4 fc_prompt

# Activate the virtualenv
pyenv activate fc_prompt
```

**Note**: You need to ensure that the virtualenv is activated before you initiate a local run, including tests, static analysis and linting.

## Installation
```bash
pip install .
```

## Usage
```bash
fc-test --config configs/default_config.yaml
fc-ui
```

## Docker
```bash
docker build -t fc-prompt-tester .
docker run -p 8501:8501 fc-prompt-tester