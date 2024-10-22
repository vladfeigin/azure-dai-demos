import os
from azure.identity import DefaultAzureCredential
from langchain_openai import AzureOpenAI

from aisearch.ai_search import search


#This model is a wrapper on top of Azue Open AI 
#It used for assistant to answer an end user question
#It utilize Lanchain framework 
class AIModel:
    def __init__(self, azure_deployment, openai_api_version, azure_endpoint, api_key):
        self.embeddings = AzureOpenAI(  
            azure_deployment=azure_deployment,
            openai_api_version=openai_api_version,
            azure_endpoint=azure_endpoint,
            api_key=api_key
        )

    
