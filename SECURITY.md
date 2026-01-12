# Security Policy

## Reporting Security Vulnerabilities

We take security seriously. If you discover a security vulnerability in Voxelle, please report it responsibly.

### Do Not

- ❌ Post exploit code or full vulnerability details in public forums if it exposes users
- ❌ Exploit the vulnerability

> Note: For low-severity or non-sensitive security issues, opening a public GitHub issue is acceptable (see guidance below). For anything that could enable attackers or expose sensitive data, please follow the private reporting guidance.

### Do

- ✅ Open a GitHub issue or contact the maintainer directly
- ✅ Include steps to reproduce (if possible)
- ✅ For non-sensitive issues, mark it clearly as `security` in the title or labels
- ✅ Allow time for us to investigate and release fixes
- ✅ Use PGP encryption if possible when sending sensitive information by email

### What to Include

```
Subject: SECURITY: [Vulnerability Type]

Details:
- Description of vulnerability
- Affected version(s)
- Steps to reproduce
- Potential impact
- Suggested fix (if you have one)

Contact:
- Your name/handle
- Email for follow-up
```

---

## Reporting Options & Expected Response Time

We support two reporting paths depending on severity and sensitivity:

- **Private (recommended for critical issues):** Contact @tulovec96 on [Discord](https://discord.gg/Z8yyEzHsYM) or via GitHub issue. Use PGP if possible. This helps prevent public exposure while we investigate and prepare a patch.
- **Public (acceptable for low-severity/non-sensitive issues):** Open a GitHub issue. Please avoid posting sensitive reproducer details publicly; instead include high-level info and ask maintainers to follow up for private details.

We aim to acknowledge reports within 24–72 hours on business days. Responses may be delayed over weekends, public holidays, or during maintainer vacations — please allow extra time in those cases.

## Security Process

1. **Receipt** - You'll receive acknowledgment (via GitHub issue comment or email) typically within 24–72 hours on business days
2. **Investigation** - We investigate and reproduce the issue
3. **Fix** - We develop and test a fix
4. **Release** - We release a patched version
5. **Disclosure** - We publish security advisory
6. **Credit** - You'll be credited (unless you prefer anonymity)

---

## Supported Versions

We provide security updates for:

| Version | Status | Security Updates |
|---------|--------|------------------|
| 2.0.x | Current | ✅ Yes |
| 1.5.x | Legacy | ⚠️ Critical only |
| 1.0.x | Old | ❌ No |

---

## Security Best Practices

### For Users

1. **Keep Updated**
   ```bash
   pip install --upgrade voxelle
   ```

2. **Use Environment Variables**
   - Store API keys in `.env`
   - Never commit `.env` to git
   - Use different keys for dev/prod

3. **Secure Discord Bot**
   - Regenerate token after leak
   - Restrict permissions
   - Use private guilds for testing

4. **Monitor Dependencies**
   - Check for updates regularly
   - Run `pip list --outdated`
   - Use `pip audit` to check for vulnerabilities

5. **Network Security**
   - Use HTTPS in production
   - Firewall sensitive endpoints
   - Use VPN for remote access

### For Developers

1. **Input Validation**
   ```python
   # Good: Validate user input
   if not isinstance(message, str):
       raise ValueError("Message must be string")
   
   # Bad: Trust user input
   eval(user_input)  # Never do this!
   ```

2. **No Hardcoded Secrets**
   ```python
   # Good
   api_key = os.getenv("API_KEY")
   
   # Bad
   api_key = "sk-1234567890abcdef"
   ```

3. **SQL Injection Prevention**
   ```python
   # Good: Use parameterized queries
   cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
   
   # Bad: String concatenation
   cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
   ```

4. **Dependency Security**
   ```bash
   # Check for vulnerabilities
   pip install pip-audit
   pip-audit
   
   # Keep dependencies updated
   pip install --upgrade-all
   ```

5. **Error Handling**
   ```python
   # Good: Don't expose sensitive info
   except Exception as e:
       logger.error(f"Database error: {e}")
       return {"error": "Database error"}
   
   # Bad: Expose stack trace to user
   raise Exception(str(e))
   ```

---

## Common Vulnerabilities

### SQL Injection
Use parameterized queries, never concatenate user input into SQL.

### Command Injection
Never use shell=True with user input. Use subprocess.run with list args.

### Path Traversal
Validate file paths. Use `pathlib.Path.resolve()` to check paths.

### XXE Attacks
Disable XML external entities in XML parsers.

### SSRF (Server-Side Request Forgery)
Validate URLs. Restrict to expected hosts and protocols.

### Dependency Vulnerabilities
Keep dependencies updated. Use `pip audit`.

---

## Security Headers

For web endpoints, include:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---

## Encryption

### Sensitive Data
- Use HTTPS in production
- Hash passwords with bcrypt/argon2
- Encrypt sensitive config files
- Use secure random for tokens

### Example
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password
hashed = pwd_context.hash("password")

# Verify password
if pwd_context.verify("password", hashed):
    print("Match!")
```

---

## Authentication

### Discord Bot Token
- Never share your token
- Regenerate if compromised
- Use OAuth2 for user auth

### API Keys
- Store in environment variables
- Rotate regularly
- Use API key scopes
- Monitor for abuse

### Example
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(credentials = Depends(security)):
    if credentials.credentials != os.getenv("API_KEY"):
        raise HTTPException(status_code=403)
    return credentials
```

---

## Audit Logging

Log security-relevant events:

```python
import logging

security_logger = logging.getLogger("security")

# Log authentication attempts
security_logger.info(f"Failed login attempt from {ip}")

# Log privilege changes
security_logger.warning(f"User {user} elevated to admin")

# Log data access
security_logger.info(f"User {user} accessed {resource}")
```

---

## Contact

- **Email**: security@jaison.dev (preferred for critical vulnerabilities)
- **GitHub Issues**: Open an issue for non-sensitive findings — use `security:` prefix in the title or request that maintainers convert it to a private disclosure if needed
- **Discord**: (do not post details publicly) contact maintainers in the private security channel or DM: [Discord Server](https://discord.gg/Z8yyEzHsYM)
- **PGP**: Available upon request (reply to `security@jaison.dev` for the key)

---

<p align="center">
  <strong>Thank you for helping keep Voxelle secure! 🔒</strong>
</p>
