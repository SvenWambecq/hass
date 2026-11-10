# Security Configuration

This document describes the security setup for the Home Assistant Raspberry Pi instance.

## Overview

Your Home Assistant instance is exposed externally via `sveneniris.duckdns.org` and implements multi-layered security:

```
┌─────────────────────────────────────────────────────────────┐
│ Internet (Untrusted)                                        │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTPS (443)
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Proximus Modem (TLS Termination)                            │
│ - Terminates HTTPS                                          │
│ - Acts as firewall                                          │
│ - Port 443 open only                                        │
└───────────────────────┬─────────────────────────────────────┘
                        │ Internal network (HTTP)
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Nginx Reverse Proxy (RPi)                                   │
│ - Listens on port 443 (HTTPS)                               │
│ - Redirects port 80 → HTTPS                                 │
│ - Validates Let's Encrypt certificate                       │
│ - Enforces security headers                                 │
└───────────────────────┬─────────────────────────────────────┘
                        │ Localhost HTTP (127.0.0.1:8123)
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ Home Assistant Core (8123)                                  │
│ - Handles actual requests                                   │
│ - Protected by MFA                                          │
└─────────────────────────────────────────────────────────────┘
```

## Security Measures in Place

### 1. HTTPS/TLS Encryption ✅

**Status:** Enabled with Let's Encrypt certificate

- **Certificate Location:** `/etc/letsencrypt/live/sveneniris.duckdns.org/`
- **TLS Version:** TLS 1.2+ (no SSLv3, TLSv1.0, or TLSv1.1)
- **Ciphers:** Strong EECDH and AESGCM suites only
- **Certificate Authority:** Let's Encrypt (free, auto-renewable)

**What it protects:**
- ✅ Encryption of all traffic between internet and modem
- ✅ Encryption of all traffic between modem and RPi
- ✅ End-to-end encryption for authentication tokens and commands

### 2. HTTP → HTTPS Redirection ✅

**Status:** Enforced

Any request to `http://sveneniris.duckdns.org` is automatically redirected to `https://`.

```nginx
server {
    listen [::]:80 default_server ipv6only=off;
    return 301 https://$host$request_uri;
}
```

**What it protects:** Prevents accidental cleartext access even if HTTP is accidentally used.

### 3. HSTS (HTTP Strict-Transport-Security) ✅

**Status:** Enabled for 1 year

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubdomains";
```

**What it protects:** Browsers remember to only use HTTPS for the next 12 months, preventing protocol downgrade attacks.

### 4. Reverse Proxy Hardening ✅

**Status:** Partially configured

Nginx forwards requests to Home Assistant on `127.0.0.1:8123` with proper headers:

```nginx
location / {
    proxy_pass http://127.0.0.1:8123;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_redirect http:// https://;
}
```

**What it protects:**
- ✅ Client IP logging
- ✅ Protocol awareness in backend
- ✅ Host header validation
- ⚠️ Missing: Additional security headers (CSP, X-Frame-Options, etc.)

### 5. Multi-Factor Authentication (MFA) ✅

**Status:** Configured on Home Assistant

See: [Home Assistant MFA Settings](https://www.home-assistant.io/docs/authentication/#multi-factor-authentication)

**What it protects:** Even if password is compromised, attackers cannot access HA without a second factor.

### 6. Firewall/Network Access ✅

**Status:** Modem firewall enabled

- Only ports 443 (HTTPS) and 80 (redirect) are accessible externally
- Port 8123 (Home Assistant) is NOT exposed to the internet
- Internal network separation between modem and RPi

**What it protects:** Limits attack surface to just the nginx reverse proxy.

## Security Gaps

### ⚠️ Missing Security Headers

The following headers would improve security but are not currently configured:

```nginx
# Prevent clickjacking attacks
add_header X-Frame-Options "SAMEORIGIN";

# Prevent MIME type sniffing
add_header X-Content-Type-Options "nosniff";

# XSS protection (browser-level)
add_header X-XSS-Protection "1; mode=block";

# Content Security Policy (restrict script sources)
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval';";

