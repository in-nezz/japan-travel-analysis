import re
from pathlib import Path
import pandas as pd
import glob
import os  # for working with file names

DATA_DIR = "C:\\DATA_ANALYSIS\\JAPAN\\data_raw\\weather"
OUTFILE = "C:\\DATA_ANALYSIS\\JAPAN\\datasets\\weather.csv"
SOURCE_URL = os.getenv("SOURCE_URL", "https://open-meteo.com/")

# Remove special characters
def normalize_col(col):
    if not isinstance(col, str):
        col = str(col)
    s = col.strip().lower()
    s = s.replace("Â", "")
    s = s.replace("°", "")
    s = re.sub(r"\(.*?\)", "", s)
    s = s.replace("%", "")
    s = re.sub(r"[^a-z0-9_\s]", "", s)
    s = re.sub(r"\s+", "_", s).strip("_")
    return s

DESIRED_COLS = [
    "city",
    "time",
    "temp_c",
    "relative_humidity",
    "apparent_temperature",
    "rain_mm",
    "snowfall_cm",
    "precipitation_mm",
    "is_day",
    "sunshine_duration",
    "source"
]

files = glob.glob("C:\\DATA_ANALYSIS\\JAPAN\\data_raw\\weather\\*.csv")
if not files:
    raise SystemExit(f"No CSV files found in {DATA_DIR}")

dfs = []

for file in files:
    city_raw = Path(file).stem
    city = city_raw.replace("_", " ").title()

    try:
        df = pd.read_csv(file, skiprows=3, sep=None, engine="python", encoding="utf-8", on_bad_lines="skip")
    except Exception as e:
        df = pd.read_csv(file, skiprows=3, sep="\t", encoding="utf-8", on_bad_lines="skip")

    df.columns = [normalize_col(c) for c in df.columns]

    col_map = {}
    for c in df.columns:
        if c == "time":
            col_map[c] = "time"
        elif "temperature_2m" in c or c.startswith("temperature"):
            col_map[c] = "temp_c"
        elif "relative_humidity" in c or "relativehumidity" in c:
            col_map[c] = "relative_humidity"
        elif "apparent_temperature" in c or "apparenttemperature" in c or "apparent" in c:
            col_map[c] = "apparent_temperature"
        elif c == "rain" or (("rain" in c) and ("precipitation" not in c)):
            col_map[c] = "rain_mm"
        elif "snow" in c:
            col_map[c] = "snowfall_cm"
        elif "precipitation" in c:
            col_map[c] = "precipitation_mm"
        elif c.startswith("is_day") or c == "isday" or c == "is_day":
            col_map[c] = "is_day"
        elif "sunshine" in c:
            col_map[c] = "sunshine_duration"
        else:
            col_map[c] = c

    df = df.rename(columns=col_map)

    # Convert time to datetime
    df["time"] = pd.to_datetime(df["time"], errors="coerce")

    # Normalize is_day
    if "is_day" in df.columns:
        try:
            df["is_day"] = pd.to_numeric(df["is_day"], errors="coerce").astype("Int64")
            df["is_day"] = df["is_day"].map({1: True, 0: False})
        except Exception:
            df["is_day"] = df["is_day"].astype(str).str.strip().str.lower().map(
                lambda x: True if x in ("1", "true", "yes", "y") else (
                    False if x in ("0", "false", "no", "n") else pd.NA)
            )

    # City column
    df.insert(0, "city", city)

    # Source column
    df["source"] = SOURCE_URL

    dfs.append(df)

merged = pd.concat(dfs, ignore_index=True, sort=False)

for c in DESIRED_COLS:
    if c not in merged.columns:
        merged[c] = pd.NA
merged = merged[DESIRED_COLS]

merged.to_csv(OUTFILE, index=False)