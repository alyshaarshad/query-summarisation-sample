import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient


def query_index(index_name,endpoint,key,query):
# Create a client
    credential = AzureKeyCredential(key)
    client = SearchClient(endpoint=endpoint,
                        index_name=index_name,
                        credential=credential)

    results = client.search(search_text=query)

    for result in results:
        return ("{}: {})".format(result["name"], result["text"]))