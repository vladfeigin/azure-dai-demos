#run as python -m aimodel.ai_model from llmops folder

from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()

from azure.identity import DefaultAzureCredential
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import PromptTemplate

#from aisearch.ai_search import search

#This model is a wrapper on top of Azue Open AI 
#It used for assistant to answer an end user question
#It utilize Lanchain framework 

 #init the azure active directory credential in order to generate the token
#credential = DefaultAzureCredential()
# Set the API type to `azure_ad`
#os.environ["OPENAI_API_TYPE"] = "azure_ad"
# Set the API_KEY to the token from the Azure credential
#api_key = credential.get_token("https://cognitiveservices.azure.com/.default").token 
#os.environ["OPENAI_API_KEY"] = api_key
    

class AIModel:
   
    
    def __init__(self, azure_deployment, openai_api_version, azure_endpoint, api_key):
        
        self.llm = AzureChatOpenAI(  
            azure_deployment=azure_deployment,
            openai_api_version=openai_api_version,
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            temperature=0
            
        )
        #self.llm.invoke("What is Microsoft Azure?")
    
    def generate_response(self, prompt):
        response = self.llm.invoke(prompt)
        return response 
   
             
if __name__ == "__main__":
    
    # Initialize the AI model
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT")
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION")
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key=os.getenv("AZURE_OPENAI_KEY")
    
    llm = AIModel(azure_deployment,openai_api_version,azure_endpoint,api_key)
    
    
  

    
