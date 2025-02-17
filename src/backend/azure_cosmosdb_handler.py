import os
from azure.identity import DefaultAzureCredential
from azure.cosmos import CosmosClient, exceptions, PartitionKey

import logging
logger = logging.getLogger(__name__)

DATABASE_NAME = 'zdjecia'
COSMOSDB_URL = "https://deployplikow.redstone-6bf9eab7.westus2.azurecontainerapps.io"

class AzureCosmosDBHandler():
    """
    Class to handle all the blob operations
    """

    def __init__(self, container_name: str = "metadata", prefix: str = "tests/"):
        """
        Initialize the class with the container name
        :param container_name: The name of the container
        """
        self.container_name = container_name
        self.prefix = prefix
        if conn_str := os.getenv("COSMOS_DB_KEY"):
            self.client = CosmosClient.from_connection_string(conn_str)
        else:
            default_credential = DefaultAzureCredential()
            self.client = CosmosClient(url = 
                                       container_name=container_name,
                                             
                                        credential=default_credential)
        try:
            self.database = self.client.create_database(DATABASE_NAME)
        except exceptions.CosmosResourceExistsError:
            self.database = self.client.get_database_client(DATABASE_NAME)

        try:
            self.container = self.database.create_container(id=self.container_name, partition_key=PartitionKey(path="/userId"))
        except exceptions.CosmosResourceExistsError:
            self.container = self.database.get_container_client(self.container_name)
        
        print("Container created")
        
    def upload_document(self, document: dict):
        """
        Upload a document to the container
        :param document: The document to upload
        """
        return self.container.upsert_item(document)
