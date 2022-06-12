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

## Queries - Before Optimizations (TODO: ?)

### Djordje
3. - ?s
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




### Igor

1. - 8.92s
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