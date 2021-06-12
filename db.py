from pymongo import MongoClient

class mongodb:
	cluster = MongoClient("mongodb+srv://yonghee:dydgml2514@cluster0.zer9c.mongodb.net/software_engineering?retryWrites=true&w=majority")
	db = cluster["software_engineering"]
	diaries = db["diaries"]
	users = db["users"]
