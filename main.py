from fastapi import FastAPI,Request
import process_documents as pd
import upload_json_to_blob as upload
import querying_index as qi
import os
from dotenv import load_dotenv
import json
import reindex
# Load environment variables from the .env file
load_dotenv()
app = FastAPI()

endpoint = os.getenv("OPENAI_ENDPOINT")
api_key = os.getenv("OPENAI_APIKEY")
storage_account_name = os.getenv("storage_account_name")
storage_account_key = os.getenv("storage_account_key")
container_name = os.getenv("container_name")
azure_search_service_name = os.getenv("azure_search_service_name")
azure_search_admin_key = os.getenv("azure_search_admin_key")
index_name = os.getenv("index_name")
azure_search_endpoint = os.getenv("azure_search_endpoint")


# Define a route that accepts POST requests
@app.post("/{name}")
async def upload_info_search(request:Request, name: str):
    
    # Call the function to process the document
    
    request_body = await request.body()
    request_body = json.loads(request_body)
    
    url = request_body["url"]
    
    file_name,file_path= pd.process_document(url, name,endpoint, api_key)
    
    # Call the function to upload the JSON file to Azure Blob Storage

    upload.upload_json_to_blob_storage(storage_account_name, storage_account_key, container_name, file_name, file_path)

        
    message = reindex.reindex_azure_search(storage_account_name, storage_account_key, container_name, azure_search_service_name, azure_search_admin_key)

    return message
    
# Define another route that takes a path parameter
@app.get("/query")
async def query_doc(request:Request):
    request_body = await request.body()
    request_body = json.loads(request_body)
    
    query = request_body["query"]
    
    results = qi.query_index(index_name,azure_search_endpoint,azure_search_admin_key,query)
    
    return results



if __name__ == "__main__":
    import uvicorn

    # Use Uvicorn to run the FastAPI application
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    
    
    
    
    
    
