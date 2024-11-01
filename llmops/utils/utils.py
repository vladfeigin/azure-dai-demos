import os
from dotenv import load_dotenv
load_dotenv()
import logging

from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from promptflow.tracing import trace, start_trace
from azure.monitor.opentelemetry import configure_azure_monitor

@trace
def configure_env():
    # Retrieve environment variables with default values or handle missing cases
    azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    azure_deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT")
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION")
    api_key = os.environ.get("AZURE_OPENAI_KEY")

    if not all([azure_endpoint, azure_deployment, api_version, api_key]):
        logging.error("One or more Azure OpenAI environment variables are missing.")
        raise Exception("One or more environment variables are missing.")

    model_config = {
    "azure_endpoint": azure_endpoint,
    "api_key": api_key,
    "azure_deployment": azure_deployment,
    "api_version": api_version,
    }   
    return model_config 

@trace
def get_credential():
    try:
        credential = DefaultAzureCredential()
        # Check if given credential can get token successfully.
        credential.get_token("https://management.azure.com/.default")
    except Exception as ex:
        # Fall back to InteractiveBrowserCredential in case DefaultAzureCredential does not work
        credential = InteractiveBrowserCredential()
    return credential

#for pf tracing see details here: https://learn.microsoft.com/en-us/azure/ai-studio/how-to/develop/trace-local-sdk?tabs=python 
#local traces see in: http://127.0.0.1:23337/v1.0/ui/traces/
@trace
def configure_tracing(collection_name: str = "llmops")-> None:
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    configure_azure_monitor(collection_name=collection_name)
    start_trace()
    
@trace    
def configure_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    #to avoid duplicate logging, check the logger has no handlers
    if not logger.handlers:
        logger.info("Configuring logging. Handlres is being added.")
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
        
    logging.getLogger('azure').setLevel(logging.WARNING)
    logging.getLogger('azure.core').setLevel(logging.WARNING)
    logging.getLogger('azure.core.pipeline').setLevel(logging.WARNING)
    logging.getLogger('azure.core.pipeline.policies').setLevel(logging.WARNING)
    logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)
    logging.getLogger('opentelemetry.attributes').setLevel(logging.ERROR)
    logging.getLogger('opentelemetry.instrumentation.instrumentor').setLevel(logging.ERROR)
    logging.getLogger('oopentelemetry.trace').setLevel(logging.ERROR)
    logging.getLogger('oopentelemetry.metrics').setLevel(logging.ERROR)
        
    return logger
    

    


