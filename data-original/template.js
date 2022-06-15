//Logicka sema podataka pre optimizacije

audio_feature = {
	"id": "2jKoVlU7VAmExKJ1Jh3w9P",
	"acousticness": 0.1800000071525573,
	"danceability": 0.8930000066757202,
	"duration": 219160,
	"energy": 0.5139999985694885,
	"instrumentalness": 0.0,
	"key": 11,
	"liveness": 0.0595999993383884,
	"loudness": -5.079999923706055,
	"mode": 1,
	"speechiness": 0.2829999923706054,
	"tempo": 95.8479995727539,
	"time_signature": 4,
	"valence": 0.7870000004768372
};

// id,disc_number,duration,explicit,audio_feature_id,name,preview_url,track_number,popularity,is_playable
// 1dizvxctg9dHEyaYTFufVi,1,275893,1,1dizvxctg9dHEyaYTFufVi,Gz And Hustlas (feat. Nancy Fletcher),,12,0,

track = {
	"id": "1dizvxctg9dHEyaYTFufVi",
	"disc_number": 1,
	"duration": 275893,
	"explicit": 1,
	"audio_feature_id": "1dizvxctg9dHEyaYTFufVi",
	"name": "Gz And Hustlas (feat. Nancy Fletcher)",
	"preview_url": "",
	"track_number": 12,
	"popularity": 0,
	"is_playable": ""
};

// r_track_artist
// track_id,artist_id
// 2jKoVlU7VAmExKJ1Jh3w9P,4tujQJicOnuZRLiBFdp3Ou

r_track_artist = {
	"track_id": "2jKoVlU7VAmExKJ1Jh3w9P",
	"artist_id": "4tujQJicOnuZRLiBFdp3Ou"
};

// r_artist_genre
// genre_id,artist_id
// detroit hip hop,4tujQJicOnuZRLiBFdp3Ou

r_artist_genre = {
	"genre_id": "detroit hip hop",
	"artist_id": "4tujQJicOnuZRLiBFdp3Ou"
};

// r_albums_tracks
// album_id,track_id
// 6os2Mv58OYnQClPf7B9E1s,3HnrHGLE9u2MjHtdobfWl9

r_albums_tracks = {
	"album_id": "6os2Mv58OYnQClPf7B9E1s",
	"track_id": "3HnrHGLE9u2MjHtdobfWl9"
};

// r_albums_artist
// album_id,artist_id
// 6os2Mv58OYnQClPf7B9E1s,2HS2wQTJXpA65XWOKlAVxk

r_albums_artist = {
	"album_id": "6os2Mv58OYnQClPf7B9E1s",
	"artist_id": "2HS2wQTJXpA65XWOKlAVxk"
};

// genres
// id
// detroit hip hop

genre = {
	"id": "detroit hip hop"
};

// artists
// name,id,popularity,followers
// Xzibit,4tujQJicOnuZRLiBFdp3Ou,69,1193665

artist = {
	"name": "Xzibit",
	"id": "4tujQJicOnuZRLiBFdp3Ou",
	"popularity": 69,
	"followers": 1193665
};

// albums
// id,name,album_group,album_type,release_date,popularity
// 2jKoVlU7VAmExKJ1Jh3w9P,"Alkaholik (feat. Erik Sermon, J Ro & Tash)",,album,954633600000,0

album = {
	"id": "2jKoVlU7VAmExKJ1Jh3w9P",
	"name": "Alkaholik (feat. Erik Sermon, J Ro & Tash)",
	"album_group": "",
	"album_type": "album",
	"release_date": "954633600000",
	"popularity": 0
};



//Logicka sema podataka nakon optimizacije

albums2 = { 
    "_id" : ObjectId("62a8845f88d8c70df07b6222"), 
    "id" : "4EFG9ipPg0h2Yi7vg0Ople", 
    "name" : "To You, In 2000 Years", 
    "album_type" : "single", 
    "release_date" : NumberLong(1601856000000), 
    "popularity" : NumberInt(12), 
    "artists" : [
        {
            "artist_id" : "4IF11U0nzFhAaLDGZH3vSx"
        }
    ], 
    "tracks" : [
        {
            "track_id" : "6xv32JCDpIom7AIIrJzRkJ"
        }
    ]
}


artists2 = { 
    "_id" : ObjectId("62a8846888d8c70df07d8bbe"), 
    "name" : "Eminem", 
    "id" : "7dGJo4pcD2V6oG8kP0tJRR", 
    "popularity" : NumberInt(94), 
    "followers" : NumberInt(43882754), 
    "genres" : [
        {
            "genre_id" : "detroit hip hop"
        }, 
        {
            "genre_id" : "hip hop"
        }, 
        {
            "genre_id" : "rap"
        }
    ]
}


track2 = { 
    "_id" : ObjectId("62a8862188d8c70df0b53d4a"), 
    "id" : "2bNYgVK6yXzAuFD6uMWKsv", 
    "duration" : NumberInt(151097), 
    "explicit" : NumberInt(0), 
    "name" : "Snow Keeps Falling", 
    "popularity" : NumberInt(54), 
    "audio_features" : {
        "acousticness" : 0.922, 
        "danceability" : 0.585, 
        "duration" : NumberInt(151097), 
        "energy" : 0.0359, 
        "liveness" : 0.115, 
        "loudness" : -22.913
    }, 
    "artists" : [
        {
            "artist_id" : "7EyQn2KSLStE6tXcdpDOXm"
        }
    ]
}


audio_features = { 
    "_id" : ObjectId("62a8850d88d8c70df07fa6c8"), 
    "id" : "4Bv9PjhIhp2sQE4S7dEAxR", 
    "acousticness" : 0.775, 
    "danceability" : 0.279, 
    "duration" : NumberInt(157500), 
    "energy" : 0.0331, 
    "instrumentalness" : 0.0086, 
    "key" : NumberInt(0), 
    "liveness" : 0.0938, 
    "loudness" : -21.254, 
    "mode" : NumberInt(1), 
    "speechiness" : 0.041, 
    "tempo" : 98.321, 
    "time_signature" : NumberInt(4), 
    "valence" : 0.212
}