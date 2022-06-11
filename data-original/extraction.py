import sqlite3
import pandas as pd
# import pymongo
from pymongo import mongo_client
import math

CHUNK_SIZE = 1000000

client = mongo_client.MongoClient("mongodb://localhost:27017/", username="root", password="example")
db = client["spotify"] # Creating db in mongo

conn = sqlite3.connect("spotify.sqlite", isolation_level=None, detect_types=sqlite3.PARSE_COLNAMES)
conn.text_factory = lambda b: b.decode(errors = 'ignore')

cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Database description: \n", cursor.fetchall())

def zbrcniGa(table, query):
	print(f"Working on '{table}'...")
	db_df = pd.read_sql_query(f"{query}", conn)
	# db_df.to_csv(f'{table}.csv', index=False)
	print("Turning into dictionary...")

	low = 0
	high = CHUNK_SIZE
	for i in range(math.ceil(len(db_df) / CHUNK_SIZE)):
		print(f"i: {i}")
		db_df_sub = db_df[low:high]
		print(db_df_sub.head())
		low += CHUNK_SIZE
		high += CHUNK_SIZE
		if high > len(db_df):
			high = len(db_df)
		# df_sub.to_csv(f"data/{table}_decompose/audio_features_{i}.csv", index=False)
		data = db_df_sub.to_dict(orient='records')
		print(f"Inserting into '{table}' collection...")
		db[f"{table}"].insert_many(data)
		del(db_df_sub)
		del(data)
	del(db_df)
	print("-----------------------------------------")

zbrcniGa("albums", "SELECT id, name, album_type, release_date, popularity FROM albums")
zbrcniGa("artists", "SELECT * FROM artists")
zbrcniGa("audio_features", "SELECT id, round(acousticness,4) as acousticness, round(danceability,4) as danceability, duration, round(energy,4) as energy, round(instrumentalness,4) as instrumentalness, key, round(liveness,4) as liveness, round(loudness,4) as loudness, mode, round(speechiness,4) as speechiness, round(tempo,4) as tempo, time_signature, round(valence,4) as valence FROM audio_features")
zbrcniGa("genres", "SELECT * FROM genres")
zbrcniGa("r_albums_artists", "SELECT * FROM r_albums_artists")
zbrcniGa("r_albums_tracks", "SELECT * FROM r_albums_tracks")
zbrcniGa("r_artist_genre", "SELECT * FROM r_artist_genre")
zbrcniGa("r_track_artist", "SELECT * FROM r_track_artist")
zbrcniGa("tracks", "SELECT id, duration, explicit, name, popularity FROM tracks")

conn.close()