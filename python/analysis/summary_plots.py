import os
import pandas as pd
import seaborn as sns
from sqlalchemy import create_engine
import matplotlib.pyplot as plt

OUTFILE = "C:\\DATA_ANALYSIS\\JAPAN\\00_SUMMARY\\plots\\"

user = os.getenv("DB_USER")
password = os.getenv("DB_PASS")
dbname = os.getenv("DB_NAME")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")

# Connection
engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}")

# SQL query
query = """
-- WEATHER SCORES
with weather_scores as(
	select
		extract(month from time) as month_number,
		round(greatest(0, 1 - abs(avg(temp_c) - 22) / 15.0), 2) as temp_score,
    		round(1 - (avg(rain_mm) / nullif((select MAX(rain_mm) from travel.weather_data), 0)), 2) as rain_score,
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
        extract(month from departure_date) as month_number,
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
		round(1 - (avg_monthly_visits / nullif(MAX(avg_monthly_visits) over(), 0)),2)
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
	        -- Adjusted festival weights
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
	w.month_number,
    w.weather_score,
	f.flight_score,
	v.visitors_score,
	fest.festival_score
from weather_scores w
	left join flight_scores f on w.month_number = f.month_number
	left join festival_scores fest on f.month_number = fest.m
	left join visitors_scores v on fest.m = v.month
order by total_score desc;
"""

df = pd.read_sql(query, engine)

# Line plot: All scores per month
df = df.sort_values("month_number")
plt.figure(figsize=(12,6))
plt.plot(df['month_name'], df['weather_score'], marker='o', label='Weather')
plt.plot(df['month_name'], df['flight_score'], marker='o', label='Flights')
plt.plot(df['month_name'], df['festival_score'], marker='o', label='Festivals')
plt.title('Scores per Month')
plt.xlabel('Month')
plt.ylabel('Score (0-1)')
plt.legend()
plt.grid(True)
plt.savefig(f"{OUTFILE}monthly_scores.png", dpi=300)
plt.show()
plt.close()

# Line plot: Total score
plt.figure(figsize=(12,6))
plt.plot(df['month_name'], df['total_score'], marker='o', label='Total Score', linewidth=2, color='black')
plt.title('Travel Score')
plt.xlabel('Month')
plt.ylabel('Score (0-1)')
plt.legend()
plt.grid(True)
plt.savefig(f"{OUTFILE}all_scores.png", dpi=300)
plt.show()
plt.close()

# Bar chart: Top recommended months
top_months = df.sort_values("total_score", ascending=False).head(5)
plt.figure(figsize=(8, 6))
sns.barplot(data=top_months, x="month_name", y="total_score")
plt.title("Top Recommended Months")
plt.ylabel("Total Score")
plt.xlabel("Month")
plt.tight_layout()
plt.savefig(f"{OUTFILE}top_months.png", dpi=300)
plt.show()
plt.close()

factors = ["weather_score", "flight_score", "festival_score", "visitors_score"]

# Stacked bar chart: Contribution to total
df_plot = df.set_index("month_name")[factors]
df_plot.plot(kind="bar", stacked=True, figsize=(10, 6), colormap="tab20")
plt.title("Contribution of Factors to Monthly Scores")
plt.ylabel("Score contribution")
plt.tight_layout()
plt.savefig(f"{OUTFILE}contributions.png", dpi=300)
plt.show()
plt.close()

# Heatmap: Factors vs Months
plt.figure(figsize=(12, 6))
heatmap_data = df.set_index("month_name")[factors]
sns.heatmap(heatmap_data.T, annot=True, cmap="YlGnBu", cbar=True, fmt=".2f")
plt.title("Heatmap of Factor Scores per Month")
plt.xlabel("Month")
plt.ylabel("Factor")
plt.tight_layout()
plt.savefig(f"{OUTFILE}heatmap_scores.png", dpi=300)
plt.show()
plt.close()