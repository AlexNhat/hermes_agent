import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
print("API Key:", api_key)
print("Current Working Directory:", os.getcwd())
print("ENV exists?", os.path.exists(".env"))
