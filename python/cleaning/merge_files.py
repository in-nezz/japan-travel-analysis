import pandas as pd

FILE_1 = "C:\\DATA_ANALYSIS\\JAPAN\\data_test\\hostels.csv"
FILE_2 = "C:\\DATA_ANALYSIS\\JAPAN\\data_test\\airbnb.csv"
OUTFILE = "C:\\DATA_ANALYSIS\\JAPAN\\data_test\\accomodation.csv"

# Read the CSVs into DataFrames
df1 = pd.read_csv(FILE_1)
df2 = pd.read_csv(FILE_2)

df_merged = pd.concat([df1, df2], ignore_index=True)
df_merged.to_csv(OUTFILE, index=False)