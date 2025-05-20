# Migration Guide: pyenv to uv

This guide will help you migrate from pyenv to uv for Python environment and package management.

## What is uv?

uv is a modern Python package installer and resolver written in Rust. It's designed to be a faster, more reliable alternative to pip and other Python package managers.

## Migration Steps

### 1. Virtual Environment Management

**With pyenv (old way):**
```bash
# Create a virtual environment
pyenv virtualenv 3.11.4 my-project-env
# Activate the environment
pyenv activate my-project-env
```

**With uv (new way):**
```bash
# Create a virtual environment
uv venv .venv
# Activate the environment
source .venv/bin/activate
```

### 2. Package Installation

**With pip (old way):**
```bash
pip install -e .
pip install -e ".[dev]"
```

**With uv (new way):**
```bash
uv pip install -e .
uv pip install pytest flake8 black mypy  # Install dev dependencies
```

### 3. Managing Dependencies

**With pip (old way):**
```bash
pip freeze > requirements.txt
pip install -r requirements.txt
```

**With uv (new way):**
```bash
# Generate a lock file
uv pip freeze > requirements-lock.txt
# Install from lock file
uv pip install -r requirements-lock.txt
```

## Workflow Changes

1. **Environment Activation**: Use `source .venv/bin/activate` instead of `pyenv activate`
2. **Package Installation**: Use `uv pip install` instead of `pip install`
3. **Dependency Management**: Use `uv pip freeze` and `uv pip install -r` for dependency management

## Benefits of uv

- **Speed**: uv is significantly faster than pip for package installation and resolution
- **Reliability**: Better dependency resolution with fewer conflicts
- **Compatibility**: Works with existing Python projects and tools
- **Modern Features**: Better caching, parallel downloads, and more

## Additional uv Commands

- `uv pip list` - List installed packages
- `uv pip uninstall <package>` - Uninstall a package
- `uv pip show <package>` - Show information about a package
- `uv pip check` - Verify installed packages have compatible dependencies

## Troubleshooting

If you encounter any issues with the migration, try the following:

1. Ensure you're using the latest version of uv: `uv --version`
2. If a package fails to install, try installing it with `--no-binary`: `uv pip install --no-binary :all: <package>`
3. For any compatibility issues, you can always fall back to pip within the virtual environment: `pip install <package>`
