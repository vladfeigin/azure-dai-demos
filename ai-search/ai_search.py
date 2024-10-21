import os

#loading environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_openai import AzureOpenAIEmbeddings

from azure.search.documents.indexes.models import (
    ScoringProfile,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    TextWeights,
)

# This module is responsible for integration with Azure Search and uses Langchain framework for this
# It contains following functions:
# search - search for similar documents in Azure Search. return top 5 results
# ingest - gets as parameters a list of documents(chunks) and metadata per document and ingests them into Azure Search

# Azure Search configuration
AZURE_SEARCH_SERVICE_ENDPOINT = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")  
AZURE_SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")    
AZURE_SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME")

# Azure OpenAI configuration
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")        
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")        
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")


# initialize AzureOpenAIEmbeddings 
embeddings: AzureOpenAIEmbeddings = \
    AzureOpenAIEmbeddings(azure_deployment=AZURE_OPENAI_DEPLOYMENT,
                          openai_api_version=AZURE_OPENAI_API_VERSION, 
                          azure_endpoint=AZURE_OPENAI_ENDPOINT,
                          api_key=AZURE_OPENAI_KEY)
    
#define search index custom schema
fields = [
    SimpleField(
        name="chunk_id",
        type=SearchFieldDataType.String,
        key=True,
        filterable=True,
    ),
     SimpleField(
        name="parent_id",
        type=SearchFieldDataType.String,
        key=True,
        filterable=True,
    ),
    SearchableField(
        name="chunk",
        type=SearchFieldDataType.String,
        searchable=True,
    ),
    SearchField(
        name="text_vector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        vector_search_dimensions=len(embeddings.embed_query("Text")),
        vector_search_profile_name="myHnswProfile",
    ),
    # Additional field to store the title
    SearchableField(
        name="title",
        type=SearchFieldDataType.String,
        searchable=True,
    ),
]

#create Langchain AzureSearch object
vector_search: AzureSearch = \
    AzureSearch(azure_search_endpoint=AZURE_SEARCH_SERVICE_ENDPOINT,
                                            azure_search_key=AZURE_SEARCH_API_KEY,
                                            index_name=AZURE_SEARCH_INDEX_NAME,
                                            embedding_function=embeddings.embed_query,
    # Configure max retries for the Azure client
    additional_search_client_options={"retry_total": 3},
    fields=fields,
)

# ingest - gets as parameters a list of documents(chunks) and metadata per document and ingests them into Azure Search
#TODO - implement async version of ingest
def ingest(documents: list, metadata):
    #check the input is valid list and non empty if not return exception
    if not isinstance(documents, list) or not documents:
        raise ValueError("Input must be a non-empty list")
    if not isinstance(metadata, list) or not metadata:
        raise ValueError("Metadata must be a non-empty list")
    if len(documents) != len(metadata):
        raise ValueError("Documents and metadata must be of the same length")
    
    # Ingest documents into Azure Search
    vector_search.add_documents(documents, metadata)


# search - search for similar documents in Azure Search. return top 5 results
def search(query: str, search_type='similarity', top_k=5):
    #check the input is valid string and non empty if not raise exception
    if not isinstance(query, str) or not query:
        raise ValueError("Search query must be a non-empty string")
    # Search for similar documents
    docs = vector_search.similarity_search(query=query, k=top_k, search_type=search_type)
    return docs[0].page_content  


#docs = search("Waht is Microsoft's Fabric?", search_type='hybrid', top_k=5)

