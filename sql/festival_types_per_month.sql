with festival_type as (
    select
        generate_series(start_month, end_month) as month,
        type
    from travel.festivals
)
select
     to_char(to_date(month::text, 'MM'), 'Month') AS month_name,
    type,
    count(*) as count
from festival_type
group by month, type
order by month, type;

select distinct type
from travel.festivals;

with festival_type as (
    select
        generate_series(start_month, end_month) AS month,
        type
    from travel.festivals
)
select
    to_char(to_date(month::text, 'MM'), 'Month') AS month_name,
    count(*) filter (where type = 'Anime culture') as anime_culture,
    count(*) filter (where type = 'Dance festival') as dance_festival,
    count(*) filter (where type = 'Fire festival') as fire_festival,
    count(*) filter (where type = 'Technology festival') as technology_festival,
    count(*) filter (where type = 'Nature festival') as nature_festival,
    count(*) filter (where type = 'Fireworks display') as fireworks,
    count(*) filter (where type = 'Sport activity') as sport_activity,
    count(*) filter (where type = 'Cultural festival' or type = 'Cultural festival / Obon' or type = 'Cultural event') as cultural_festival,
    count(*) filter (where type = 'Sakura') as sakura,
    count(*) filter (where type = 'Snow_festival') as snow_festival,
    count(*) filter (where type = 'Music festival') as music_festival
from festival_type
group by month
order by month;

select distinct destination from travel.flights;

