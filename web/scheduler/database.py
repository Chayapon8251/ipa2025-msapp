import os
from pymongo import MongoClient

def get_router_info():
    """
    Connects to MongoDB, retrieves router information, and returns the data.
    """
    mongo_uri = os.environ.get("MONGO_URI")
    db_name = os.environ.get("DB_NAME")

    # This is a good practice to handle cases where environment variables are not set.
    if not mongo_uri or not db_name:
        print("Error: MONGO_URI or DB_NAME environment variable is not set.")
        return []

    try:
        client = MongoClient(mongo_uri)
        db = client[db_name]
        routers = db["routers"]
        
        router_data = list(routers.find()) # Converts cursor to a list
        print(router_data)
        return router_data
    except Exception as e:
        print(f"An error occurred while connecting to MongoDB: {e}")
        return []

if __name__ == '__main__':
    # This is a good way to test your function independently.
    for router in get_router_info():
        print(router)
