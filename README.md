# Opis
Projekat namenjen za rad sa NoSQL bazom (u ovom slucaju MongoDB) sa ciljem izvlačenja znanja iz odabrane baze podataka. Izvršena je optimizacija logičke strukture baze primenom šablona proširene reference, kao i korišćenjem indeksa.

# ftn-sbp-spotify
[Sistemi Baza Podataka] - Predmetni Projekat - Optimizacija Dokument Orijentisane NoSQL baze podataka.

## Setup

```shell
sudo snap install robo3t-snap # MongoDB Query Environment
pip install pymongo
pip install pandas
```

Skup podataka je dobavljen sa [ove stranice](https://www.kaggle.com/datasets/maltegrosse/8-m-spotify-tracks-genre-audio-features) u `.sqlite` formatu.\
Ucitavanje podataka u MongoDB bazu podataka je izvršeno u `data-original/extraction.py` skripti.

## Inicijalna Logička Šema

Inicijalna logička šema je prikazana u `data-original/template.js` fajlu.

## Upiti

Đorđe :
- Koji su najpopularniji albumi po žanrovima?
- Iz koje godine je album sa najviše akustičnih pesama?
- Koji umetnik u proseku izbacuje najglasnije pesme?
- Koji umetnici su izbacili najviše pesama iz žanra ‘rap’?
- Odrediti umetnike koji su najviše svojih pesama snimali uživo.

Igor :
- Koji su najpopularniji žanrovi po broju pratioca umetnika koji ih prave?
- Koji su umetnici sa najviše eksplicitnih pesama?
- Pesme kojeg izvođača su u proseku najviše “danceable”?
- Koji albumi u proseku imaju najduže pesme?
- Odrediti albume sa najenergičnijim pesmama.

## Neoptimizovani Upiti

### Đorđe
- 1 - Koji su najpopularniji albumi po žanrovima?\
Time: `8.56s`
```js
db.r_albums_artists.createIndex({"album_id": 1})
db.r_artist_genre.createIndex({"artist_id": 1})

db.r_albums_artists.dropIndex({"album_id": 1})
db.r_artist_genre.dropIndex({"artist_id": 1})

db.albums.aggregate([
    {$limit: 100},
    // Adding artists to album (as an array)
    {$lookup: {
        from: 'r_albums_artists',
        localField: 'id', 
        foreignField: 'album_id', 
//         pipeline: [
//             {$project: {"_id": 0, "genre_id": 1}}
//         ],
        as: 'artists'}},
    {$unwind: "$artists"}, // Split an album with many artists into many of the same album with 1 artist, in order to lookup by artist_id
    {$match: {"album_type": "album"}},
    // Adding genres to album (as an array)
    {$lookup: {
        from: 'r_artist_genre', 
        localField: 'artists.artist_id', 
        foreignField: 'artist_id', 
//         pipeline: [
//             {$project: {"_id": 0, "track_id": 1}}
//         ], 
        as: 'genres'}},
    {$unwind: "$genres"}, // Split an album with many genres into many of the same album with 1 genre, in order to group and max
    {$group: {_id: {most_popular_album: "$name", genre: "$genres.genre_id"}, max_popularity: {$max: "$popularity"}}},
    {$sort: {"max_popularity": -1}}
], {allowDiskUse: true})
```
- 2 - Iz koje godine je album sa najviše akustičnih pesama?\
Time: `826s`
```js
db.r_albums_tracks.createIndex({"album_id": 1})
db.audio_features.createIndex({"id": 1})

db.r_albums_tracks.dropIndex({"album_id": 1})
db.audio_features.dropIndex({"id": 1})

db.albums.aggregate([
    {$limit: 100},
    {$project: {"_id": 0, "id": 1, "name": 1, "release_date": 1}},
    {$lookup: {
        from: 'r_albums_tracks',
        localField: 'id', 
        foreignField: 'album_id', 
        pipeline: [
            {$project: {"_id": 0, "track_id": 1}}
        ],
        as: 'tracks'}},
    {$unwind: "$tracks"},
    {$lookup: {
        from: 'audio_features', 
        localField: 'tracks.track_id', 
        foreignField: 'id', 
        pipeline: [
            {$project: {"_id": 0, "acousticness": 1}}
        ], 
        as: 'features'}},
    {$unwind: "$features"},
    {$match: {"features.acousticness": {$gt: 0.5}}},
    {$group: {_id: {album_name: "$name", release_date: "$release_date"}, num_acoustic_tracks: {$sum: 1}}},
    {$sort: {"num_acoustic_tracks": -1}},
], {allowDiskUse: true})
```

- 3 - Koji umetnik u proseku izbacuje najglasnije pesme?\
Time: `123s`
```js
db.audio_features.createIndex({"id": 1})
db.r_track_artist.createIndex({"track_id": 1})
db.artists.createIndex({"id": 1})

db.audio_features.dropIndex({"id": 1})
db.r_track_artist.dropIndex({"track_id": 1})
db.artists.dropIndex({"id": 1})

db.tracks.aggregate([
    {$limit: 100},
    // Adding audio features information (as an array)
    {
        $lookup:{
			from: 'audio_features',
			localField: 'id',
			foreignField: 'id',
			as: 'audio_features'
        }
    },
    // Adding artist id information (as an array)
    {
        $lookup: {
			from: 'r_track_artist',
			localField: 'id',
			foreignField: 'track_id',
			as: 'artists'
        }
    },
    {$unwind: "$audio_features"}, // To not make it into an array
    {$unwind: "$artists"}, // Split a track with many artists into many of the same track with 1 artist
    {$group: {_id: "$artists.artist_id", avg_loudness: {$avg: "$audio_features.loudness"}}},
//     {$group: {_id: "$artists.artist_id", pop: {$avg: "$popularity"}}},
    // Adding artist name information (as an array)
    {
        $lookup: {
			from: 'artists',
			localField: '_id',
			foreignField: 'id',
			as: 'artist_name'
        }
    },
    {$sort: {"avg_loudness": -1}}
], {allowDiskUse: true})
```
- 4 - Koji umetnici su izbacili najviše pesama iz žanra 'rap'?\
Time: `12.3s`
```js
db.r_artist_genre.createIndex({"artist_id": 1})
db.r_track_artist.createIndex({"artist_id": 1})

db.r_artist_genre.dropIndex({"artist_id": 1})
db.r_track_artist.dropIndex({"artist_id": 1})

db.artists.aggregate([
    {$limit: 100},
    // Show only name and id for $lookup
    {$project: {"name": 1, "id": 1}},
    // Adding genre info for artist
    {$lookup: {
        from: 'r_artist_genre',
        localField: 'id', 
        foreignField: 'artist_id', 
        pipeline: [
            {$project: {"_id": 0, "genre_id": 1}}
        ],
        as: 'genre'}},
    {$unwind: "$genre"},
    {$match: {"genre.genre_id": "rap"}},
    // Adding tracks to artists (as an array)
    {$lookup: {
        from: 'r_track_artist', 
        localField: 'id', 
        foreignField: 'artist_id', 
        pipeline: [
            {$project: {"_id": 0, "track_id": 1}}
        ], 
        as: 'tracks'}},
    {$unwind: "$tracks"}, // Split an artist with many tracks_infos into many of the same artist with 1 tracks_info, in order to group and sum
    {$group: {_id: {name: "$name", genre: "$genre"}, num_songs: {$sum: 1}}},
    {$sort: {"num_songs": -1}}
], {allowDiskUse: true})
```
- 5 - Odrediti umetnike koji su najviše svojih pesama snimali uživo.\
Time: `1200s` (approx. - pokrenuto sa `$limit: 10`, pomnozeno sa 10)
```js
db.r_track_artist.createIndex({"artist_id": 1})
db.audio_features.createIndex({"id": 1})

db.r_track_artist.dropIndex({"artist_id": 1})
db.audio_features.dropIndex({"id": 1})

db.artists.aggregate([
    {$limit: 100},
    {$project: {"_id": 0, "id": 1, "name": 1}},
    {$lookup: {
        from: 'r_track_artist',
        localField: 'id', 
        foreignField: 'artist_id', 
//         pipeline: [
//             {$project: {"_id": 0, "track_id": 1}}
//         ],
        as: 'tracks'}},
    {$unwind: "$tracks"},
    {$lookup: {
        from: 'audio_features', 
        localField: 'tracks.track_id', 
        foreignField: 'id', 
//         pipeline: [
//             {$project: {"_id": 0, "duration": 1}}
//         ], 
        as: 'features'}},
    {$unwind: "$features"},
    {$match: {"features.liveness": {$gt: 0.5}}},
    {$group: {_id: {artist_name: "$name"}, num_live_songs: {$sum: 1}}},
    {$sort: {"num_live_songs": -1}},
], {allowDiskUse: true})
```


### Igor
- 1 - Koji su najpopularniji žanrovi po broju pratioca umetnika koji ih prave?\
Time: `8.92s`
```js
db.r_artist_genre.createIndex({"artist_id": 1})

db.r_artist_genre.dropIndex({"artist_id": 1})

db.artists.aggregate([
    {$limit: 100},
    // Adding audio features information (as an array)
    {
        $lookup:{
                from: 'r_artist_genre',
                localField: 'id',
                foreignField: 'artist_id',
                as: 'genres'
        }
    },
    {$unwind: "$genres"}, // Split an artist with many genres into many of the same artist with 1 genre
    {$group: {_id: "$genres.genre_id", num_followers: {$sum: "$followers"}}},
    {$sort: {"num_followers": -1}}
], {allowDiskUse: true})
```
- 2 - Koji su umetnici sa najviše eksplicitnih pesama?\
Time: `133.05s`
```js
db.r_track_artist.createIndex({"artist_id": 1})
db.tracks.createIndex({"id": 1})

db.r_track_artist.dropIndex({"artist_id": 1})
db.tracks.dropIndex({"id": 1})

db.artists.aggregate([
    {$limit: 100},
    // Show only name and id for $lookup
    {$project: {"name": 1, "id": 1}},
    // Adding tracks to artists (as an array)
    {$lookup: {
        from: 'r_track_artist', 
        localField: 'id', 
        foreignField: 'artist_id', 
        pipeline: [
            {$project: {"_id": 0, "track_id": 1}}
        ], 
        as: 'tracks'}},
    // Adding track info for every track (as an array)
    {$lookup: {
        from: 'tracks', 
        localField: 'tracks.track_id', 
        foreignField: 'id', 
        pipeline: [
            {$project: {"_id": 0, "explicit": 1, "name": 1}}
        ],
        as: 'tracks_info'}},
    {$unwind: "$tracks_info"}, // Split an artist with many tracks_infos into many of the same artist with 1 tracks_info, in order to group and sum
    {$group: {_id: "$name", num_explicits: {$sum: "$tracks_info.explicit"}}},
    {$sort: {"num_explicits": -1}}
], {allowDiskUse: true})
```
- 3 - Pesme kojeg izvođača su u proseku najviše "danceable"?
Time: `126s`
```js
db.audio_features.createIndex({"id": 1})
db.r_track_artist.createIndex({"track_id": 1})
db.artists.createIndex({"id": 1})

db.audio_features.dropIndex({"id": 1})
db.r_track_artist.dropIndex({"track_id": 1})
db.artists.dropIndex({"id": 1})

db.tracks.aggregate([
    {$limit: 100},
    // Adding artists to album (as an array)
    {$lookup: {
        from: 'audio_features',
        localField: 'id', 
        foreignField: 'id', 
        pipeline: [
            {$project: {"_id": 0, "danceability": 1}}
        ],
        as: 'features'}},
    {$unwind: "$features"}, // Split an album with many artists into many of the same album with 1 artist, in order to lookup by artist_id
    // Adding genres to album (as an array)
    {$lookup: {
        from: 'r_track_artist', 
        localField: 'id', 
        foreignField: 'track_id', 
//         pipeline: [
//             {$project: {"_id": 0, "track_id": 1}}
//         ], 
        as: 'artists'}},
    {$unwind: "$artists"}, // Split an album with many genres into many of the same album with 1 genre, in order to group and max
    {$group: {_id: {artist_id: "$artists.artist_id"}, avg_danceability: {$avg: "$features.danceability"}}},
    {$lookup: {
        from: 'artists', 
        localField: '_id.artist_id', 
        foreignField: 'id', 
        pipeline: [
            {$project: {"_id": 0, "name": 1}}
        ], 
        as: 'artist_name'}},
    {$sort: {"avg_danceability": -1}}
], {allowDiskUse: true})
```
- 4 - Koji albumi u proseku imaju najduže pesme?\
Time: `782s`
```js
db.r_albums_tracks.createIndex({"album_id": 1})
db.tracks.createIndex({"id": 1})

db.r_albums_tracks.dropIndex({"album_id": 1})
db.tracks.dropIndex({"id": 1})

db.albums.aggregate([
    {$limit: 100},
    {$project: {"_id": 0, "id": 1, "name": 1}},
    {$lookup: {
        from: 'r_albums_tracks',
        localField: 'id', 
        foreignField: 'album_id', 
        pipeline: [
            {$project: {"_id": 0, "track_id": 1}}
        ],
        as: 'tracks'}},
    {$unwind: "$tracks"},
    {$lookup: {
        from: 'tracks', 
        localField: 'tracks.track_id', 
        foreignField: 'id', 
        pipeline: [
            {$project: {"_id": 0, "duration": 1}}
        ], 
        as: 'track_info'}},
    {$unwind: "$track_info"},
    {$group: {_id: {album_name: "$name"}, avg_track_duration: {$avg: "$track_info.duration"}}},
    {$sort: {"avg_track_duration": -1}},
], {allowDiskUse: true})
```

- 5 - Odrediti albume sa najenergičnijim pesmama.\
Time: `769s`
```js
// db.r_albums_tracks.createIndex({"album_id": 1})
// db.audio_features.createIndex({"id": 1})

db.r_albums_tracks.dropIndex({"album_id": 1})
db.audio_features.dropIndex({"id": 1})

db.albums.aggregate([
    {$limit: 100},
    {$project: {"_id": 0, "id": 1, "name": 1}},
    {$lookup: {
        from: 'r_albums_tracks',
        localField: 'id', 
        foreignField: 'album_id', 
//         pipeline: [
//             {$project: {"_id": 0, "track_id": 1}}
//         ],
        as: 'tracks'}},
    {$unwind: "$tracks"},
    {$lookup: {
        from: 'audio_features', 
        localField: 'tracks.track_id', 
        foreignField: 'id', 
//         pipeline: [
//             {$project: {"_id": 0, "duration": 1}}
//         ], 
        as: 'features'}},
    {$unwind: "$features"},
    {$group: {_id: {album_name: "$name"}, avg_energy: {$avg: "$features.energy"}}},
    {$sort: {"avg_energy": -1}},
], {allowDiskUse: true})
```

## Optimizacije Šeme Baze Podataka

Za optimizaciju šeme baze podataka smo koristili šablon proširene reference,\
da bi u što većoj meri izbegli spajanje, i da bi u dokumentima imali već spremne relevantne podatke.

Pošto su žanrovi direktno povezani samo sa izvođačima, možemo ukloniti tabele `r_artist_genre` i `genres`, i relevantne podatke ubaciti u kolekciju `artists`.

```js
db.r_artist_genre.createIndex({"artist_id": 1})

db.artists.aggregate([
	{$lookup: {
		from: 'r_artist_genre',
		localField: 'id',
		foreignField: 'artist_id',
		pipeline: [
			{$project: {"_id": 0, "artist_id": 0}}
		],
		as: 'genres'}},
	{$out: "artists2"}
], {allowDiskUse: true})
```

Na sličan način su povezane i pesme sa njihovim atributima, pa možemo ukloniti kolekciju `audio_features`, i ubaciti relevantne podatke u kolekciju `tracks`.

```js
db.audio_features.createIndex({"id": 1})
db.r_track_artist.createIndex({"track_id": 1})

db.tracks.aggregate([
	{$lookup: {
		from: 'audio_features',
		localField: 'id',
		foreignField: 'id',
		pipeline: [
			{$project: {"_id": 0, "id": 0, "instrumentalness": 0, "key": 0, "mode": 0, "speechiness": 0, "tempo": 0, "time_signature": 0, "valence": 0}}
		],
		as: 'audio_features'}},
    {$unwind: "$audio_features"}, // To convert from array to object
	{$lookup: {
		from: 'r_track_artist',
		localField: 'id',
		foreignField: 'track_id',
		pipeline: [
			{$project: {"_id": 0, "track_id": 0}}
		],
		as: 'artists'}},
	{$out: "tracks2"}
], {allowDiskUse: true})
```

Na kraju, da bi uklonili i preostale međutabele, možemo ukloniti kolekcije `r_albums_artists` i `r_albums_tracks`, i ubaciti relevantne podatke u kolekciju `albums`.

```js
db.r_albums_artists.createIndex({"album_id": 1})
db.r_albums_tracks.createIndex({"album_id": 1})

db.albums.aggregate([
	{$lookup: {
		from: 'r_albums_artists',
		localField: 'id',
		foreignField: 'album_id',
		pipeline: [
			{$project: {"_id": 0, "album_id": 0}}
		],
		as: 'artists'}},
        {$lookup: {
		from: 'r_albums_tracks',
		localField: 'id',
		foreignField: 'album_id',
		pipeline: [
			{$project: {"_id": 0, "album_id": 0}}
		],
		as: 'tracks'}}, 
	{$out: "albums2"}
], {allowDiskUse: true})
```

## Optimizacije Upita

Rezultati optimizacije upita su prikazani u sledećem grafiku.

![](/optimizacije.png)

### Đorđe

- 1 :\
Optimizacija bez indeksa - Time: `3.83s`.\
Optimizacija sa indeksima - Time: `0.019s`.
```js
db.artists2.createIndex({"id": 1})

db.artists2.dropIndex({"id": 1})

db.albums2.aggregate([
    {$limit: 100},
    {$match: {"album_type": "album"}},
    {$lookup: {
        from: 'artists2',
        localField: 'artists.artist_id',
        foreignField: 'id', 
        pipeline: [
            {$project: {"_id": 0, "name": 1, "genres": 1}}
        ],
        as: 'artists_and_genres'}},
    {$project: {"artists":0, "tracks": 0, "release_date": 0, "_id": 0}},
    {$unwind: "$artists_and_genres"},
    {$unwind: "$artists_and_genres.genres"},
    {$group: {_id: {most_popular_album: "$name", genre: "$artists_and_genres.genres.genre_id"}, max_popularity: {$max: "$popularity"}}},
    {$sort: {"max_popularity": -1}}
], {allowDiskUse: true})
```
- 2 :\
Optimizacija bez indeksa - Time: `785s`.\
Optimizacija sa indeksima - Time: `0.198s`.
```js
db.tracks2.createIndex({"id": 1})

db.tracks2.dropIndex({"id": 1})

db.albums2.aggregate([
    {$limit: 100},
    {$unwind: "$tracks"},
    {$project: {"_id": 0, "name": 1, "tracks": 1, "release_date": 1}},
    {$lookup: {
        from: 'tracks2',
        localField: 'tracks.track_id', 
        foreignField: 'id', 
        pipeline: [
            {$project: {"_id": 0, "name": 1, "audio_features": 1}}
        ],
        as: 'tracks-info'}},
    {$project: {"tracks": 0}},
    {$match: {"tracks-info.audio_features.acousticness": {$gt: 0.5}}},
    {$group: {_id: {album_name: "$name", release_date: "$release_date"}, num_acoustic_tracks: {$sum: 1}}},
    {$sort: {"num_acoustic_tracks": -1}},
], {allowDiskUse: true})
```

- 3 :\
Optimizacija bez indeksa - Time: `6.557s`.\
Optimizacija sa indeksima - Time: `0.010s`.

```js
db.artists2.createIndex({"id": 1})

db.artists2.dropIndex({"id": 1})

db.tracks2.aggregate([
    {$limit: 100},
    {$unwind: "$artists"},
    {
        $lookup: {
			from: 'artists2',
			localField: 'artists.artist_id',
			foreignField: 'id',
			as: 'artists_info',
			pipeline: [
                {$project: {"_id": 0, "name": 1}}
            ], 
        }
    },
    {$unwind: "$artists_info"}, // Split a track with many artists into many of the same track with 1 artist
    {$group: {_id: "$artists_info.name", avg_loudness: {$avg: "$audio_features.loudness"}}},
    {$sort: {"avg_loudness": -1}}
], {allowDiskUse: true})
```

- 4 :\
Optimizacija bez indeksa - Time: `2.540s`.\
Optimizacija sa indeksima - Time: `0.003s`.

```js
db.tracks2.createIndex({"artists.artist_id": 1})

db.tracks2.dropIndex({"artists.artist_id": 1})

db.artists2.aggregate([
    { $limit: 100 },
    {$unwind: "$genres"},
    {$match: {"genres.genre_id": "rap"}},
    {$lookup: {
        from: 'tracks2', 
        localField: 'id', 
        foreignField: 'artists.artist_id', 
        pipeline: [
            {$project: {"_id": 0, "id": 1}}
        ], 
        as: 'tracks'}},
    {$unwind: "$tracks"},
    {$group: {_id: {name: "$name", genre: "$genres.genre_id"}, num_songs: {$sum: 1}}},
    {$sort: {"num_songs": -1}}
], {allowDiskUse: true})
```

- 5 :\
Optimizacija bez indeksa - Time: `98.8s`.\
Optimizacija sa indeksima - Time: `0.127s`.

```js
db.tracks2.createIndex({"artists.artist_id": 1})

db.tracks2.dropIndex({"artists.artist_id": 1})

db.artists2.aggregate([
    {$limit: 100}, // Change over to 10 for testing
    {$project: {"_id": 0, "genres": 0}},
    {$lookup: {
        from: 'tracks2', 
        localField: 'id', 
        foreignField: 'artists.artist_id', 
        pipeline: [
            {$project: {"_id": 0, "audio_features.liveness": 1}}
        ], 
        as: 'tracks'}},
    {$unwind: "$tracks"},
    {$match: {"tracks.audio_features.liveness": {$gt: 0.5}}},
    {$group: {_id: {artist_name: "$name"}, num_live_songs: {$sum: 1}}},
    {$sort: {"num_live_songs": -1}},
], {allowDiskUse: true})
```

### Jaki

- 1 :\
Optimizacija bez indeksa - Time: `0.03s`.\
Optimizacija sa indeksima - Time: `0.03s`.
``` js
db.artists2.aggregate([
    {$limit: 100},
    {$unwind: "$genres"}, // Split an artist with many genres into many of the same artist with 1 genre
    {$group: {_id: "$genres.genre_id", num_followers: {$sum: "$followers"}}},
    {$sort: {"num_followers": -1}}
], {allowDiskUse: true})
```

- 2 :\
Optimizacija bez indeksa - Time: `96.2s`.\
Optimizacija sa indeksima - Time: `0.097s`.
```js
db.tracks2.createIndex({"artists.artist_id": 1})

db.tracks2.dropIndex({"artists.artist_id": 1})

db.artists2.aggregate([
    {$limit: 100},
    {$lookup: {
        from: 'tracks2', 
        localField: 'id', 
        foreignField: 'artists.artist_id', 
        pipeline: [
            {$project: {"_id": 0, "explicit": 1}}
        ], 
        as: 'tracks'}},
    {$project: {"_id": 0, "name": 1, "tracks": 1}},
    {$unwind: "$tracks"},
    {$group: {_id: "$name", num_explicits: {$sum: "$tracks.explicit"}}},
    {$sort: {"num_explicits": -1}}
], {allowDiskUse: true})
```

- 3 :\
Optimizacija bez indeksa - Time: `7.92s`.\
Optimizacija sa indeksima - Time: `0.028s`.
```js
db.artists2.createIndex({"id":1})

db.artists2.dropIndex({"id":1})

db.tracks2.aggregate([
    {$limit: 100},
    {
        $lookup: {
            from: 'artists2',
            localField: 'artists.artist_id',
            foreignField: 'id',
            pipeline: [
                {$project: {"_id": 0, "name": 1}}
            ],
            as: 'artists_info'
        }
    },
    {$project: {"_id": 0, "name": 1, "audio_features": 1, "artists_info": 1}},
    {$unwind: "$artists_info"},
    {$group: {_id: {artist_id: "$artists_info.name"}, avg_danceability: {$avg: "$audio_features.danceability"}}},
    {$sort: {"avg_danceability": -1}}
], {allowDiskUse: true})
```
- 4 :\
Optimizacija bez indeksa - Time: `56.3s`.\
Optimizacija sa indeksima - Time: `0.049s`.
```js
db.tracks2.createIndex({"id": 1})

db.tracks2.dropIndex({"id": 1})

db.albums2.aggregate([
    {$limit: 100},
    {$lookup: {
        from: 'tracks2',
        localField: 'tracks.track_id', 
        foreignField: 'id', 
        pipeline: [
            {$project: {"_id": 0, "name": 1, "audio_features": 1}}
        ],
        as: 'tracks'}},
    {$unwind: "$tracks"},    
    {$group: {_id: {album_name: "$name"}, avg_track_duration: {$avg: "$tracks.audio_features.duration"}}},
    {$sort: {"avg_track_duration": -1}},
], {allowDiskUse: true})
```
- 5 :\
Optimizacija bez indeksa - Time: `52.8s`.\
Optimizacija sa indeksima - Time: `0.023s`.
```js
db.tracks2.createIndex({"id": 1})

db.tracks2.dropIndex({"id": 1})

db.albums2.aggregate([
    {$limit: 100},
    {$lookup: {
        from: 'tracks2',
        localField: 'tracks.track_id', 
        foreignField: 'id',
        as: 'tracks'}},
    {$unwind: "$tracks"},
    {$group: {_id: {album_name: "$name"}, avg_energy: {$avg: "$tracks.audio_features.energy"}}},
    {$sort: {"avg_energy": -1}},
], {allowDiskUse: true})
```
