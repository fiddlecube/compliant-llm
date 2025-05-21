# Release Checklist for Compliant LLM

This checklist helps ensure a smooth release process for new versions of the Compliant LLM package.

## Before Release

### Code Preparation
- [ ] Update version number in `pyproject.toml`
- [ ] Update `CHANGELOG.md` with all notable changes
- [ ] Ensure all tests pass locally: `pytest`
- [ ] Check code quality with linters: `flake8`, `black`, `mypy`
- [ ] Verify all documentation is up to date
- [ ] Make sure all CI checks pass on the main branch

### Package Testing
- [ ] Build the package locally:
  ```bash
  uv pip install build
  python -m build
  ```
- [ ] Test installation from local build:
  ```bash
  uv pip install dist/compliant-llm-X.Y.Z-py3-none-any.whl
  ```
- [ ] Verify the installed package works as expected

## Creating the Release

### Git Operations
- [ ] Commit all changes: `git commit -m "Prepare release vX.Y.Z"`
- [ ] Tag the release: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
- [ ] Push changes and tag: `git push origin main && git push origin vX.Y.Z`

### GitHub Release
- [ ] Go to GitHub Releases page
- [ ] Create a new release using the tag
- [ ] Copy relevant section from CHANGELOG.md to the release notes
- [ ] Mark as pre-release if applicable
- [ ] Publish release (this will trigger the GitHub Actions workflow)

### Verify Publication
- [ ] Check GitHub Actions workflow completed successfully
- [ ] Verify package is available on TestPyPI (for pre-releases)
- [ ] Verify package is available on PyPI (for full releases)
- [ ] Test installation from PyPI:
  ```bash
  uv pip install compliant-llm==X.Y.Z
  ```

## After Release

- [ ] Update version in `pyproject.toml` to next development version (X.Y.Z-dev)
- [ ] Announce the release to relevant channels (if applicable)
- [ ] Close related issues and milestones in GitHub
- [ ] Review and address any feedback from early adopters

## PyPI Secrets Setup (First-time only)

To enable automated publishing to PyPI, add these secrets to your GitHub repository:

1. Go to your GitHub repository → Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `PYPI_USERNAME`: Your PyPI username
   - `PYPI_PASSWORD`: Your PyPI password or token (preferred)
   - `TEST_PYPI_USERNAME`: Your TestPyPI username
   - `TEST_PYPI_PASSWORD`: Your TestPyPI password or token (preferred)
