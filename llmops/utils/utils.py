import os
from dotenv import load_dotenv
load_dotenv()
import logging

from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from promptflow.tracing import trace, start_trace
from azure.monitor.opentelemetry import configure_azure_monitor

def get_credential():
    try:
        credential = DefaultAzureCredential()
        # Check if given credential can get token successfully.
        credential.get_token("https://management.azure.com/.default")
    except Exception as ex:
        # Fall back to InteractiveBrowserCredential in case DefaultAzureCredential does not work
        credential = InteractiveBrowserCredential()
    return credential

def configure_tracing(collection_name: str = "llmops")-> None:
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    configure_azure_monitor(collection_name=collection_name)
    start_trace()
    
def configure_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    # Add handler to the root logger
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    return logger
    
    


