import pandas as pd
import numpy as np

FILE = "C:\\DATA_ANALYSIS\\JAPAN\\data_raw\\attractions\\festivals-1.csv"
OUTFILE = "C:\\DATA_ANALYSIS\\JAPAN\\datasets\\festivals.csv"

df = pd.read_csv(FILE, encoding='utf-8')

# Replace common "empty" placeholders with np.nan
df.replace(['', 'NaN', 'null', None], np.nan, inplace=True)

df.to_csv(OUTFILE, index=False)