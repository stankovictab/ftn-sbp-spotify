from audioop import tostereo
from pymongo import mongo_client
import csv

class ArtistsParser:
	def __init__(self, file):
		self._file = file

	def add_artists_to_db(self, url, db_name):
		client = mongo_client.MongoClient(url, username="root", password="example")
		db = client[db_name]
		artists = []
		
		with open(self._file, 'r') as csv_file:
			reader = csv.DictReader(csv_file)
			for row in reader:
				artist = get_artist(row)
				artists.append(artist)
				# TODO: Maybe do insert_one() to not use tracks list for memory usage
		
		db['artists'].insert_many(artists)
		del(artists)
			
def get_artist(row) -> dict:
	genres_str = row['genres']

	if genres_str[0] == '[':
		# Ima vise
		genres_str = genres_str.replace('[', '')
		genres_str = genres_str.replace(']', '')
		genres_array = genres_str.split(',')
		genres_array = [genre.strip(' ') for genre in genres_array]
		genres_array = [genre.strip('"') for genre in genres_array]
		genres_array = [genre.strip("'") for genre in genres_array]
		genres_array = [genre.strip('"') for genre in genres_array]
	elif genres_str[1] == ']': 
		# Nema ni jedan
		genres_array = []
	else:
		genres_str = genres_str.strip('[')
		genres_str = genres_str.strip(']')
		genres_str = genres_str.strip("'")
		genres_array = [genres_str]
	# TODO: Genres

	return {
		'_id': row['id'],
		'followers': row['followers'],
		'genres': genres_array, # TODO: Need to parse this as a list?
		'name': row['name'],
		'popularity': int(row['popularity'])
	}


class TracksParser:
	def __init__(self, file):
		self._file = file

	def add_tracks_to_db(self, url, db_name):
		client = mongo_client.MongoClient(url, username="root", password="example")
		db = client[db_name]
		tracks = []
		
		with open(self._file, 'r') as csv_file:
			reader = csv.DictReader(csv_file)
			for row in reader:
				track = get_track(row)
				tracks.append(track)
				# TODO: Maybe do insert_one() to not use tracks list for memory usage
		
		db['tracks'].insert_many(tracks)
		del(tracks)

def get_track(row) -> dict:
	artists_name_str = row['artists']
	artists_id_str = row['id_artists']

	if artists_name_str[0] == '[':
		# Ima vise
		artists_name_str = artists_name_str.replace('[', '')
		artists_name_str = artists_name_str.replace(']', '')
		artists_name_array = artists_name_str.split(',')
		artists_name_array = [artist.strip(' ') for artist in artists_name_array]
		artists_name_array = [artist.strip('"') for artist in artists_name_array]
		artists_name_array = [artist.strip("'") for artist in artists_name_array]
		artists_name_array = [artist.strip('"') for artist in artists_name_array]

		artists_id_str = artists_id_str.replace('[', '')
		artists_id_str = artists_id_str.replace(']', '')
		artists_id_array = artists_id_str.split(',')
		artists_id_array = [artist.strip(' ') for artist in artists_id_array]
		artists_id_array = [artist.strip('"') for artist in artists_id_array]
		artists_id_array = [artist.strip("'") for artist in artists_id_array]
		artists_id_array = [artist.strip('"') for artist in artists_id_array]
	else:
		# Ima samo jedan
		artists_name_str = artists_name_str.strip('[')
		artists_name_str = artists_name_str.strip(']')
		artists_name_str = artists_name_str.strip("'")
		artists_name_array = [artists_name_str]

		artists_id_str = artists_id_str.strip('[')
		artists_id_str = artists_id_str.strip(']')
		artists_id_str = artists_id_str.strip("'")
		artists_id_array = [artists_id_str]

	# artists_dict = {}
	artists_array = []

	while len(artists_name_array) > len(artists_id_array):
		artists_id_array.append(artists_id_array[0])

	for i in range(len(artists_name_array)):
		# artists_dict[str(i)] = {"id": artists_id_array[i], "name": artists_name_array[i]}
		artists_array.append({"id": artists_id_array[i], "name": artists_name_array[i]})

	return {
		'_id': row['id'],
		'name': row['name'],
		'popularity': int(row['popularity']),
		'duration_ms': int(row['duration_ms']),
		'explicit': int(row['explicit']),
		'artists': artists_array,
		#  'id_artists': row['id_artists'], # TODO: Need to parse this as a list?
		'release_date': row['release_date'],
		'danceability': float(row['danceability']),
		'energy': float(row['energy']),
		'key': int(row['key']),
		'loudness': float(row['loudness']),
		'mode': int(row['mode']),
		'speechiness': float(row['speechiness']),
		'acousticness': float(row['acousticness']),
		'instrumentalness': float(row['instrumentalness']),
		'liveness': float(row['liveness']),
		'valence': float(row['valence']),
		'tempo': float(row['tempo']),
		'time_signature': int(row['time_signature'])
	}

print("Artists")
artists_parser = ArtistsParser('data/artists.csv')
artists_parser.add_artists_to_db(url = 'mongodb://localhost:27017/', db_name = 'spotify')

print("Tracks")
tracks_parser = TracksParser('data/tracks.csv')
tracks_parser.add_tracks_to_db(url = 'mongodb://localhost:27017/', db_name = 'spotify')