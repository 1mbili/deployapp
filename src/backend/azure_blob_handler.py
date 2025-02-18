import os
import time
from datetime import datetime, timedelta
from typing import BinaryIO
from azure.storage.blob import ContainerClient, BlobServiceClient, generate_blob_sas, AccountSasPermissions
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
import logging
ACCOUNT_URL  = 'https://projektzdjecia.blob.core.windows.net'
logger = logging.getLogger(__name__)

class AzureBlobHandler():
    """
    Class to handle all the blob operations
    """

    def __init__(self, container_name: str = "zdjecia", prefix: str = "tests/"):
        """
        Initialize the class with the container name
        :param container_name: The name of the container
        """
        self.container_name = container_name
        self.prefix = prefix
        if conn_str := os.getenv("AZURE_STORAGE_CONNECTION_STRING"):
            self.container = ContainerClient.from_connection_string(
                conn_str, container_name)
        else:
            default_credential = ManagedIdentityCredential(client_id="978f1e1d-946a-4fe9-83c7-c9fdd44ee70e")
            self.container = ContainerClient(account_url=ACCOUNT_URL, container_name=container_name,
                                             credential=default_credential)

    def list_blobs(self, dir: str = ""):
        """
        List all the blobs in the container
        :param prefix: The prefix to filter the blobs
        :param dir: The directory to filter the blobs
        :return: A list of blobs
        """
        blob_list = self.container.list_blobs(name_starts_with=self.prefix+dir)
        return blob_list

    def upload_blob(self, blob_name: str, file: BinaryIO):
        """
        Upload a blob to the container
        :param blob_name: The name of the blob
        :param file_path: The path of the file to upload
        """
        return self.container.upload_blob(name=self.prefix+blob_name, data=file, overwrite=True)

    def upload_from_url(self, blob_name: str, url: str):
        """
        Upload a blob to the container
        :param blob_name: The name of the blob
        :param url: The url of the file to upload
        """
        block_blob_service = BlobServiceClient.from_connection_string(
            CONNECTION_STRING)
        copied_blob = block_blob_service.get_blob_client(
            self.container_name, blob_name)
        copied_blob.start_copy_from_url(url)
        for _ in range(10):
            props = copied_blob.get_blob_properties()
            status = props.copy.status
            print("Copy status: " + status)
            if status == "success":
                # Copy finished
                break
            time.sleep(3)

        if status != "success":
            # if not finished after 30s, cancel the operation
            props = copied_blob.get_blob_properties()
            print(props.copy.status)
            copy_id = props.copy.id
            copied_blob.abort_copy(copy_id)
            props = copied_blob.get_blob_properties()
            print(props.copy.status)
        return copied_blob

    def download_blob(self, blob_name: str):
        """
        Download a blob from the container
        :param blob_name: The name of the blob
        :return: The blob
        """
        blob = self.container.download_blob(
            self.prefix+blob_name).content_as_bytes()
        return blob

    def delete_blob(self, blob_name: str):
        """
        Delete a blob from the container
        :param blob_name: The name of the blob
        """
        return self.container.delete_blob(self.prefix+blob_name)

    def generate_blob_sas(self, blob_name: str):
        """
        Generate a blob url
        :param blob_name: The name of the blob
        :return: The url of the blob
        """
        path = self.prefix + blob_name
        block_blob_service = BlobServiceClient.from_connection_string(
            CONNECTION_STRING)
        sas_uri = generate_blob_sas(
            account_name=block_blob_service.account_name,
            account_key=block_blob_service.credential.account_key,
            container_name=self.container_name,
            blob_name=path,
            permission=AccountSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(minutes=15)
        )
        blob_url = 'https://' + BLOB_ACC_NAME + '.blob.core.windows.net/' + \
            self.container_name + '/' + path + '?' + sas_uri
        return blob_url