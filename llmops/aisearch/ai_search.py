from utils.utils import configure_logging
from opentelemetry import trace
from azure.search.documents.indexes.models import (
    ScoringProfile,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    TextWeights,
)
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.retrievers import AzureAISearchRetriever
from langchain_community.vectorstores.azuresearch import AzureSearch
import os
import atexit
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()


logger = configure_logging()
tracer = trace.get_tracer(__name__)

# Azure Search configuration
AZURE_AI_SEARCH_SERVICE_ENDPOINT = os.getenv(
    "AZURE_AI_SEARCH_SERVICE_ENDPOINT")
AZURE_AI_SEARCH_API_KEY = os.getenv("AZURE_AI_SEARCH_API_KEY")
AZURE_AI_SEARCH_INDEX_NAME = os.getenv("AZURE_AI_SEARCH_INDEX_NAME")
AZURE_AI_SEARCH_SERVICE_NAME = os.getenv("AZURE_AI_SEARCH_SERVICE_NAME")

# Azure OpenAI configuration
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv(
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
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

    # init method to initialize the class
    def __init__(self) -> None:

        logger.info("AISearch.Initializing Azure Search client.")
        # Create Langchain AzureSearch object
        self._vector_search = AzureSearch(
            azure_search_endpoint=AZURE_AI_SEARCH_SERVICE_ENDPOINT,
            azure_search_key=AZURE_AI_SEARCH_API_KEY,
            index_name=AZURE_AI_SEARCH_INDEX_NAME,
            embedding_function=_embeddings.embed_query,
            search_type="hybrid",
            semantic_configuration_name="vector-1729431147052-semantic-configuration",
            additional_search_client_options={"retry_total": 3, "logging_enable":True, "logger":logger},
            fields=_fields,
        )
        # Create retriever object
        #supported search types: "semantic_hybrid", "similarity" (default) , "hybryd"
        self._retriever = self._vector_search.as_retriever(search_type="hybrid")
               
        atexit.register(self.__close__)

    def __close__(self) -> None:
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
            raise ValueError(
                "Documents and metadata must be of the same length")

        self._vector_search.add_documents(documents, metadata)

    # TODO: Add thresholds and output score
    def search(self, query: str, search_type: str = 'hybrid', top_k: int = 5) -> str:
        """
        Search for similar documents in Azure Search.

        :param query: Search query string.
        :param search_type: Type of search to perform.
        :param top_k: Number of top results to return.
        :return: Content of the top search result.
        :raises ValueError: If input is invalid.
        """
        logger.info(
            f"Search: Searching for similar documents using query: {query}")
        with tracer.start_as_current_span("aisearch") as aisearch_span:
            if not isinstance(query, str) or not query:
                raise ValueError("Search query must be a non-empty string")
            aisearch_span.set_attribute("ai_search_query:", query)
            
            docs = self._vector_search.similarity_search(
                query=query, k=top_k, search_type=search_type)
            
            # run in loop on the list of documents take the content for each document in page_content and concatenate them. put tab between content of each document
            # return the concatenated content
            # each document in the list is: langchain_core.documents.base.Document
            final_content = ""
            for doc in docs:
                final_content += doc.page_content + "\t"
            return final_content

if __name__ == "__main__":
    try:
        aisearch = AISearch()
        content = aisearch.search("What Microsoft Fabric",
                               search_type='hybrid', top_k=3)
        print("Content:>>>> ", content)
     
        """
        docs_retr = aisearch.retriever().invoke("What is Microsoft Fabric?")
        content = ""
        for doc in docs_retr:
            content += doc.page_content + "###"
            
        print("Content:>>>> ", content)
        """   
    except Exception as e:
        logger.error(f"Error during search: {e}")
    finally:
        logger.info("Search completed.")
