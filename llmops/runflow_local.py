#import sys
#print("sys.path:", sys.path)
import os
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from promptflow.core import  AzureOpenAIModelConfiguration
from promptflow.client import PFClient
from rag.rag_main import RAG
from utils.utils import configure_logging  # Assuming you have this function
import pandas as pd

# Configure logging
logger = configure_logging()

flow = "."  # Path to the flow directory
data = "./rag/data.jsonl"  # Path to the data file for batch evaluation

#this function is used to run the RAG flow for batch evaluation
def rag_flow(session_id: str, question: str = " ") -> str:
    rag = RAG()
    return rag(session_id, question)

#run the flow
def runflow():
    # Retrieve environment variables with default values or handle missing cases
    azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    azure_deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT")
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION")
    api_key = os.environ.get("AZURE_OPENAI_KEY")

    if not all([azure_endpoint, azure_deployment, api_version, api_key]):
        logger.error("One or more Azure OpenAI environment variables are missing.")
        return

    model_config = AzureOpenAIModelConfiguration(
        azure_endpoint=azure_endpoint,
        azure_deployment=azure_deployment,
        api_version=api_version,
        api_key=api_key
    )
    logger.info(f"Model configuration: {model_config}")

    pf = PFClient()
    try:
        base_run = pf.run(
            flow=rag_flow,
            data=data,
            column_mapping={
                "session_id": "${data.session_id}",
                "question": "${data.question}",
            },
            model_config=model_config,
            stream=True,  # To see the running progress of the flow in the console
        )
    except Exception as e:
        logger.exception("An error occurred during flow execution.")
        return

    # Get run details
    logger.info("---------------------Getting run details----------------")
    details = pf.get_details(base_run)

    # Print to console
    print(details.head(10))

    # Log the DataFrame
    logger.info("Run Details:\n%s", details.head(10).to_string())

if __name__ == "__main__":
    runflow()
    logger.info("Done")

    