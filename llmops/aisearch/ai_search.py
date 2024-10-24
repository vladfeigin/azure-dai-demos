import os
import atexit
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_community.retrievers import AzureAISearchRetriever
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
from logging import INFO, getLogger
# Logging calls with this logger will be tracked
logger = getLogger(__name__)

# Azure Search configuration
AZURE_AI_SEARCH_SERVICE_ENDPOINT = os.getenv("AZURE_AI_SEARCH_SERVICE_ENDPOINT")
AZURE_AI_SEARCH_API_KEY = os.getenv("AZURE_AI_SEARCH_API_KEY")
AZURE_AI_SEARCH_INDEX_NAME = os.getenv("AZURE_AI_SEARCH_INDEX_NAME")
AZURE_AI_SEARCH_SERVICE_NAME = os.getenv("AZURE_AI_SEARCH_SERVICE_NAME")

# Azure OpenAI configuration
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
AZURE_OPENAI_EMBEDDING_ENDPOINT = os.getenv("AZURE_OPENAI_EMBEDDING_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# Validate environment variables
_required_env_vars = [
    "AZURE_AI_SEARCH_SERVICE_ENDPOINT", "AZURE_AI_SEARCH_API_KEY", "AZURE_AI_SEARCH_INDEX_NAME",
    "AZURE_OPENAI_KEY", "AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "AZURE_OPENAI_EMBEDDING_ENDPOINT", "AZURE_OPENAI_API_VERSION"
]

for var in _required_env_vars:
    if not os.getenv(var):
        logger.error(f"Environment variable {var} is not set.")
        raise EnvironmentError(f"Environment variable {var} is not set.")

# Initialize AzureOpenAIEmbeddings
_embeddings = AzureOpenAIEmbeddings(
    azure_deployment=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    openai_api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_EMBEDDING_ENDPOINT,
    api_key=AZURE_OPENAI_KEY
)

# Define search index custom schema
_fields = [
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
        vector_search_dimensions=len(_embeddings.embed_query("Text")),
        vector_search_profile_name="myHnswProfile",
    ),
    SearchableField(
        name="title",
        type=SearchFieldDataType.String,
        searchable=True,
    ),
]

# AISearch class to perform search operations
class AISearch:
    
    #init method to initialize the class
    def __init__(self) -> None:
        
        logger.info("AISearch.Initializing Azure Search client.")
        # Create Langchain AzureSearch object
        self._vector_search = AzureSearch(
        azure_search_endpoint=AZURE_AI_SEARCH_SERVICE_ENDPOINT,
        azure_search_key=AZURE_AI_SEARCH_API_KEY,
        index_name=AZURE_AI_SEARCH_INDEX_NAME,
        embedding_function=_embeddings.embed_query,
        additional_search_client_options={"retry_total": 3},
        fields=_fields,
        )
        self._retriever = AzureAISearchRetriever(content_key="chunk", top_k=3, index_name=AZURE_AI_SEARCH_INDEX_NAME)
        atexit.register(self.__close__)

    def __close__(self)-> None:
        """
        Close the Azure Search client.
        """
        print("Closing Azure Search client.")   
          
    def retriever(self) -> AzureAISearchRetriever:
        return self._retriever
        
    def ingest(self, documents: list, metadata: list) -> None:
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
        
        self._vector_search.add_documents(documents, metadata)

    #TODO: Add thresholds and output score
    def search(self, query: str, search_type: str = 'similarity', top_k: int = 5) -> str:
        """
        Search for similar documents in Azure Search.

        :param query: Search query string.
        :param search_type: Type of search to perform.
        :param top_k: Number of top results to return.
        :return: Content of the top search result.
        :raises ValueError: If input is invalid.
        """
        logger.info(f"Search: Searching for similar documents using query: {query}")
        if not isinstance(query, str) or not query:
            raise ValueError("Search query must be a non-empty string")
        
        docs = self._vector_search.similarity_search (query=query, k=top_k, search_type=search_type)
        return docs[0].page_content


if __name__ == "__main__":
    try:
        aisearch = AISearch()
        docs = aisearch.search("What Microsoft Fabric", search_type='hybrid', top_k=3)
        #print(docs)
        docs_retr = aisearch.retriever().invoke("What is Microsoft Azure?")
        print(docs_retr)
    except Exception as e:
        logger.error(f"Error during search: {e}")
    finally:
        logger.info("Search completed.")
