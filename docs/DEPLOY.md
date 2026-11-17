# Deploy the separate Policy Q&A demo

The source is ready for Streamlit Community Cloud. Account access and adding a private API key are still required. The app is not hosted simply because these files exist on GitHub.

## Deployment settings

| Setting | Value |
|---|---|
| Repository | `dblomqu1-8980/aegis-policy-qa` |
| Branch | `main` |
| Main file path | `src/app.py` |
| Python version | `3.12` |
| Suggested subdomain | `aegis-policy-qa` (subject to availability) |

Open https://share.streamlit.io and create an app from this repository. In Advanced settings, choose Python 3.12 and add the following in the **private Secrets field**. Replace the placeholder directly in Streamlit, never in GitHub or chat:

```toml
OPENAI_API_KEY = "REPLACE_IN_STREAMLIT_ONLY"
OPENAI_MODEL = "gpt-4o-mini"
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
DAILY_REQUEST_LIMIT = "100"
SESSION_REQUEST_LIMIT = "20"
REQUEST_COOLDOWN_SECONDS = "10"
```

Root-level Streamlit secrets are exposed as environment variables. Local development can continue using the ignored `.env` file. The first submitted question builds the index; later questions reuse it. A changed corpus or embedding model triggers reindexing.

## Cost controls and their limits

Questions are limited to 1,000 characters and generated answers to 600 tokens. API requests use a 30-second timeout and no automatic retries. A SQLite counter reserves a request before paid work, shared across visitors on the same server. It allows 100 question attempts per UTC day by default, with 20 per browser session and a 10-second session cooldown. No question or response text is stored in that counter.

These are demo controls, not a guaranteed dollar spending cap. Session limits can be bypassed by opening another session. The shared daily counter resets if the host discards local files; separate replicas would each have their own counter. Indexing, failed API work, and direct CLI tests may incur costs. Use a dedicated API project, monitor actual spend, and stop/revoke the key if needed. Before heavy public promotion, use durable centralized quotas and stronger abuse protection.

## Verify before adding a website link

1. Submit a policy question. Confirm the answer and source cards.
2. Ask about the holiday schedule and confirm refusal.
3. Check the layout on a phone and desktop.
4. Verify repeated submissions show the cooldown warning.
5. Open the live URL while signed out. Confirm the intended audience can access it.
6. Record the actual working URL; then add the Aegis demo page and homepage card.

Do not commit `.env`, `*.env`, or `.streamlit/secrets.toml`. If a key was previously committed, revoke it even after the file is deleted.

Official deployment guide: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
