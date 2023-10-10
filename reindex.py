# reindex.py
import os
import json
import requests
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes.models import SearchIndexer,IndexingParameters,SearchIndexerDataSourceConnection,SearchIndex,SimpleField,SearchFieldDataType, SearchableField, CorsOptions,BM25SimilarityAlgorithm
import azure.search.documents.indexes.models as models
import os
from dotenv import load_dotenv
load_dotenv()

index_name = os.getenv("index_name")
indexer_name = os.getenv("indexer_name")
data_source_name = os.getenv("data_source_name")


def reindex_azure_search(storage_account_name, storage_account_key, container_name, azure_search_service_name, azure_search_admin_key):
    # Initialize the SearchIndexerClient and SearchIndexClient with the latest API version
    indexer_client = SearchIndexerClient(endpoint=f"https://{azure_search_service_name}.search.windows.net", index_name=index_name, credential=AzureKeyCredential(azure_search_admin_key))
    index_client = SearchIndexClient(endpoint=f"https://{azure_search_service_name}.search.windows.net", index_name=index_name, credential=AzureKeyCredential(azure_search_admin_key))
    # Create or get the Azure Cognitive Search index
    index = create_or_get_azure_search_index(index_client, index_name)
    # Create or get the Azure Cognitive Search data source
    data_source = create_or_get_azure_search_datasource(indexer_client, data_source_name, storage_account_name, storage_account_key, container_name)
    # Create or get the Azure Cognitive Search indexer
    indexer = create_or_get_azure_search_indexer(indexer_client, indexer_name, index.name, data_source_name)
    # Return the indexer object
    return indexer

def create_or_get_azure_search_index(index_client, index_name):

    fields = [SimpleField(name="id", type="Edm.String", key=True),
                SimpleField(
                    name="url",
                    type="Edm.String",
                    searchable=False,
                    filterable=False,
                    retrievable=True,
                    sortable=False,
                    facetable=False,
                ),
                SearchableField(
                    name="text",
                    type="Edm.String",
                    searchable=True,
                    filterable=False,
                    retrievable=True,
                    sortable=False,
                    facetable=False,
                    analyzer="standard.lucene",
                ),
                SearchableField(
                    name="name",
                    type="Edm.String",
                    searchable=True,
                    filterable=False,
                    retrievable=True,
                    sortable=False,
                    facetable=False,
                    
                ),
            ]
    
    cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
    
    similarity = BM25SimilarityAlgorithm()
    # Create a custom scoring profile
    scoring_profile = []
    
    index = SearchIndex(name=index_name, fields=fields, similarity = similarity ,scoring_profiles=scoring_profile,cors_options=cors_options)
    index_client.create_or_update_index(index, allow_index_downtime = True)
    result = index_client.get_index(index_name)
    
    return result

    
def create_or_get_azure_search_datasource(indexer_client, data_source_name, storage_account_name, storage_account_key, container_name):
    # Check if the data source exists
    existing_data_sources = list(indexer_client.get_data_source_connection_names())
    for existing_data_source in existing_data_sources:
        if existing_data_source == data_source_name:
            return indexer_client.get_data_source_connection(data_source_name)
    # Create the data source if it doesn't exist
    connection_string = f"DefaultEndpointsProtocol=https;AccountName={storage_account_name};AccountKey={storage_account_key};EndpointSuffix=core.windows.net"
    container = {"name": container_name}
    data_source = SearchIndexerDataSourceConnection(name=data_source_name, type="azureblob", connection_string=connection_string, container=container)
    indexer_client.create_data_source_connection(data_source)
    return data_source


def create_or_get_azure_search_indexer( indexer_client, indexer_name, index_name, data_source_name):
    # Check if the indexer exists
    field_mappings = [
    {
        "sourceFieldName": "url",  # Source field in your documents
        "targetFieldName": "url",  # Target field in your search index
    },
    {
        "sourceFieldName": "text",  # Source field in your documents
        "targetFieldName": "text",  # Target field in your search index
    },
    {
        "sourceFieldName": "name",  # Source field in your documents
        "targetFieldName": "name",  # Target field in your search index
    }
]
    indexer = SearchIndexer(name=indexer_name, target_index_name=index_name, data_source_name=data_source_name)
    # Define the indexer's parameters for incremental indexing
    indexer.parameters = IndexingParameters(configuration={"dataToExtract": "contentAndMetadata","parsingMode":"json"})
    indexer.field_mappings=field_mappings
    
    indexer_client.create_or_update_indexer(indexer)
    indexer_client.run_indexer(indexer_name)
    # Return a success message
    return f'Indexer {indexer_name} has started indexing documents.'

