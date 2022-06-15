import sqlite3
import pandas as pd
# import pymongo
from pymongo import mongo_client
import math
from timeit import default_timer as timer

start = timer()

CHUNK_SIZE = 500000
UNIX_DATE = 1514761200000 # 1514761200000 is the unix date for 1/1/2018

client = mongo_client.MongoClient("mongodb://localhost:27017/", username="root", password="example")
db = client["spotify-original"] # Creating db in mongo

conn = sqlite3.connect("spotify.sqlite", isolation_level=None, detect_types=sqlite3.PARSE_COLNAMES)
conn.text_factory = lambda b: b.decode(errors = 'ignore')

cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Database description: \n", cursor.fetchall())

def extractData(table, query):
	print(f"Working on '{table}'...")
	db_df = pd.read_sql_query(f"{query}", conn)
	# db_df.to_csv(f'{table}.csv', index=False)
	print("Turning into dictionary...")

	low = 0
	high = CHUNK_SIZE
	# print("len(db_df): ", len(db_df))
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

# extractData("albums", f"SELECT id, name, album_type, release_date, popularity FROM albums WHERE release_date > {UNIX_DATE}")

# extractData("artists", f"SELECT * FROM artists WHERE id in (SELECT artist_id FROM r_albums_artists WHERE album_id in (SELECT id FROM albums WHERE release_date > {UNIX_DATE}))")

# extractData("audio_features", f"SELECT id, round(acousticness,4) as acousticness, round(danceability,4) as danceability, duration, round(energy,4) as energy, round(instrumentalness,4) as instrumentalness, key, round(liveness,4) as liveness, round(loudness,4) as loudness, mode, round(speechiness,4) as speechiness, round(tempo,4) as tempo, time_signature, round(valence,4) as valence FROM audio_features WHERE id in (SELECT id FROM tracks WHERE id in (SELECT track_id FROM r_albums_tracks WHERE album_id in (SELECT id FROM albums WHERE release_date > {UNIX_DATE})))")

# TODO: Ova tabela nam nije potrebna, sve vec imamo u r_artist_genre, ali dobra je da se vidi koji sve zanrovi postoje i koliko ih ima
# extractData("genres", "SELECT * FROM genres")

# extractData("r_albums_artists", f"SELECT * FROM r_albums_artists WHERE album_id in (SELECT id FROM albums WHERE release_date > {UNIX_DATE})")

# extractData("r_albums_tracks", f"SELECT * FROM r_albums_tracks WHERE album_id in (SELECT id FROM albums WHERE release_date > {UNIX_DATE})")

# extractData("r_artist_genre", f"SELECT * FROM r_artist_genre WHERE artist_id in (SELECT id FROM artists WHERE id in (SELECT artist_id FROM r_albums_artists WHERE album_id in (SELECT id FROM albums WHERE release_date > {UNIX_DATE})))")

# TODO: Ova tabela nam mozda ne treba ali je korisna za upite
extractData("r_track_artist", f"SELECT * FROM r_track_artist WHERE track_id in (SELECT id FROM tracks WHERE id in (SELECT track_id FROM r_albums_tracks WHERE album_id in (SELECT id FROM albums WHERE release_date > {UNIX_DATE})))")

# extractData("tracks", f"SELECT id, duration, explicit, name, popularity FROM tracks WHERE id in (SELECT track_id FROM r_albums_tracks WHERE album_id in (SELECT id FROM albums WHERE release_date > {UNIX_DATE}))") # 198s

conn.close()

end = timer()
print("Time: ", end - start)