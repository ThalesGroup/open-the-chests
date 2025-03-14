## Goods practices to follow

:warning:**You must never store credentials information into source code or config file in a GitHub repository**
- Block sensitive data being pushed to GitHub by git-secrets or its likes as a git pre-commit hook
- Audit for slipped secrets with dedicated tools
- Use environment variables for secrets in CI/CD (e.g. GitHub Secrets) and secret managers in production

# Security Policy

## Supported Versions

There is no concurrente version of the project. That means that the safest version is the last release. 
Therefore, users are invited to update to the latest package available.

## Reporting a Vulnerability

If you find a potential vulnerability, please open a dedicated issue.


