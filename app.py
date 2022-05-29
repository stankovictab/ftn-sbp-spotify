import pymongo
import pandas as pd
import json
import math

# mongodb://mongo:27017 doesn't work
# Authentication is also needed
client = pymongo.MongoClient("mongodb://localhost:27017/", username="root", password="example")

db = client["spotify"] # Creating db in mongo

tables = ["audio_features", "tracks", "albums", "artists", "genres", "r_albums_artists", "r_albums_tracks", "r_artist_genre", "r_track_artist"]

print("Reading CSV...")
df = pd.read_csv("data/audio_features.csv")
df.drop('analysis_url', axis=1, inplace=True)
low = 0
high = 2000000
for i in range(math.ceil(len(df) / 2000000)):
	print(f"I: {i}")
	df_sub = df[low:high]
	print(df_sub.head())
	low += 2000000
	if high == 8000000:
		high = len(df)
	else:
		high += 2000000
	df_sub.to_csv(f"data/audio_features_decompose/audio_features_{i}.csv", index=False)

# TODO: Decompose other csv files


# for table in tables:
# 	print(f"Importing table '{table}'...")
# 	print("Reading CSV...")
# 	df = pd.read_csv(f"data/{table}.csv")
# 	print("Turning into dictionary...")
# 	data = df.to_dict(orient='records')
# 	print(f"Inserting into '{table}' collection...")
# 	db[f"{table}"].insert_many(data)