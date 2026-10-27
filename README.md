# CFB Analytics & Prediction Pipeline

An end-to-end, $0-to-run data/ML/AI project built on public college football data.
Designed as a portfolio piece: ingestion -> warehouse -> dbt transforms -> ML model ->
LLM insight layer -> public dashboard, all orchestrated with GitHub Actions.

## Architecture

```
CFBD API  -->  ingestion/ (Python)  -->  Warehouse (BigQuery sandbox or Snowflake)
                                               |
                                               v
                                        dbt_project/ (staging -> intermediate -> marts)
                                               |
                                               v
                                   ml/ (feature build + train + predict)
                                               |
                                               v
                           llm/ (RAG: embeddings + hosted free LLM for game blurbs)
                                               |
                                               v
                              app/streamlit_app.py  -->  Streamlit Community Cloud
                                                           or HF Spaces (public demo)

Orchestration: .github/workflows/*.yml (scheduled, free on public repos)
```

## Why this stack (all free)

| Layer | Tool | Free tier |
|---|---|---|
| Source data | [CFBD API](https://collegefootballdata.com) | 1,000 calls/month free |
| Warehouse | BigQuery Sandbox (default) or Snowflake trial | BigQuery: 10GB storage + 1TB query/mo, no card, lifetime |
| Transform | dbt Core | Open source, free forever |
| Orchestration | GitHub Actions | Unlimited on public repos |
| ML | scikit-learn / XGBoost | Free, local |
| LLM insights | sentence-transformers (local embeddings) + Groq or Gemini free API | Free, rate-limited |
| Hosting | Streamlit Community Cloud or HF Spaces (CPU Basic) | Free, sleeps when idle |

Swap warehouse by setting `WAREHOUSE=bigquery` or `WAREHOUSE=snowflake` in `.env`.

## Setup

1. `python -m venv .venv && source .venv/bin/activate`
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in:
   - `CFBD_API_KEY` (free key from collegefootballdata.com)
   - Warehouse creds (BigQuery service account JSON path, or Snowflake account/user/password)
   - `LLM_API_KEY` (Groq or Gemini free API key) — optional, only needed for the insight layer
4. Backfill historical data: `python ingestion/pull_games.py --start-year 2015`
5. `cd dbt_project && dbt run && dbt test`
6. Train the model: `python ml/train_model.py`
7. Run the app locally: `streamlit run app/streamlit_app.py`
8. Push to a **public** GitHub repo, then enable the workflows in `.github/workflows/` (set the same secrets in repo Settings -> Secrets).
9. Deploy `app/streamlit_app.py` on Streamlit Community Cloud (or build the HF Spaces equivalent) pointing at your repo.

## Resume-relevant pieces this project demonstrates

- Python ETL against a REST API with pagination/rate-limit handling
- Cloud data warehouse modeling (BigQuery or Snowflake)
- dbt: staging/intermediate/marts layering, source freshness tests, docs
- CI/CD-style orchestration via GitHub Actions (scheduled jobs, secrets management)
- ML model development + evaluation (scikit-learn/XGBoost)
- Basic LLM/RAG integration (embeddings + retrieval + generation)
- Public cloud deployment of a data product

## Status / next steps

This scaffold ships with working structure and stub logic — see `TODO` markers in each
file. The next milestones are: finish the CFBD pull scripts, flesh out dbt marts,
pick a target variable (straight-up winner vs. point spread), and wire up the
Streamlit app to read from the warehouse.
