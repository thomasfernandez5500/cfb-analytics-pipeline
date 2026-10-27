-- Final mart: one row per game with both teams' outcomes side by side.
-- This is what ml/features.py and app/streamlit_app.py should read from.

with features as (
    select * from {{ ref('int_team_game_features') }}
    where is_home
)

select
    game_id,
    season_year,
    week,
    team                                   as home_team,
    opponent                               as away_team,
    points_scored                          as home_points,
    points_allowed                         as away_points,
    (points_scored > points_allowed)       as home_team_won,
    spread,
    over_under
from features
