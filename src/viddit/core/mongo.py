import logging
import time
from typing import Dict, List

import pymongo

logger = logging.getLogger(__name__)


class MongoDBClient:
    """
    A class that provides a simple interface for performing common operations with MongoDB using the PyMongo library.
    This is a standard interface that can be used to implement any sort of database functionality.
    """

    def __init__(self, host: str, port: int, database: str = "Viddit"):
        """
        Initialize the MongoDB instance.

        Parameters:
        - host: the hostname or IP address of the MongoDB instance
        - port: the port number of the MongoDB instance
        - database: the name of the database to use
        """
        self.client = pymongo.MongoClient(host, port)
        self.db = self.client[database]

    def create_collection(self, collection_name: str, validator_schema: Dict = None):
        """
        Create a new collection.

        Parameters:
        - collection_name: the name of the collection to create
        - validators: a list of document validation rules to apply to the collection (optional)
        """
        try:
            self.db.create_collection(collection_name)
        except pymongo.errors.CollectionInvalid:
            logger.warning(f"Collection {collection_name} already exists.")
        if validator_schema:
            self.configure_validation(collection_name, validator_schema)

    def get_all_collection_names(self):
        """Get all collection names in the database."""
        return self.db.list_collection_names()

    def drop_collection(self, collection_name: str):
        """
        Drop (delete) a collection.

        Parameters:
        - collection_name: the name of the collection to drop
        """
        self.db.drop_collection(collection_name)

    def configure_validation(self, collection: str, validator: Dict):
        """
        Configure document validation rules for a collection.

        """
        try:
            self.db.command("collMod", collection, validator={"$jsonSchema": validator})
        except pymongo.errors.OperationFailure:
            logger.warning(f"Validation rule already exists for collection {collection}.")

    def insert_one(self, collection: str, document: Dict):
        """
        Insert a single document into a collection.

        Parameters:
        - collection: the name of the collection
        - document: the document to insert
        """
        self.db[collection].insert_one(document)

    def insert_many(self, collection: str, documents: List[Dict]):
        """Insert multiple documents into a collection.

        Parameters
        ----------
        collection : str
            The name of the collection.
        documents : List[Dict]
            The documents to insert.
        """
        self.db[collection].insert_many(documents)

    def find_one(self, collection: str, query: Dict = {}):
        """Find a single document in a collection.

        Parameters
        ----------
        collection : str
            The name of the collection.
        query : Dict, optional
            The query to use to find the document, by default {}

        Returns
        -------
        _type_
            The document found.
        """
        return self.db[collection].find_one(query)

    def find(self, collection: str, query: Dict = {}):
        """Find multiple documents in a collection.

        Parameters
        ----------
        collection : str
            The name of the collection.
        query : Dict, optional
            The query to use to find the documents, by default {}

        Returns
        -------
        _type_
            The documents found.
        """
        return self.db[collection].find(query)

    def update_one(self, collection: str, query: Dict, update: Dict, upsert: bool = False):
        """Update a single document in a collection.

        Parameters
        ----------
        collection : str
            The name of the collection.
        query : Dict
            The query to use to find the document.
        update : Dict
            The update to apply to the document.
        upsert : bool, optional
            Flag to insert the document if it is not found, by default False
        """
        self.db[collection].update_one(query, update, upsert=upsert)

    def update_many(self, collection: str, query: Dict, update: Dict, upsert: bool = False):
        """Update multiple documents in a collection.

        Parameters
        ----------
        collection : str
            The name of the collection.
        query : Dict
            The query to use to find the documents.
        update : Dict
            The update to apply to the documents.
        upsert : bool, optional
            Flag to insert the documents if they are not found, by default False
        """
        self.db[collection].update_many(query, update, upsert=upsert)

    def delete_one(self, collection, query):
        """Delete a single document from a collection.

        Parameters
        ----------
        collection : _type_
            The name of the collection.
        query : _type_
            The query to use to find the document.
        """
        self.db[collection].delete_one(query)

    def delete_many(self, collection, query):
        """Delete multiple documents from a collection.

        Parameters
        ----------
        collection : _type_
            The name of the collection.
        query : _type_
            The query to use to find the documents.
        """
        self.db[collection].delete_many(query)

    # def backup_db(self):
    #     """Backup the MongoDB instance."""

    #     subprocess.run(["docker", "exec", "mongo", "sh", "-c", "'mongodump", "--archive'", ">", "db.dump"])
    #     logger.info("Database backed up.")


class VidditMongoClient(MongoDBClient):
    def initialise_viddited_table(self):
        """"""
        validator = {
            "bsonType": "object",
            "title": "Viddited Collection Validation",
            "required": ["PostLink"],
            "properties": {
                "PostLink": {
                    "bsonType": "string",
                    "description": "Link to the Post.",
                }
            },
        }
        self.create_collection("Viddited", validator_schema=validator)
        logger.info("Viddited table initialised.")

    def add_viddited(self, post_link: str):
        """Add a viddited post to the database if it doesn't aready exist."""
        if not self.find_one("Viddited", {"PostLink": post_link}):
            self.insert_one("Viddited", {"PostLink": post_link})

    def get_viddited(self, post_link: str):
        """Get a viddited post from the database."""
        return self.find_one("Viddited", {"PostLink": post_link})

    def get_all_viddited(self):
        """Get all viddited posts from the database."""
        return self.find("Viddited")


def initialise_db(
    max_attempts: int = 5, sleep: int = 5
):  # This is called in the main bot file and is the bit of code that connects to the database.
    """Initialise the database."""
    connected = False
    attempts = 0
    while connected == False and attempts < max_attempts:
        logger.info(f"Connecting to database... Attempt {str(attempts+1)} of {max_attempts}")
        db_client = VidditMongoClient(
            host="mongo", port=27017
        )  # It creates a new instance of the CustomMongoDBClient class, which abstracts our database interactions.
        try:
            time.sleep(sleep)
            db_client.client.admin.command("ping")  # This is a test to see if the database is up and running.
            connected = True
        except Exception as e:
            logger.error("Connecting to database...")
            logger.error(e)
            if attempts < max_attempts - 1:
                logger.info("Retrying...")
            else:
                logger.info("Failed to connect to database.")
            attempts += 1
    if connected:
        logger.info("Connected to database.")
        db_client.initialise_viddited_table()  # This makes the table if it doesn't exist and ensures the validation rules.
    return db_client, connected
