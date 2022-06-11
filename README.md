# ftn-sbp-spotify
[Sistemi Baza Podataka] - Predmetni Projekat - Optimizacija Dokument Orijentisane NoSQL baze podataka.

## Setup

```shell
pip install pymongo
pip install pandas
```

## Examples

Inserting audio features into tracks.
```js
db.tracks.aggregate([
    // { $limit: 2 },
    {
        $lookup:
		{
			from: 'audio_features',
			localField: 'audio_feature_id',
			foreignField: 'id',
			as: 'audio_features'
		}
    },
    { $merge: { into: "myOutput" } }
])
```




