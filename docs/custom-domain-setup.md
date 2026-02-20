# Custom Domain Setup Guide

This guide explains how to point your Ionos domain to the BGSTM documentation site hosted on GitHub Pages.

## Prerequisites

- GitHub Pages is enabled for this repository
- You have access to your Ionos domain DNS settings

## Steps

### 1. Configure GitHub Pages Custom Domain

1. Go to repository Settings → Pages
2. Under "Custom domain", enter your domain (e.g., `docs.yourdomain.com`)
3. Click "Save"
4. Wait for DNS check to complete

### 2. Configure Ionos DNS Settings

Log in to your Ionos account and add the following DNS records:

#### Option A: Subdomain (Recommended)
If using a subdomain like `docs.yourdomain.com`:

```
Type: CNAME
Host: docs
Points to: bg-playground.github.io
TTL: 3600
```

#### Option B: Apex Domain
If using the root domain `yourdomain.com`:

```
Type: A
Host: @
Points to: 185.199.108.153
TTL: 3600

Type: A
Host: @
Points to: 185.199.109.153
TTL: 3600

Type: A
Host: @
Points to: 185.199.110.153
TTL: 3600

Type: A
Host: @
Points to: 185.199.111.153
TTL: 3600
```

### 3. Wait for DNS Propagation

DNS changes can take 24-48 hours to fully propagate, but often complete within a few hours.

Check propagation status: https://www.whatsmydns.net/

### 4. Enable HTTPS

Once DNS is configured:

1. Return to GitHub Pages settings
2. Check "Enforce HTTPS" (may take a few minutes to become available)

## Verification

Your site should be accessible at:
- `https://docs.yourdomain.com` (or your chosen domain)
- `https://bg-playground.github.io/BGSTM` (GitHub Pages default)

## Troubleshooting

**DNS not resolving:**
- Wait longer (up to 48 hours)
- Clear your DNS cache: `ipconfig /flushdns` (Windows) or `sudo dscacheutil -flushcache` (Mac)
- Verify records in Ionos dashboard

**HTTPS not available:**
- Wait 10-15 minutes after DNS propagation
- Disable and re-enable custom domain in GitHub settings

**404 errors:**
- Verify GitHub Actions deployment succeeded
- Check that `gh-pages` branch exists and has content

## Support

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Ionos DNS Help](https://www.ionos.com/help/domains/)
