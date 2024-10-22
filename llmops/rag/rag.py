#this module encapsulates the RAG (Retrieval Augmented Generation) implementation
#it leverages AIModule class and aisearch module to search for the answer
#create RAG class


#initialize all environment variables from .env file
from dotenv import load_dotenv
import os
load_dotenv()

from aisearch.ai_search import search
from aimodel.ai_model import AIModel

#init Azure open ai env variables

class RAG:
    def __init__(self) -> None:
        self.llm = AIModel(
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        )


if __name__ == "__main__":
    # Initialize the RAG model
    rag = RAG()
    r("What is the capital of France?")