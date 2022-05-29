import sqlite3
import pandas as pd

conn = sqlite3.connect("spotify.sqlite", isolation_level=None,
                       detect_types=sqlite3.PARSE_COLNAMES)
conn.text_factory = lambda b: b.decode(errors = 'ignore')

cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Database description: \n", cursor.fetchall())

db_df = pd.read_sql_query("SELECT * FROM albums", conn)
db_df.to_csv('albums.csv', index=False)

db_df = pd.read_sql_query("SELECT * FROM artists", conn)
db_df.to_csv('artists.csv', index=False)

db_df = pd.read_sql_query("SELECT * FROM audio_features", conn)
db_df.to_csv('audio_features.csv', index=False)

db_df = pd.read_sql_query("SELECT * FROM genres", conn)
db_df.to_csv('genres.csv', index=False)

db_df = pd.read_sql_query("SELECT * FROM r_albums_artists", conn)
db_df.to_csv('r_albums_artists.csv', index=False)

db_df = pd.read_sql_query("SELECT * FROM r_albums_tracks", conn)
db_df.to_csv('r_albums_tracks.csv', index=False)

db_df = pd.read_sql_query("SELECT * FROM r_artist_genre", conn)
db_df.to_csv('r_artist_genre.csv', index=False)

db_df = pd.read_sql_query("SELECT * FROM r_track_artist", conn)
db_df.to_csv('r_track_artist.csv', index=False)

db_df = pd.read_sql_query("SELECT * FROM tracks", conn)
db_df.to_csv('tracks.csv', index=False)

# cursor = conn.cursor()
# for row in cursor.execute("SELECT * FROM albums"):
# 	print(row)

conn.close()