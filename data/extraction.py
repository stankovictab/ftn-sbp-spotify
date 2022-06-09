import sqlite3
import pandas as pd

conn = sqlite3.connect("spotify.sqlite", isolation_level=None,
                       detect_types=sqlite3.PARSE_COLNAMES)
conn.text_factory = lambda b: b.decode(errors = 'ignore')

cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Database description: \n", cursor.fetchall())

print("Exporting 'albums' into CSV...")
db_df = pd.read_sql_query("SELECT id, name, album_type, release_date, popularity FROM albums", conn)
db_df.to_csv('albums.csv', index=False)

print("Exporting 'artists' into CSV...")
db_df = pd.read_sql_query("SELECT * FROM artists", conn)
db_df.to_csv('artists.csv', index=False)

print("Exporting 'audio_features' into CSV...")
db_df = pd.read_sql_query("SELECT id, round(acousticness,4) as acousticness, round(danceability,4) as danceability, duration, round(energy,4) as energy, round(instrumentalness,4) as instrumentalness, key, round(liveness,4) as liveness, round(loudness,4) as loudness, mode, round(speechiness,4) as speechiness, round(tempo,4) as tempo, time_signature, round(valence,4) as valence FROM audio_features", conn)
db_df.to_csv('audio_features.csv', index=False)

print("Exporting 'genres' into CSV...")
db_df = pd.read_sql_query("SELECT * FROM genres", conn)
db_df.to_csv('genres.csv', index=False)

print("Exporting 'r_albums_artists' into CSV...")
db_df = pd.read_sql_query("SELECT * FROM r_albums_artists", conn)
db_df.to_csv('r_albums_artists.csv', index=False)

print("Exporting 'r_albums_tracks' into CSV...")
db_df = pd.read_sql_query("SELECT * FROM r_albums_tracks", conn)
db_df.to_csv('r_albums_tracks.csv', index=False)

print("Exporting 'r_artist_genre' into CSV...")
db_df = pd.read_sql_query("SELECT * FROM r_artist_genre", conn)
db_df.to_csv('r_artist_genre.csv', index=False)

print("Exporting 'r_track_artist' into CSV...")
db_df = pd.read_sql_query("SELECT * FROM r_track_artist", conn)
db_df.to_csv('r_track_artist.csv', index=False)

print("Exporting 'tracks' into CSV...")
db_df = pd.read_sql_query("SELECT id, duration, explicit, audio_feature_id, name, popularity FROM tracks", conn)
db_df.to_csv('tracks.csv', index=False)

# cursor = conn.cursor()
# for row in cursor.execute("SELECT * FROM albums"):
# 	print(row)

conn.close()