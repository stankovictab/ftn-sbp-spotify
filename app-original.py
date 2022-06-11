from pymongo import mongo_client
import csv

client = mongo_client.MongoClient("mongodb://localhost:27017/", username="root", password="example")
db = client["spotify"] # Creating db in mongo


# Inserting audio features into tracks collection
# You can't place {tableName}.{columnName} in these queries, needs to be just {columnName}
# TODO: Need to print() to see the result
# TODO: These changes don't persist in the database
client['spotify']['tracks'].aggregate([
    {
        '$lookup':
		{
			'from': 'audio_features',
			'localField': 'audio_feature_id',
			'foreignField': 'id',
			'as': 'audio_features'
		}
    }
])

print(db["albums"].find_one())