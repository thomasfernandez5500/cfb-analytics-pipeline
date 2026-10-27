# Architecture notes

## Data flow

1. `ingestion/*.py` pulls from the CFBD API and lands raw tables in the
   warehouse (`raw_games`, `raw_team_game_stats`, `raw_recruiting_rankings`,
   `raw_betting_lines`, `raw_advanced_stats`).
2. `dbt_project/models/staging/*` cleans/types those raw tables 1:1.
3. `dbt_project/models/intermediate/*` reshapes to one-row-per-team-per-game
   so features are easy to join.
4. `dbt_project/models/marts/fct_games.sql` is the final training table.
5. `ml/train_model.py` reads `fct_games`, trains XGBoost, saves `model.joblib`.
6. `llm/` provides a RAG insight layer: local embeddings for retrieval,
   a free hosted LLM (Groq/Gemini) for generation.
7. `app/streamlit_app.py` ties prediction + insight together for a public demo.

## Why this order matters for the resume story

Each stage maps to a distinct, nameable skill: Python ETL -> cloud warehouse
modeling -> dbt transformation (testing + docs) -> ML -> LLM/RAG -> deployment.
Keep commits granular by stage so the GitHub history itself tells that story.

## Known gaps in this scaffold (intentional -- fill in as you build)

- Only a handful of raw CFBD endpoints are wired up; recruiting and advanced
  stats aren't joined into `int_team_game_features` yet.
- `ml/features.py` only uses spread/over_under/week as features -- the real
  value-add is adding recruiting gap, advanced stats deltas, recent-form
  rolling averages, etc.
- The retrain workflow uploads the model as a GitHub Actions artifact but
  doesn't yet wire it into the deployed app automatically -- decide on a
  hand-off (commit back to repo vs. cloud storage) once the app is live.
- `llm/generate_insight.py` model names (`llama-3.1-8b-instant`,
  `gemini-flash-latest`) should be double-checked against each provider's
  current free-tier model list before relying on them -- these change.
