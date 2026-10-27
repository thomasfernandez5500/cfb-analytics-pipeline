-- One row per (game, team) with the features the ML model will consume:
-- points scored/allowed, home/away flag, betting line, recruiting gap, etc.
-- TODO: join in stg advanced stats and recruiting once those staging models
-- are built out (left as an exercise -- same pattern as stg_games.sql).

with games as (
    select * from {{ ref('stg_games') }}
),

lines as (
    select * from {{ ref('stg_betting_lines') }}
),

home_rows as (
    select
        g.game_id,
        g.season_year,
        g.week,
        g.home_team as team,
        g.away_team as opponent,
        true as is_home,
        g.home_points as points_scored,
        g.away_points as points_allowed,
        l.spread,
        l.over_under
    from games g
    left join lines l on g.game_id = l.game_id
),

away_rows as (
    select
        g.game_id,
        g.season_year,
        g.week,
        g.away_team as team,
        g.home_team as opponent,
        false as is_home,
        g.away_points as points_scored,
        g.home_points as points_allowed,
        l.spread * -1 as spread,
        l.over_under
    from games g
    left join lines l on g.game_id = l.game_id
)

select * from home_rows
union all
select * from away_rows
