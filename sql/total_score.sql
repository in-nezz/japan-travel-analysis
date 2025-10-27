-- WEATHER SCORES
with weather_scores as(
	select
		extract(month from time) as month_number,
    	-- Scores
		round(avg(0, 1 - abs(avg(temp_c) - 22) / 15.0), 2) as temp_score,
    	round(1 - (avg(rain_mm) / nullif((select max(rain_mm) from travel.weather_data), 0)), 2) as rain_score,
   		round(1 - least(avg(snowfall_cm) / 1.0, 1), 2) as snow_score,
    	round(avg(sunshine_duration) / nullif((select max(sunshine_duration) from travel.weather_data), 1), 2) as sunshine_score,
    	round(1 - (abs(avg(relative_humidity) - 50) / nullif((
    			select max(abs(relative_humidity - 50))
    			from travel.weather_data), 1)), 2)
    			as humidity_score,	
    	-- Composite score
    	round(
    				(
        			(1 - abs(avg(temp_c) - 22) / 15.0) +
        			(1 - (avg(rain_mm) / nullif((select max(rain_mm) from travel.weather_data), 0))) +
        			(1 - least(avg(snowfall_cm) / 1.0, 1)) +
        			(avg(sunshine_duration) / nullif((select max(sunshine_duration) from travel.weather_data), 1)) +
        			(1 - (abs(avg(relative_humidity) - 50) / nullif((select max(abs(relative_humidity - 50)) from travel.weather_data), 1)))
    			) / 5.0
    		, 2) as weather_score
	from travel.weather_data
	group by month_number
),
-- FLIGHT SCORES
flight_scores as(
	select
        extract(MONTH from departure_date) as month_number,
        round(1 - (avg(price) / nullif((select max(price) from travel.flights), 0)), 2) as flight_score
    from travel.flights
    group by month_number
),
-- VISITORS SCORES
visitors_month_year as(
	select
		month,
		year,
		sum(visitor_arrivals) as monthly_visits
	from travel.visitors
	group by month, year
),
avg_visits_per_month as(
	select
		month,
		avg(monthly_visits) as avg_monthly_visits
	from visitors_month_year
	group by month
),
visitors_scores as(
	select
		month,
		ROUND(1 - (avg_monthly_visits / nullif(max(avg_monthly_visits) over(), 0)),2)
		as visitors_score
	from avg_visits_per_month
),
-- FESTIVALS SCORES
chosen_festivals as (
    select
        m,
        cf.type
    from generate_series(1, 12) as m
    left join (
        select
            generate_series(start_month, end_month) as month_number,
            type
        from travel.festivals
        where type in (
            'Sakura', 
            'Cultural festival', 
            'Cultural festival / Obon',
            'Nature festival',
            'Seasonal event',
            'Fireworks display',
            'Dance festival',
            'Fire festival'
        )
    ) cf
    on m = cf.month_number
),
festivals_weights as (
    select
        m,
        case
	        -- Adjust festival weights
            when type = 'Sakura' then 0.30
            when type in ('Cultural festival', 'Cultural festival / Obon') then 0.20
            when type = 'Nature festival' then 0.10
            when type = 'Seasonal event' then 0.10
            when type = 'Fireworks display' then 0.05
            when type = 'Dance festival' then 0.10
            when type = 'Fire festival' then 0.15
            else 0
        end as weight
    from chosen_festivals
),
festival_scores as (
    select
        m,
        coalesce(ROUND(SUM(weight) / nullif(MAX(SUM(weight)) over(), 0), 2),0) as festival_score
    from festivals_weights
    group by m
)
-- SUM UP SCORES
select
	to_char(to_date(w.month_number::text, 'MM'), 'Month') as month_name,
	round(w.weather_score * 0.4 + f.flight_score * 0.2 + festival_score * 0.2 + v.visitors_score * 0.2, 3) as total_score,
	w.weather_score,
	f.flight_score,
	v.visitors_score,
	fest.festival_score
from weather_scores w
	left join flight_scores f on w.month_number = f.month_number
	left join festival_scores fest on f.month_number = fest.m
	left join visitors_scores v on fest.m = v.month
	cross join accommodation_scores a
order by total_score desc;






