-- TEMPERATURE
with temperature as (
select
	to_char(time,'Month') as month,
	round(avg(temp_c), 2) as average_temperature
from travel.weather_data
where
	extract(month from time) in (10, 4, 3, 8, 9)
group by to_char(time,'Month')
),
-- FLIGHTS COSTS
flights as(
select
	to_char(departure_date,'Month') as month,
	round(avg(price), 2) as average_flight_cost
from travel.flights
where
	extract(month from departure_date) in (10, 4, 3, 8, 9)
group by to_char(departure_date,'Month')
)
select
	t.month as month,
	t.average_temperature as average_temperature,
	f.average_flight_cost as average_flight_cost
from temperature t
	join flights f on t.month = f.month
order by t.month;

