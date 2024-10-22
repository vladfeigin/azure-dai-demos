#run as python -m aimodel.ai_model from llmops folder

from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()

from azure.identity import DefaultAzureCredential
from langchain_openai import AzureOpenAI

from aisearch.ai_search import search

#This model is a wrapper on top of Azue Open AI 
#It used for assistant to answer an end user question
#It utilize Lanchain framework 

 #init the azure active directory credential in order to generate the token
credential = DefaultAzureCredential()
# Set the API type to `azure_ad`
os.environ["OPENAI_API_TYPE"] = "azure_ad"
# Set the API_KEY to the token from the Azure credential
os.environ["OPENAI_API_KEY"] = credential.get_token("https://cognitiveservices.azure.com/.default").token    
    

class AIModel:
   
    
    def __init__(self, azure_deployment, openai_api_version, azure_endpoint):
        self.llm = AzureOpenAI(  
            azure_deployment=azure_deployment,
            openai_api_version=openai_api_version,
            azure_endpoint=azure_endpoint,
            #api_key=api_key,
        )
    
    def __set_system_prompt__():
             


if __name__ == "__main__":
    # Initialize the AI model
    llm = AIModel()

    
