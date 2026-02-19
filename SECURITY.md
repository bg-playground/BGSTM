# Security Policy

## Supported Versions

The following versions of BGSTM currently receive security updates:

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously and appreciate responsible disclosure. Please **do not** report security vulnerabilities through public GitHub issues.

### Preferred Method: GitHub Security Advisories

1. Navigate to the [Security Advisories](https://github.com/bg-playground/BGSTM/security/advisories/new) page for this repository.
2. Click **"New draft security advisory"**.
3. Fill in the details of the vulnerability, including:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if known)
4. Submit the advisory. It will be kept private until we coordinate a fix and disclosure.

### Alternative: Email

If you prefer email, contact the maintainers at the address listed in the repository profile. Please encrypt your message if possible.

## Response Timeline

| Severity | Initial Response | Fix Timeline |
| -------- | ---------------- | ------------ |
| Critical | 24 hours         | 7 days       |
| High     | 48 hours         | 14 days      |
| Medium   | 48 hours         | 30 days      |
| Low      | 5 business days  | 90 days      |

We aim to acknowledge all reports within the timeline shown in the table above and will keep you informed of our progress throughout the investigation and resolution process.

## Disclosure Policy

- Security issues will be kept confidential until a fix is released.
- We follow a **coordinated disclosure** model: we work with reporters to agree on a disclosure timeline.
- After a fix is deployed, we will publish a security advisory crediting the reporter (unless anonymity is requested).
- We request a minimum of **90 days** before public disclosure to allow time for patching.

## Security Update Process

1. Reporter submits vulnerability via GitHub Security Advisories.
2. Maintainers triage and confirm the issue within the initial response window.
3. A private fork or branch is created to develop a fix.
4. Fix is reviewed, tested, and merged.
5. A new patch release is published and users are notified via the changelog and GitHub releases.
6. Security advisory is published and CVE is requested if applicable.

## Security Configuration Guidance

### Backend (FastAPI)

- Always run the application behind a reverse proxy (e.g., Nginx, Traefik) in production.
- Set `DEBUG=False` and configure `ALLOWED_HOSTS` in production environments.
- Use strong, randomly-generated values for `SECRET_KEY` — never commit secrets to source control.
- Enable HTTPS/TLS termination at the reverse proxy layer.
- Review and restrict CORS origins using the `CORS_ORIGINS` environment variable.
- Keep the `requirements.txt` dependencies up to date and monitor for vulnerabilities.

### Database (PostgreSQL)

- Use a dedicated database user with the minimum required privileges.
- Never use the default `postgres` superuser for the application.
- Store database credentials exclusively in environment variables (`.env` file, not in source control).
- Enable SSL connections between the application and the database in production.
- Regularly back up the database and test restoration procedures.
- Rotate database passwords periodically and whenever team members change.

### Frontend

- Keep `package.json` dependencies up to date and run `npm audit` regularly.
- Configure a strict `Content-Security-Policy` header in production.
- Avoid storing sensitive data in `localStorage` or `sessionStorage`.
- Ensure API keys or tokens used in the frontend are scoped to the minimum necessary permissions.

## Known Security Gaps

The following security features are not yet fully implemented. Contributions are welcome:

| Gap                 | Description                                                          |
| ------------------- | -------------------------------------------------------------------- |
| Authentication      | Endpoint authentication is partial; some routes may be unauthenticated |
| Rate Limiting       | No rate limiting is currently applied to API endpoints               |
| Input Validation    | Some input fields may lack thorough server-side validation           |
| Audit Logging       | No structured audit log exists for sensitive operations              |

## Security Best Practices for Users

- **Never commit secrets**: Use `.env` files (already in `.gitignore`) and environment variable management tools.
- **Use Docker Secrets or a secrets manager** (e.g., HashiCorp Vault, AWS Secrets Manager) for production deployments.
- **Keep dependencies updated**: Run `pip install --upgrade` and `npm update` regularly and review Dependabot PRs promptly.
- **Review access controls**: Limit who has write access to the repository and rotate access tokens regularly.
- **Enable two-factor authentication (2FA)** on all GitHub accounts with repository access.
- **Monitor GitHub Security Advisories** for dependencies used in this project.

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security/getting-started/github-security-features)
- [SQLAlchemy Security Considerations](https://docs.sqlalchemy.org/en/20/core/connections.html#dbapi-connections)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
