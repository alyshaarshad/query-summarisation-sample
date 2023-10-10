from azure.storage.blob import BlobServiceClient, ContainerClient

def upload_json_to_blob_storage(storage_account_name, storage_account_key, container_name, blob_name, local_json_file_path):
    try:
        # Set up your Azure Blob Storage connection
        connection_string = f"DefaultEndpointsProtocol=https;AccountName={storage_account_name};AccountKey={storage_account_key};EndpointSuffix=core.windows.net"
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        # Create a ContainerClient
        container_client = blob_service_client.get_container_client(container_name)

        # Create the container if it doesn't exist
        if not container_client.exists():
            container_client.create_container()

        # Create a BlobClient
        blob_client = container_client.get_blob_client(blob_name)

        # Upload the JSON file to Blob Storage
        with open(local_json_file_path, "rb") as data:
            blob_client.upload_blob(data)

        return True, f"JSON file '{local_json_file_path}' uploaded successfully to Azure Blob Storage in container '{container_name}' as '{blob_name}'."
    except Exception as e:
        return False, str(e)
