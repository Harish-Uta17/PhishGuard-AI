
import os

from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient


load_dotenv()

uri = os.getenv("MONGO_DB_URL")
if not uri:
    raise RuntimeError("MONGO_DB_URL is not set. Add it to your local .env file.")

client = MongoClient(uri)

try:
    client.admin.command("ping")
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as exc:
    print(exc)
