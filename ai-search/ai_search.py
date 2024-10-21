import os
import logging
from dotenv import load_dotenv
# Load environment variables from .env file
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

# Configure logging
#logging.basicConfig(level=logging.INFO)

# Azure Search configuration
AZURE_SEARCH_SERVICE_ENDPOINT = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
AZURE_SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
AZURE_SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME")

# Azure OpenAI configuration
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OAZURE_OPENAI_EMBEDDING_DEPLOYMENTPENAI_DEPLOYMENT")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# Validate environment variables
required_env_vars = [
    "AZURE_SEARCH_SERVICE_ENDPOINT", "AZURE_SEARCH_API_KEY", "AZURE_SEARCH_INDEX_NAME",
    "AZURE_OPENAI_KEY", "AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_VERSION"
]

for var in required_env_vars:
    if not os.getenv(var):
        logging.error(f"Environment variable {var} is not set.")
        raise EnvironmentError(f"Environment variable {var} is not set.")

# Initialize AzureOpenAIEmbeddings
embeddings = AzureOpenAIEmbeddings(
    azure_deployment=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    openai_api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY
)

# Define search index custom schema
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
    SearchableField(
        name="title",
        type=SearchFieldDataType.String,
        searchable=True,
    ),
]

# Create Langchain AzureSearch object
vector_search = AzureSearch(
    azure_search_endpoint=AZURE_SEARCH_SERVICE_ENDPOINT,
    azure_search_key=AZURE_SEARCH_API_KEY,
    index_name=AZURE_SEARCH_INDEX_NAME,
    embedding_function=embeddings.embed_query,
    additional_search_client_options={"retry_total": 3},
    fields=fields,
)

def ingest(documents: list, metadata: list) -> None:
    """
    Ingest documents into Azure Search.

    :param documents: List of document chunks to ingest.
    :param metadata: List of metadata corresponding to each document chunk.
    :raises ValueError: If input is invalid.
    """
    if not isinstance(documents, list) or not documents:
        raise ValueError("Input must be a non-empty list")
    if not isinstance(metadata, list) or not metadata:
        raise ValueError("Metadata must be a non-empty list")
    if len(documents) != len(metadata):
        raise ValueError("Documents and metadata must be of the same length")
    
    vector_search.add_documents(documents, metadata)

#TODO: Add thresholds and output score
def search(query: str, search_type: str = 'similarity', top_k: int = 5) -> str:
    """
    Search for similar documents in Azure Search.

    :param query: Search query string.
    :param search_type: Type of search to perform.
    :param top_k: Number of top results to return.
    :return: Content of the top search result.
    :raises ValueError: If input is invalid.
    """
    if not isinstance(query, str) or not query:
        raise ValueError("Search query must be a non-empty string")
    
    docs = vector_search.similarity_search(query=query, k=top_k, search_type=search_type)
    return docs[0].page_content


if __name__ == "__main__":
    try:
        docs = search("What Azure AI Studio ?", search_type='hybrid', top_k=3)
        print(docs)
    except Exception as e:
        logging.error(f"Error during search: {e}")
    finally:
        if hasattr(vector_search, 'close'):
            vector_search.close()