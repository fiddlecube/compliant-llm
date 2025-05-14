# Contributing to FC Prompt Tester

Thank you for considering contributing to FC Prompt Tester! This document outlines the process for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct.

## How Can I Contribute?

### Reporting Bugs

- Check if the bug has already been reported
- Use the bug report template when opening an issue
- Include detailed steps to reproduce the bug
- Include relevant details about your environment

### Suggesting Features

- Check if the feature has already been suggested
- Use the feature request template when opening an issue
- Explain why this feature would be useful to most users

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Setup

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/fc-prompt-tester.git
   cd fc-prompt-tester
   ```

2. Create a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies
   ```bash
   pip install -e ".[dev]"
   ```

4. Run tests
   ```bash
   pytest
   ```

## Coding Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to all functions, classes, and modules
- Keep functions focused on a single responsibility

## Testing

- Write tests for any new functionality
- Ensure all tests pass before submitting a PR
- Aim for high test coverage

## Documentation

- Update documentation to reflect any changes
- Keep the API documentation up to date
- Add examples for new features

Thank you for your contributions!
