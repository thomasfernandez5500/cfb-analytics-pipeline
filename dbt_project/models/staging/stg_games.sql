-- Cleans and standardizes the raw games feed: one row per game, typed
-- columns, consistent team-name casing.

with source as (
    select * from {{ source('raw', 'raw_games') }}
)

select
    id                                      as game_id,
    season                                  as season_year,
    week,
    seasonType                              as season_type,
    cast(startDate as timestamp)            as start_date,
    neutralSite                             as neutral_site,
    conferenceGame                          as conference_game,
    homeTeam                                as home_team,
    homeConference                          as home_conference,
    cast(homePoints as int64)               as home_points,
    awayTeam                                as away_team,
    awayConference                          as away_conference,
    cast(awayPoints as int64)               as away_points,
    venue

from source
where completed = true
  and homePoints is not null
  and awayPoints is not null