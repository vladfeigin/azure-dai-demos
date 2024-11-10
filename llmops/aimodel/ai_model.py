#run as python -m aimodel.ai_model from llmops folder

from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()

from azure.identity import DefaultAzureCredential
from langchain_openai import AzureChatOpenAI
from flow_configuration.flow_config import FlowConfiguration


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

from utils.utils import configure_tracing
# Configure logging
from logging import INFO, getLogger
# Logging calls with this logger will be tracked
logger = getLogger(__name__)    
tracer = configure_tracing(__file__)

#create a class LLMConfig to store the configuration of the LLM model , inherits from  AgenticConfig

class LLMConfig(FlowConfiguration):
    def __init__(self, flow_name: str, **kwargs) -> None:
        super().__init__(flow_name, **kwargs)

    def to_dict(self) -> dict:
        # Utilize the parent class's to_dict method to gather attributes
        return super().to_dict()
      
        
        
        
#Wrapper class for LLM Open AI model
class AIModel:
    def __init__(self, azure_deployment, openai_api_version, azure_endpoint, api_key)-> None:
        logger.info("AIModel.Initializing AIModel")
        
        #TODO add try catch block to catch the exception
    
        with tracer.start_as_current_span("AIModel.Initializing AIModel") as span:
            self._llm = AzureChatOpenAI(  
                azure_deployment=azure_deployment,
                openai_api_version=openai_api_version,
                azure_endpoint=azure_endpoint,
                api_key=api_key,
                temperature=0
            )
            self.llm_config = \
            LLMConfig(flow_name = "AIModel. Azure Open AI",
                      azure_deployment= azure_deployment, 
                      openai_api_version = openai_api_version, 
                      azure_endpoint=azure_endpoint, 
                      model_parameters =  {"temperature":0, "seed":42})
            
            span.set_attribute ("AIModel.llm_config", self.llm_config.to_dict())
        
    def llm(self)-> AzureChatOpenAI:
        return self._llm
    
    def llm_config(self)-> LLMConfig:
        return self.llm_config
    
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
      
  

    
