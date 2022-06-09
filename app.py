import pymongo
import pandas as pd

client = pymongo.MongoClient("mongodb://localhost:27017/", username="root", password="example")
db = client["spotify"] # Creating db in mongo

print(db["albums"].database.name)