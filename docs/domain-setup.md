# Domain Setup Guide

This guide walks through connecting your GoDaddy domain to the MangroveMarkets Cloud Run service.

> MangroveMarkets uses a single Cloud Run service named `mangrovemarkets`. The deploy workflow only targets this service and never deletes services.

## Prerequisites

- Domain registered with GoDaddy (or any DNS provider)
- MangroveMarkets deployed to Cloud Run
- GCloud CLI configured with `mangrove-markets` project

## Step 1: Deploy the App

Deployment happens automatically when you push to `main` via GitHub Actions. You can also trigger it manually from the Actions tab.

To verify the deployment:

```bash
gcloud run services describe mangrovemarkets --region=us-central1 --project=mangrove-markets
```

Note the service URL from the output (e.g., `https://mangrovemarkets-xxx-uc.a.run.app`).

## Step 2: Create Domain Mapping in GCP

Run the domain mapping command with your domain:

```bash
gcloud run domain-mappings create \
    --service=mangrovemarkets \
    --domain=YOURDOMAIN.COM \
    --region=us-central1 \
    --project=mangrove-markets
```

Replace `YOURDOMAIN.COM` with your actual domain.

GCP will output DNS records that you need to add. It will look something like this:

```
Please add the following DNS records:

  NAME               TYPE  DATA
  YOURDOMAIN.COM     A     216.239.32.21
  YOURDOMAIN.COM     A     216.239.34.21
  YOURDOMAIN.COM     A     216.239.36.21
  YOURDOMAIN.COM     A     216.239.38.21
  YOURDOMAIN.COM     AAAA  2001:4860:4802:32::15
  YOURDOMAIN.COM     AAAA  2001:4860:4802:34::15
  YOURDOMAIN.COM     AAAA  2001:4860:4802:36::15
  YOURDOMAIN.COM     AAAA  2001:4860:4802:38::15
```

**Copy these records** — you'll need them for the next step.

## Step 3: Configure DNS in GoDaddy

1. **Log in to GoDaddy** and go to your domain's DNS management page
2. **Remove any existing A or AAAA records** for the root domain (@)
3. **Add the A records** from GCP's output:
   - Type: `A`
   - Name: `@` (represents the root domain)
   - Value: Each of the four IP addresses
   - TTL: `600` (10 minutes)

4. **Add the AAAA records** (IPv6):
   - Type: `AAAA`
   - Name: `@`
   - Value: Each of the four IPv6 addresses
   - TTL: `600`

### GoDaddy-Specific Notes

- GoDaddy sometimes uses `@` for the root domain, sometimes just leave the "Host" field blank
- If GoDaddy's UI asks for "Points to", that's the IP address
- Make sure "Forwarding" is **disabled** for your domain

## Step 4: Verify Domain Ownership (If Required)

Sometimes GCP requires domain verification. If prompted:

1. Run the verification command GCP provides
2. Follow the instructions to add a TXT record to your DNS
3. Wait for propagation (can take up to 48 hours, usually much faster)

## Step 5: Wait for DNS Propagation

DNS changes can take:
- **5-10 minutes** (typical)
- **Up to 48 hours** (worst case)

Check propagation status:
```bash
# Check A records
dig YOURDOMAIN.COM A

# Check AAAA records
dig YOURDOMAIN.COM AAAA
```

Or use online tools:
- https://www.whatsmydns.net/
- https://dnschecker.org/

## Step 6: Verify HTTPS

Once DNS propagates, GCP automatically provisions an SSL certificate via Let's Encrypt. This can take **15-30 minutes**.

Check certificate status:
```bash
gcloud run domain-mappings describe \
    --domain=YOURDOMAIN.COM \
    --region=us-central1 \
    --project=mangrove-markets
```

Look for `resourceRecords` and `certificateStatus: ACTIVE`.

## Step 7: Test Your Domain

Visit your domain:
```
https://YOURDOMAIN.COM
```

You should see the MangroveMarkets landing page with a valid SSL certificate.

## Subdomain Setup (Optional)

To use a subdomain like `www.yourdomain.com` or `app.yourdomain.com`:

1. Create a domain mapping for the subdomain:
```bash
gcloud run domain-mappings create \
    --service=mangrovemarkets \
    --domain=www.YOURDOMAIN.COM \
    --region=us-central1 \
    --project=mangrove-markets
```

2. Add the DNS records provided by GCP to GoDaddy:
   - Type: `CNAME`
   - Name: `www` (or your subdomain)
   - Value: `ghs.googlehosted.com.`
   - TTL: `600`

## Troubleshooting

### "Domain not verified"
- Add the TXT verification record GCP provides
- Wait 5-10 minutes for propagation
- Retry the domain mapping command

### "DNS records not found"
- Double-check A/AAAA records in GoDaddy
- Ensure there are no conflicting records (like CNAME for @)
- Wait longer for DNS propagation

### "SSL certificate pending"
- GCP auto-provisions Let's Encrypt certificates
- Can take 15-30 minutes after DNS propagates
- Check status with `gcloud run domain-mappings describe`

### "ERR_NAME_NOT_RESOLVED"
- DNS hasn't propagated yet
- Check `dig YOURDOMAIN.COM` to see current records
- Wait and retry

## Domain Migration from Another Service

If you're migrating from another hosting provider:

1. **Lower TTL first**: Before migrating, set your DNS TTL to 300-600 seconds at your current provider
2. **Wait for old TTL to expire**: If your old TTL was 3600 (1 hour), wait 1 hour
3. **Then follow the steps above**: Add GCP's A/AAAA records
4. **Monitor traffic**: Use Cloud Run metrics to confirm traffic is reaching GCP

## Custom Domain Best Practices

- **Use the root domain** (`yourdomain.com`) for the main site
- **Redirect `www`** to the root domain (or vice versa)
- **Enable HTTPS-only**: GCP enforces this automatically
- **Monitor DNS health**: Use UptimeRobot or similar to monitor domain availability

## Reference

- [Cloud Run Custom Domains](https://cloud.google.com/run/docs/mapping-custom-domains)
- [GoDaddy DNS Management](https://www.godaddy.com/help/manage-dns-680)
- [DNS Propagation Checker](https://www.whatsmydns.net/)
