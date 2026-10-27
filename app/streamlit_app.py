"""
Public-facing dashboard: pick a matchup, see the model's win probability and
an LLM-generated blurb. Deploy this file on Streamlit Community Cloud or
HF Spaces.

TODO: replace the hardcoded team list with a live query against fct_games,
and wire up real context text for llm/generate_insight.py instead of the
placeholder string below.
"""
import sys
import os
import streamlit as st

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "ml"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "llm"))

from predict import predict_matchup          # noqa: E402
from generate_insight import generate_insight  # noqa: E402

st.set_page_config(page_title="CFB Win Probability", page_icon="🏈")
st.title("🏈 College Football Win Probability")
st.caption("Built on CFBD data, dbt, XGBoost, and a free-tier LLM insight layer.")

col1, col2 = st.columns(2)
with col1:
    home_team = st.text_input("Home team", "Texas")
with col2:
    away_team = st.text_input("Away team", "Oklahoma")

spread = st.slider("Vegas spread (home team, negative = favored)", -30.0, 30.0, -3.5)
over_under = st.slider("Over/under", 20.0, 90.0, 55.0)
week = st.slider("Week", 1, 15, 8)

if st.button("Predict"):
    win_prob = predict_matchup(spread=spread, over_under=over_under, week=week)
    st.metric(f"{home_team} win probability", f"{win_prob:.1%}")

    with st.spinner("Generating insight..."):
        try:
            context = f"{home_team} vs {away_team}, week {week}."  # TODO: real context
            insight = generate_insight(context=context, win_prob=win_prob)
            st.write(insight)
        except Exception as e:
            st.info(f"LLM insight unavailable: {e}")
