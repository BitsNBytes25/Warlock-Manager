# PyPI Deployment Guide

This guide explains how to use the GitHub Actions workflows to deploy your project to PyPI.

## Overview

Three workflows have been created:

1. **tests.yml** - Runs tests and code quality checks on push and pull requests
2. **publish-to-testpypi.yml** - Publishes test releases to TestPyPI (optional)
3. **publish-to-pypi.yml** - Publishes releases to PyPI

## Setup Instructions

### Step 1: Configure PyPI Access with Trusted Publisher

The recommended approach is to use PyPI's **Trusted Publisher** feature with OIDC (OpenID Connect). This requires no secret token management.

1. Go to your [PyPI Account Settings](https://pypi.org/manage/account/)
2. Navigate to "Publishing" section
3. Add a new trusted publisher with these details:
   - **PyPI Project Name**: `warlock-manager`
   - **Owner**: Your GitHub username (e.g., `BitsNBytes25`)
   - **Repository Name**: `Warlock-Manager`
   - **Workflow Name**: `publish-to-pypi.yml`
   - **Environment Name**: `pypi`

### Step 2: Create GitHub Environments (Optional but Recommended)

For added security, create GitHub environments:

1. Go to your repository settings on GitHub
2. Navigate to Environments
3. Create two environments (if using TestPyPI):
   - `pypi` - for production PyPI deployments
   - `testpypi` - for test deployments

You can add protection rules to require approval before deployments.

### Step 3: Verify Your Repository is Public (or Configure Accordingly)

For the Trusted Publisher flow to work:
- Public repositories: No additional configuration needed
- Private repositories: You'll need to manage PyPI tokens via GitHub Secrets instead

### Step 4: Tag a Release

To publish to PyPI, create a GitHub release:

```bash
# Create and push a version tag
git tag -a v2.1.0 -m "Release version 2.1.0"
git push origin v2.1.0
```

Then create a GitHub Release from the tag via the web interface, and the workflow will automatically:
1. Build the distribution packages
2. Check the build with `twine check`
3. Upload to PyPI

## Version Management

### Updating Versions

The version is defined in `pyproject.toml`. Update it before creating a release:

```toml
[project]
version = "2.1.1"  # Update this
```

Then commit and tag:

```bash
git add pyproject.toml
git commit -m "Bump version to 2.1.1"
git tag -a v2.1.1 -m "Release version 2.1.1"
git push origin main
git push origin v2.1.1
```

## Workflow Details

### Tests Workflow (tests.yml)

Runs on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

Actions:
- Tests on Python 3.10, 3.11, 3.12, 3.13
- Code coverage reporting to Codecov
- Flake8 linting checks

### TestPyPI Workflow (publish-to-testpypi.yml)

Runs on:
- Push to `develop` branch
- When `pyproject.toml` or source code changes

Purpose:
- Test your build process before production
- Verify package integrity
- Test installation from TestPyPI

To test:
```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ warlock-manager
```

### PyPI Workflow (publish-to-pypi.yml)

Runs on:
- Release published on GitHub
- Manual workflow dispatch (optional)

Actions:
1. Builds distribution packages (wheel and sdist)
2. Checks with `twine check` for metadata issues
3. Uploads to PyPI using Trusted Publisher authentication

## Manual Deployment (Alternative)

If Trusted Publisher isn't set up, you can manually deploy:

1. Generate a PyPI API token from [PyPI Account Settings](https://pypi.org/manage/account/#api-tokens)
2. Add it as a GitHub Secret: `PYPI_API_TOKEN`
3. Update the publish workflow to use the token instead

### Using PyPI Token (Not Recommended)

If you need to use a token-based approach:

```yaml
# In publish-to-pypi.yml, replace the publish step with:
- name: Publish to PyPI
  env:
    TWINE_USERNAME: __token__
    TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
  run: |
    twine upload dist/*
```

## Troubleshooting

### Build Fails

1. Check the workflow logs in GitHub Actions
2. Verify `pyproject.toml` syntax
3. Ensure all required dependencies are listed
4. Run locally: `python -m build`

### Upload Fails

1. Verify PyPI credentials/Trusted Publisher setup
2. Check package version isn't already on PyPI
3. Ensure package name is correct in `pyproject.toml`
4. Check file size limits (PyPI has 60MB limit per file)

### Tests Fail

1. Run tests locally: `pytest`
2. Check coverage: `pytest --cov=warlock_manager`
3. Run flake8: `flake8 warlock_manager tests`

## Best Practices

1. **Always test first**: Use TestPyPI before production
2. **Update CHANGELOG**: Document changes before releasing
3. **Tag consistently**: Use semantic versioning (v2.1.0, v2.1.1, etc.)
4. **Review metadata**: Ensure README.md and classifiers are up-to-date
5. **Test installation**: Install from PyPI and verify functionality

## References

- [PyPI Trusted Publishers Documentation](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions: Configuring OpenID Connect in PyPI](https://docs.github.io/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect#configuring-oidc-with-pypi)
- [Build and Publish Guide](https://packaging.python.org/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)

## What's Next?

1. Set up the Trusted Publisher on PyPI
2. Commit the workflow files to your repository
3. Create a test release on TestPyPI
4. Create a production release on PyPI

Happy deploying! 🚀

