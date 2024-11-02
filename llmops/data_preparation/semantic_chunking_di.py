"""
The environment variables are loaded from the `.env` file in the same directory as this notebook.
"""
import os
from dotenv import load_dotenv
_=load_dotenv()

from azure.storage.blob import BlobServiceClient
from typing import List
from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_openai import AzureOpenAIEmbeddings
from utils.utils import(configure_aoai_env,
                         configure_logging,
                         configure_embedding_env,
                         configure_docintell_env,
                         get_credential)


embedding_env = configure_embedding_env()
aoai_env = configure_aoai_env()

aoai_embeddings = AzureOpenAIEmbeddings(
    azure_deployment=embedding_env["embedding_model_name"],
    azure_endpoint=embedding_env["embedding_model_endpoint"],
    api_key=aoai_env["api_key"], 
    openai_api_version=aoai_env["api_version"], 
)
#test the embedding model
#vector = aoai_embeddings.embed_query("What is the LLM?")
#print(vector)

docintel_env = configure_docintell_env()
#pdf_path="./data/hyde.pdf"

def process_document(doc_path, mode="markdown"):
    """
    Process a document using Azure AI Document Intelligence and split it into chunks based on markdown headers.
    """
    # Load the document using Azure AI Document Intelligence.
    loader = AzureAIDocumentIntelligenceLoader(file_path=doc_path, 
                                               api_key = docintel_env["doc_intelligence_key"], 
                                               api_endpoint = docintel_env["doc_intelligence_endpoint"],
                                               api_model="prebuilt-layout",
                                               api_version=docintel_env["doc_intellugence_api_version"],
                                               mode=mode)
    docs = loader.load()
    
    # Split the document into chunks base on markdown headers.
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    text_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    
    doc_content = docs[0].page_content
    chunks = text_splitter.split_text(doc_content)
    print("Length of splits: " + str(len(chunks)))
    return chunks


def get_files_from_blob_storage(storage_account_name:str, container_name:str, folder_name:str)->List[str]:
    
    from azure.identity import DefaultAzureCredential
    import os
    # Create a blob service client
    blob_service_client = BlobServiceClient(account_url=f"https://{storage_account_name}.blob.core.windows.net", credential=DefaultAzureCredential())
    # Get the container client
    container_client = blob_service_client.get_container_client(container_name)
    # List the blobs in the container
    blobs = container_client.list_blobs(name_starts_with=folder_name)
    # Get the blob names
    files = [blob.name for blob in blobs]
    return files

#create a function getting a list of files from the blob storage and then it calculates path to the file and 
# calls process_document function to process the document
def process_files_from_blob_storage(storage_account_name:str, container_name:str, folder_name:str, mode="markdown"):
    files = get_files_from_blob_storage(storage_account_name, container_name, folder_name)
    for file in files:
        file_path = f"https://{storage_account_name}.blob.core.windows.net/{container_name}/{file}"
        print("Processing file: ", file_path)
        chunks = process_document(file_path, mode)
        print("Number of chunks: ", len(chunks))
    return chunks








if __name__ == "__main__":
    chinks = process_document("./data/hyde.pdf")


                         


