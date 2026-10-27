-- Flattens betting lines down to one row per game (taking the consensus /
-- first available line). TODO: decide how to handle multiple books per game
-- -- this scaffold just grabs the first row per game_id.

with source as (
    select * from {{ source('raw', 'raw_betting_lines') }}
),

unnested as (
    select
        id                                  as game_id,
        line.provider                       as provider,
        cast(line.spread as float64)        as spread,
        cast(line.overUnder as float64)     as over_under
    from source,
    unnest(lines) as line
),

deduped as (
    select
        *,
        row_number() over (partition by game_id order by provider) as rn
    from unnested
)

select
    game_id,
    spread,
    over_under,
    provider
from deduped
where rn = 1
