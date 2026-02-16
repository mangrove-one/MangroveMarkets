# MangroveMarkets Status Report

## Current State

- **Dev infrastructure provisioned** in GCP project `mangrove-markets` (Artifact Registry, Cloud Run service, service accounts, Secret Manager secret).
- **Cloud SQL (Postgres 16)** instance `mangrovemarkets-dev` created and DB `mangrove_dev` provisioned.
- **App image built and pushed** to Artifact Registry (`mangrovemarkets:latest`).
- **Cloud Run service deployed**: `mangrovemarkets-dev` (us-central1).
- **Public access enabled** (`allUsers` invoker set).
- **Domain mapping pending** because `mangrovemarkets.com` is not yet verified in Google Search Console for this account.

## Current Service URL (Dev)
- https://mangrovemarkets-dev-483282138591.us-central1.run.app

## Blockers
- Org policy prevents public `allUsers` invoker on Cloud Run.
- DNS mapping for `mangrovemarkets.com` pending until public access is allowed.
