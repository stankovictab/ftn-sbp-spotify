# ftn-sbp-spotify
[Sistemi Baza Podataka] - Predmetni Projekat - Optimizacija Dokument Orijentisane NoSQL baze podataka.

## Setup

```shell
pip install pymongo
pip install pandas
```

> Ne koristimo $merge i $out, radimo sve sa $lookup u query-u.

> Kazemo da radimo sa limitom jer nemamo vremena da cekamo 144h

> imamo puno lookup-a jer merge ili out je nemoguce

> lookup uvek vraca niz i uvek vraca sve elemente, ne moze da se filtrira izgleda

> Mozemo limit na 100, sve tako da posmatramo, jer limit raste linearno uvek

> Optimizacija ce nam biti da (posto ne mozemo da radimo out i merge) da preko pythona napravimo bolju bazu, da dokumenti imaju relevantne podatke u njima, da smanjimo, ili potpuno eliminisemo lookup-e

> $project je kao filter u find()-u, znaci 1 ili 0, sta zelimo da se prikaze nakon tog nekog aggregation stage-a

> U pipeline unutar $lookup-a mozemo da radimo project da selektujemo iz lookup-a sta zelimo, da ne uzimamo sve

> $match je kao uslov, uglavnom se stavlja medju prvim stage-evima, mozda se smatra kao neka optimizacija

> Dobar primer za optimizaciju je da se za Jakijev 2. umesto 2 lookup-a radi 1 za pesme, i da se sa njima povlace i informacije o pesmi (da ne koristimo medjutabelu)

> Dok radimo ovaj development mozemo da koristimo indekse za brzi rad, zapravo trebali bi uvek da ih koristimo, ali za odbranu necemo da bi prikazali bolju optimizaciju. Pravimo ih nad svim tabelama sa kojima radimo upit, nad poljima koje referenciramo za, na primer, foreignFeild. Bitno sad, kada gledamo koliko upitu zapravo treba da se izvrsi, treba da izbrisemo sve indekse iz baze, i da pokrenemo ponovo. Kada imas vise upita u shell-u on ih sve pokrene, a rezultati su u tabovima.
```
db.getCollection('r_artist_genre').createIndex({"artist_id": 1})
db.getCollection('r_track_artist').createIndex({"artist_id": 1})
```

> $limit uvek uzima tih istih prvih n torki

> TODO: Pokreni svaki query ponovo i proveri da li je dobro

## Queries - Before Optimizations (TODO: ?)

### Djordje
- 1 - Koji su najpopularniji albumi po zanrovima?\
Time: 8.56s
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
// db.r_albums_tracks.createIndex({"album_id": 1})
// db.audio_features.createIndex({"id": 1})

// db.r_albums_tracks.dropIndex({"album_id": 1})
// db.audio_features.dropIndex({"id": 1})

db.albums.aggregate([
    {$limit: 100},
    // Adding artists to album (as an array)
    {$project: {"_id": 0, "id": 1, "name": 1, "release_date": 1}},
    {$lookup: {
        from: 'r_albums_tracks',
        localField: 'id', 
        foreignField: 'album_id', 
        pipeline: [
            {$project: {"_id": 0, "track_id": 1}}
        ],
        as: 'tracks'}},
    {$unwind: "$tracks"}, // Split an album with many artists into many of the same album with 1 artist, in order to lookup by artist_id
    // Adding genres to album (as an array)
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
Time: `?s`
```js
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
    {$sort: {"avg_loudness": 1}}
], {allowDiskUse: true})
```
- 4 - Koji umetnici su izbacili najviše pesama iz žanra 'rap'?\
Time: `?s`
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
Time: `?s`
```js
// db.r_track_artist.createIndex({"artist_id": 1})
// db.audio_features.createIndex({"id": 1})

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
// db.audio_features.createIndex({"id": 1})
// db.r_track_artist.createIndex({"track_id": 1})
// db.artists.createIndex({"id": 1})

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
    // ...
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
Time: `?s`
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
//     {$match: {"features.liveness": {$gt: 0.5}}},
    {$group: {_id: {album_name: "$name"}, avg_energy: {$avg: "$features.energy"}}},
    {$sort: {"avg_energy": -1}},
], {allowDiskUse: true})
```