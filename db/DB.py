from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

ATLAS_URL = "mongodb+srv://tomasvarasoviedo:poker-simulation@poker-cluster.btm3i80.mongodb.net/?retryWrites=true&w=majority&appName=Poker-cluster"
DB_NAME = "Poker-db"


class DBConnect ():
    def __init__(self, atlas_url, dbname):
        """
        Args:
            atlas_url [str]: Atlas url for connect
            dbname [str]: DataBase name in Atlas
        """
        self.mongodb_client = MongoClient(atlas_url, server_api=ServerApi('1'))
        self.database = self.mongodb_client[dbname]

    def ping(self):
        self.mongodb_client.admin.command('ping')

    def get_collection(self, collection_name: str):
        """
        Method for get the collection on the database

        Args:
            collection name [str]: Collection that need to find on the database

        Returns:
            colection [Colleccion]: Collection on the database

        """
        if collection_name == "" or collection_name is None:
            raise ValueError("Collection name is empty or None")

        collection = self.database[collection_name]
        return collection

    def create_collection(self, collection_name: str):
        """
        Method for create collection on the database

        Args:
            collection_name [str]: Collection name

        """
        return self.database.create_collection(collection_name)

    def add_data_collection(self, collection_name: str, data: dict) -> bool:
        """
        Method for add data on the colection

        Args:
            colection_name [str]: colection name on the database
            data [dict]: data for insert on the database

        Returns:
            confirmation [bool]: confirmation
        """
        if not isinstance(data, dict) or len(data) == 0:
            raise ValueError("Data is empty or not a dictionary")

        collection = self.get_collection(collection_name)
        return collection.insert_one(data)

    def add_data_results(self, data: dict) -> bool:
        """
        Method for add data on the colection

        Args:
            data [dict]: data for insert on the database

        Returns:
            result [bool]: confirmation
        """
        if not isinstance(data, dict) or len(data) == 0:
            raise ValueError("Data is empty or not a dictionary")
        collection = self.get_collection("results")
        return collection.insert_one(data)

    def find(self, colection_name: str, filter={}, limit=0):
        """
        Method for find on the database

        Args:
            colection_name [str]: colection name on the database
            filter [dict]: filter for apply
            limit [int]: number registers limit
        Returns:
            data [list]: information result
        """
        collection = self.get_collection(colection_name)
        items = list(collection.find(filter=filter, limit=limit))
        return items

    def delete_document(self, collection_name: str, filter={}):
        """
        Method for delete on the database
        Example the filter: filter = {"name": "tomas"}

        Args:
            colection_name [str]: colection name on the database
            filter [dict]: filter for apply
        Returns:
            data [list]: information result
        """
        collection = self.get_collection(collection_name)
        items = list(collection.delete_many(filter=filter))
        return items
