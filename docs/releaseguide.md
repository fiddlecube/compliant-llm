# Release Guide

A guide for developers to release a new version of the project

## Setup

```bash
# Clone the repository
git clone https://github.com/fiddlecube/compliant-llm.git
cd compliant-llm

# Install in development mode
uv pip install -e .
```

## Release Process

Follow the [RELEASE_CHECKLIST](https://github.com/fiddlecube/compliant-llm/blob/main/RELEASE_CHECKLIST.md) before each release or pre-release.

After testing the release candidate thoroughly, first create a pre-release.

### Pre-release Guide

Publish the package to TestPyPI and test it before a full release.

For creating a pre-release:

- Create a branch in the format `vX.Y.Z-alphaN` where `N` is the release candidate number.

```bash
# Create a new branch
git checkout -b vX.Y.Z-alphaN
```

- Update version number in `pyproject.toml`

```toml
version = "X.Y.Z-alphaN"
```

- Commit the changes

```bash
git add pyproject.toml

git commit -m "Release vX.Y.Z-alphaN"
```

- Add the tag `vX.Y.Z-alphaN` to the branch

```bash
git tag vX.Y.Z-alphaN
```

- Push the branch and tag to GitHub

```bash
git push origin vX.Y.Z-alphaN
git push origin vX.Y.Z-alphaN --tags
```

Once the tag is pushed, you will see a github action running that will publish the package to TestPyPI.

Test the pre-release by installing it from TestPyPI:

```bash
pip install -i https://test.pypi.org/simple compliant-llm==X.Y.Z-aN # Note: make sure to match the version number to install the correct pre-release
```

Test the pre-release by running the CLI commands in the [Quick Start](https://github.com/fiddlecube/compliant-llm/blob/main/docs/quickstart.md) section.

Merge the release branch into main and push it to GitHub.

### Full Release Guide

Publish the package to PyPI and release it to the public.

For creating a full release:

- Make sure you list all the major changes in [CHANGELOG.md](https://github.com/fiddlecube/compliant-llm/blob/main/CHANGELOG.md)
- Create a branch in the format `vX.Y.Z` where `X.Y.Z` is the release version.

```bash
# Create a new branch
git checkout -b vX.Y.Z
```

- Update version number in `pyproject.toml`

```toml
version = "X.Y.Z"
```

- Commit the changes

```bash
git add pyproject.toml

git commit -m "Release vX.Y.Z"
```

- Add the tag `vX.Y.Z` to the branch

```bash
git tag vX.Y.Z
```

- Push the branch and tag to GitHub

```bash
git push origin vX.Y.Z
git push origin vX.Y.Z --tags
```

Once the tag is pushed, you will see a github action running that will publish the package to PyPI.

Test the full release by installing it from PyPI:

```bash
pip install compliant-llm==X.Y.Z
```

Test the full release by running the CLI commands in the [Quick Start](https://github.com/fiddlecube/compliant-llm/blob/main/docs/quickstart.md) section.

