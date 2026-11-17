# Aegis AI Policy Q&A

A work-in-progress retrieval-augmented Q&A demo for professional firms. Ask about a fictional Northwoods Professional Services AI policy and handbook or short public NIST AI RMF excerpts. The app retrieves relevant passages, generates a response, and shows the supporting quotations and document sections. Northwoods is fictional; this demo is not legal advice.

**Status:** Initial implementation. A recorded walkthrough and live deployment are planned; neither is available yet.

## Run locally

Python 3.11 is recommended. This demo requires an OpenAI API key with API access and incurs usage charges. An OpenAI subscription does not necessarily include API credits.

```bash
git clone https://github.com/dblomqu1-8980/aegis-policy-qa.git
cd aegis-policy-qa
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # Windows: copy .env.example .env
# Edit .env locally and add OPENAI_API_KEY. Never commit it.
python src/ingest.py
streamlit run src/app.py
```

Re-run ingestion when the documents or embedding model change. `.chroma` and `.env` stay local and are excluded from git. The distance threshold in `.env.example` is an initial setting, not a calibrated guarantee.

## How it works

Markdown sections → OpenAI embeddings → local Chroma index → similarity search → model response → citation validation → answer and quoted passages. The response is withheld if retrieval returns no sufficiently close passages, the model declines, or its citations are missing or invalid. Exact-quote validation does **not** prove that the answer follows from those quotes; human review and real evaluations remain necessary.

## Governance notes

- **Data:** Only fictional and public materials belong in this demo. Questions and retrieved passages are sent to OpenAI for embeddings and generation. Do not enter sensitive or client information. The app does not intentionally save question history, but provider and hosting retention policies apply.
- **Controls:** The prompt restricts answers to retrieved content, asks for refusal when evidence is missing, and treats retrieved text as data. A similarity threshold and quote validation provide additional checks. These safeguards are imperfect; prompt injection and unsupported interpretations remain possible.
- **Oversight:** A person maintains the documents, approves policy, reviews outputs, and handles exceptions. The assistant cannot change policy. This sample does not provide authentication, durable abuse prevention, incident monitoring, or production access controls. Hosted demo request limits are described below.
- **Evaluation:** `python -m pytest` runs offline logic checks. The 12-question evaluation set in `evals/questions.yaml` is for future end-to-end evaluation with an API key; it has not been claimed as passing. Check citations, substance, and refusals manually before any public deployment.

See [data/README.md](data/README.md) for source details. No client integrations or live Aegis website changes are included. Contact: https://aegisaiadvisory.com.

## Hosted demo setup

See [deployment instructions](docs/DEPLOY.md) for the exact repository settings and private secrets setup. The app now indexes the sample corpus automatically on the first question and uses per-session and shared daily request limits. These limits apply to one hosting instance and are not a guaranteed dollar cap; see the documented limitations before promoting a public URL.