# Referrer policy
add_header Referrer-Policy "no-referrer-when-downgrade";
```

**Impact:** Low - mainly protects against browser-based attacks. HA API clients may not enforce these.

### ❌ No Rate Limiting

Currently, there is no rate limiting configured on the nginx reverse proxy.

**Risk:** Vulnerable to brute-force login attempts if someone discovers valid usernames.

**Recommended fix:**
```nginx
limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
limit_req zone=general burst=20 nodelay;
```

**Impact:** Medium - reduces brute-force risk.

### ⚠️ TLS 1.2 Minimum (not 1.3 only)

The configuration supports TLS 1.2, which is acceptable but not bleeding-edge.

**Note:** TLS 1.2 is still considered secure and necessary for broader device compatibility.

## Certificate Management

### Checking Certificate Validity

```bash
ssl-cert-check -b -c /etc/letsencrypt/live/sveneniris.duckdns.org/cert.pem
```

### Manual Certificate Renewal

Certificates auto-renew via Let's Encrypt, but manual renewal if needed:

```bash
sudo systemctl stop nginx
sudo certbot renew --cert-name sveneniris.duckdns.org --preferred-challenges http-01
sudo systemctl start nginx
```

### Certificate Auto-Renewal

Let's Encrypt certificates expire after 90 days. Certbot automatically renews them before expiration via:

- **Systemd timer:** `certbot.timer` (usually enabled)
- **Renewal check:** Daily via cron or systemd

Verify auto-renewal is working:

```bash
sudo systemctl status certbot.timer
sudo certbot renew --dry-run
```

## Configuration Files

| File | Purpose |
|------|---------|
| `/etc/nginx/sites-available/hass` | Nginx configuration (reverse proxy + HTTPS) |
| `/etc/letsencrypt/live/sveneniris.duckdns.org/` | SSL certificate and private key |
| `/etc/nginx/ssl/dhparams.pem` | Diffie-Hellman parameters (TLS security) |

## Nginx Configuration

The main nginx configuration is located at:

```
/etc/nginx/sites-available/hass
```

It's enabled via symlink:

```bash
sudo ln -s /etc/nginx/sites-available/hass /etc/nginx/sites-enabled/hass
```

### Reloading Configuration

After making changes to nginx config:

```bash
sudo nginx -t                    # Test configuration syntax
sudo systemctl reload nginx      # Reload without dropping connections
```

## Best Practices

### ✅ Do:

- Keep Home Assistant and OS packages updated
- Monitor certificate expiration (set calendar reminder for 80+ days after installation)
- Review nginx logs regularly: `tail -f /var/log/nginx/access.log`
- Use MFA for all user accounts
- Change default passwords and API tokens
- Periodically rotate authentication credentials

### ❌ Don't:

- Disable HTTPS or use self-signed certificates for external access
- Expose port 8123 directly to the internet
- Commit API tokens or secrets to git
- Use weak passwords for HA accounts
- Open unnecessary ports on the modem firewall

## Incident Response

### If you suspect compromise:

1. **Change all Home Assistant user passwords immediately**
2. **Revoke all API tokens** (Home Assistant > Developer Tools > Applications)
3. **Review nginx access logs** for suspicious activity:
   ```bash
   grep "401\|403" /var/log/nginx/access.log
   grep -E "curl|wget|nmap" /var/log/nginx/access.log
   ```
4. **Check for unauthorized automations/scripts** in Home Assistant
5. **Rotate DuckDNS token** (if needed)
6. **Force certificate renewal** and regenerate dhparams

## Future Improvements

### High Priority:
- [ ] Add security headers (CSP, X-Frame-Options, etc.)
- [ ] Implement rate limiting on nginx
- [ ] Set up log monitoring/alerting

### Medium Priority:
- [ ] Enforce TLS 1.3 only (when broader compatibility not needed)
- [ ] Add ModSecurity WAF rules
- [ ] Implement request size limits
- [ ] Enable nginx security module features

### Low Priority:
- [ ] OCSP stapling for certificate validation
- [ ] Perfect Forward Secrecy tuning
- [ ] Custom error pages

## References

- [Home Assistant Security](https://www.home-assistant.io/docs/authentication/)
- [Let's Encrypt Best Practices](https://letsencrypt.org/docs/)
- [Nginx Security](https://nginx.org/en/docs/http/ngx_http_ssl_module.html)
- [OWASP Security Headers](https://owasp.org/www-project-secure-headers/)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)

## Questions?

For security-related questions or vulnerabilities, refer to:
- Home Assistant documentation: https://www.home-assistant.io/
- Let's Encrypt support: https://letsencrypt.org/docs/
- Nginx documentation: https://nginx.org/en/docs/

---

**Last Updated:** 2026-11-10  
**Reviewed by:** Security analysis
