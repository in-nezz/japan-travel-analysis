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
query = """with festival_type as (
    select
        generate_series(start_month, end_month) as month,
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
"""

df = pd.read_sql(query, engine)

factors = ["anime_culture", "dance_festival", "fire_festival", "technology_festival", "nature_festival", "fireworks", "sport_activity", "cultural_festival", "sakura", "snow_festival", "music_festival"]

# Heatmap: Festivals vs Months
plt.figure(figsize=(12, 6))
heatmap_data = df.set_index("month_name")[factors]
sns.heatmap(heatmap_data.T, annot=True, cmap="YlGnBu", cbar=True, fmt=".2f")
plt.title("Heatmap of Festivals per Month")
plt.xlabel("Month")
plt.ylabel("Festival type")
plt.tight_layout()
plt.savefig(f"{OUTFILE}heatmap_festivals.png", dpi=300)
plt.show()
plt.close()