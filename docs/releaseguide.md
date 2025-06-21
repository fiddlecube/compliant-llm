# Release Guide

This guide provides instructions for releasing new versions of Compliant LLM.

## Pre-release Checklist

Before creating a release, ensure you have completed the following:

1. **Code Review**: All changes have been reviewed and approved
2. **Testing**: All tests pass locally and in CI/CD
3. **Documentation**: Documentation is up to date
4. **Version Update**: Version numbers are updated in all relevant files
5. **Changelog**: CHANGELOG.md is updated with new features and fixes

Follow the [RELEASE_CHECKLIST](https://github.com/fiddlecube/compliant-llm/blob/main/RELEASE_CHECKLIST.md) before each release or pre-release.

## Pre-release Process

### 1. Update Version Numbers

Update the version number in the following files:

- `pyproject.toml`
- `setup.py`
- `core/__init__.py`

### 2. Update CHANGELOG.md

Add a new section for the release with:

- New features
- Bug fixes
- Breaking changes
- Known issues

### 3. Create Pre-release Tag

```bash
git tag -a v0.1.0-rc.1 -m "Release candidate 1 for v0.1.0"
git push origin v0.1.0-rc.1
```

### 4. Test Pre-release

Test the pre-release by running the CLI commands in the [Getting Started](https://github.com/fiddlecube/compliant-llm/blob/main/docs/getting_started.md) section.

### 5. Create GitHub Pre-release

1. Go to GitHub releases page
2. Click "Draft a new release"
3. Select the pre-release tag
4. Add release notes
5. Mark as pre-release
6. Publish

## Full Release Process

### 1. Final Testing

- Run all tests locally
- Test installation from PyPI
- Verify all documentation links work
- Test on different platforms

### 2. Update Documentation

- Make sure you list all the major changes in [CHANGELOG.md](https://github.com/fiddlecube/compliant-llm/blob/main/CHANGELOG.md)
- Update any version-specific documentation
- Verify all links are working

### 3. Build and Upload to PyPI

```bash
# Build the package
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

### 4. Create Release Tag

```bash
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

### 5. Create GitHub Release

1. Go to GitHub releases page
2. Click "Draft a new release"
3. Select the release tag
4. Add comprehensive release notes
5. Publish

### 6. Post-release Tasks

- Update development version numbers
- Announce release on social media
- Update any external documentation
- Monitor for any issues

## Testing the Release

Test the full release by running the CLI commands in the [Getting Started](https://github.com/fiddlecube/compliant-llm/blob/main/docs/getting_started.md) section.

## Rollback Plan

If issues are discovered after release:

1. **Immediate**: Mark the release as deprecated on PyPI
2. **Short-term**: Create a patch release with fixes
3. **Long-term**: Update documentation with known issues

## Release Schedule

- **Patch releases**: As needed for critical bug fixes
- **Minor releases**: Monthly for new features
- **Major releases**: Quarterly for breaking changes

## Communication

- Update the project README with latest version
- Post release notes on GitHub
- Notify stakeholders and contributors
- Update any external references

