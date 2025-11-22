# Contributing Guide

## Welcome!

Thank you for your interest in contributing to the Data Analytics Pipeline project! This guide will help you get started.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Testing Requirements](#testing-requirements)
6. [Documentation](#documentation)
7. [Pull Request Process](#pull-request-process)
8. [Release Process](#release-process)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors.

### Our Standards

**Positive behaviors**:
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behaviors**:
- Harassment or discriminatory language
- Trolling, insulting/derogatory comments
- Public or private harassment
- Publishing others' private information
- Other conduct which could reasonably be considered inappropriate

### Enforcement

Violations of the Code of Conduct may be reported to the project maintainers at conduct@example.com.

---

## Getting Started

### Prerequisites

- Python 3.11+
- AWS CLI configured
- Terraform 1.5.0+
- Git 2.x+
- GitHub account

### Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/dataanalytics-project.git
cd dataanalytics-project

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/dataanalytics-project.git
```

### Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Verify Setup

```bash
# Run tests
pytest tests/unit/ -v

# Run linters
black --check src/
flake8 src/
pylint src/

# Verify Terraform
cd terraform/environments/dev
terraform init -backend=false
terraform validate
```

---

## Development Workflow

### 1. Create a Branch

```bash
# Update your fork
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-number-description
```

### Branch Naming Convention

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions/updates
- `chore/` - Maintenance tasks

### 2. Make Changes

```bash
# Make your changes
# Write tests
# Update documentation

# Run tests frequently
pytest tests/unit/ -v

# Format code
black src/ tests/
isort src/ tests/
```

### 3. Commit Changes

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Format: <type>(<scope>): <subject>

git commit -m "feat(ingestion): add CSV validation for product data"
git commit -m "fix(etl): handle null values in transaction amount"
git commit -m "docs(api): update S3Helper method signatures"
git commit -m "test(utils): add tests for AthenaHelper"
```

**Commit Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements

### 4. Push Changes

```bash
# Push to your fork
git push origin feature/your-feature-name
```

### 5. Create Pull Request

1. Go to GitHub and create a Pull Request
2. Fill out the PR template
3. Link related issues
4. Request reviews from maintainers

---

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

**Line Length**: 100 characters (not 79)

**Imports**:
```python
# Standard library
import os
import sys
from datetime import datetime

# Third-party
import boto3
import pandas as pd

# Local
from src.utils.s3_helper import S3Helper
```

**Docstrings**: Use Google style
```python
def upload_file(file_path: str, bucket: str, key: str) -> bool:
    """
    Upload a file to S3.
    
    Args:
        file_path: Local file path to upload
        bucket: S3 bucket name
        key: S3 object key
        
    Returns:
        True if successful, False otherwise
        
    Raises:
        ClientError: If AWS API call fails
        
    Example:
        >>> s3 = S3Helper()
        >>> s3.upload_file('/tmp/data.csv', 'my-bucket', 'data.csv')
        True
    """
    # Implementation
```

**Type Hints**: Always use type hints
```python
from typing import List, Dict, Optional

def process_records(records: List[Dict], limit: Optional[int] = None) -> List[Dict]:
    """Process records with optional limit."""
    # Implementation
```

**Error Handling**: Be explicit
```python
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise
```

### Terraform Style Guide

**Naming**: Use lowercase with hyphens
```hcl
resource "aws_s3_bucket" "data-lake" {
  bucket = "${var.project_name}-data-lake-${var.environment}"
}
```

**Variables**: Always include description
```hcl
variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}
```

**Outputs**: Document what they're for
```hcl
output "data_lake_bucket_name" {
  description = "Name of the data lake S3 bucket"
  value       = aws_s3_bucket.data-lake.id
}
```

### SQL Style Guide

**Keywords**: UPPERCASE
```sql
SELECT 
    customer_id,
    SUM(total_amount) AS total_revenue
FROM curated.transactions
WHERE status = 'completed'
GROUP BY customer_id
ORDER BY total_revenue DESC
LIMIT 10;
```

**Indentation**: 4 spaces
**Line breaks**: After major clauses

---

## Testing Requirements

### Unit Tests

**Coverage**: Minimum 70% for new code

**Location**: `tests/unit/test_<module_name>.py`

**Example**:
```python
import pytest
from src.utils.s3_helper import S3Helper

@pytest.mark.unit
class TestS3Helper:
    """Test S3Helper class."""
    
    def test_upload_file(self, s3_client):
        """Test file upload to S3."""
        # Arrange
        helper = S3Helper()
        
        # Act
        result = helper.upload_file('/tmp/test.txt', 'bucket', 'key')
        
        # Assert
        assert result is True
```

### Integration Tests

**Location**: `tests/integration/test_<workflow_name>.py`

**Requirements**:
- Use LocalStack for AWS services
- Clean up resources after tests
- Test end-to-end workflows

### Running Tests

```bash
# Unit tests only
pytest tests/unit/ -v

# With coverage
pytest tests/unit/ --cov=src --cov-report=term-missing

# Specific test file
pytest tests/unit/test_s3_helper.py -v

# Specific test
pytest tests/unit/test_s3_helper.py::TestS3Helper::test_upload_file -v
```

### Test Requirements for PRs

- [ ] All existing tests pass
- [ ] New code has >70% coverage
- [ ] Integration tests added for new features
- [ ] Edge cases tested
- [ ] Error handling tested

---

## Documentation

### Code Documentation

**Every module** must have:
- Module docstring
- Class docstrings
- Method/function docstrings with parameters and return values
- Type hints

**Example**:
```python
"""
S3 helper utilities for data pipeline operations.

This module provides a helper class for common S3 operations including
upload, download, list, and delete operations.
"""

class S3Helper:
    """
    Helper class for Amazon S3 operations.
    
    Attributes:
        s3_client: Boto3 S3 client
        s3_resource: Boto3 S3 resource
    """
    
    def __init__(self, region_name: str = 'us-east-1'):
        """
        Initialize S3 client.
        
        Args:
            region_name: AWS region name. Defaults to 'us-east-1'.
        """
        # Implementation
```

### User Documentation

Update relevant docs in `docs/`:
- `README.md` - Project overview
- `ARCHITECTURE.md` - Architecture changes
- `API_REFERENCE.md` - API changes
- `DEPLOYMENT.md` - Deployment changes
- `OPERATIONS.md` - Operational changes

### Changelog

Update `CHANGELOG.md` with your changes:

```markdown
## [Unreleased]

### Added
- New feature X that does Y

### Changed
- Improved performance of Z by 50%

### Fixed
- Bug in component A that caused B
```

---

## Pull Request Process

### PR Checklist

Before submitting:

- [ ] Code follows style guidelines
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No merge conflicts
- [ ] CI/CD pipeline passing
- [ ] Self-reviewed code

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Fixes #123

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Screenshots (if applicable)

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests passing
```

### Review Process

1. **Automated Checks**: CI/CD must pass
2. **Code Review**: At least 1 approval required
3. **Testing**: Reviewer verifies tests
4. **Documentation**: Reviewer checks docs
5. **Approval**: Maintainer approves
6. **Merge**: Squash and merge to main

### Review Timeline

- Initial review: Within 2 business days
- Follow-up reviews: Within 1 business day
- Merge: After approval and CI passing

---

## Release Process

### Versioning

We use [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Steps

1. **Update Version**
```bash
# Update version in setup.py, __init__.py, etc.
git commit -m "chore: bump version to 1.2.0"
```

2. **Update Changelog**
```bash
# Move [Unreleased] to [1.2.0] - 2025-01-15
git commit -m "docs: update changelog for v1.2.0"
```

3. **Create Tag**
```bash
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin v1.2.0
```

4. **GitHub Release**
- Create release on GitHub
- Add release notes from CHANGELOG
- Attach any artifacts

5. **Deploy**
```bash
# Deploy to staging
./scripts/deploy.sh staging v1.2.0

# Verify staging
./scripts/verify.sh staging

# Deploy to production
./scripts/deploy.sh prod v1.2.0
```

---

## Getting Help

### Resources

- **Documentation**: `docs/` directory
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Slack**: #data-pipeline channel

### Questions?

- Check existing issues and discussions
- Review documentation
- Ask in Slack channel
- Create a new discussion

### Reporting Bugs

Use the bug report template:

```markdown
**Describe the bug**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen

**Screenshots**
If applicable

**Environment**
- OS: [e.g. Ubuntu 20.04]
- Python version: [e.g. 3.11]
- AWS region: [e.g. us-east-1]

**Additional context**
Any other context
```

---

## Recognition

Contributors will be recognized in:
- `CONTRIBUTORS.md` file
- Release notes
- Project README

Thank you for contributing! 🎉

---

**Last Updated**: 2025-11-22  
**Version**: 1.0  
**Maintained By**: Data Engineering Team
