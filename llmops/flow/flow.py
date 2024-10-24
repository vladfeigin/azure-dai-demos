import os
# Configure logging
import logging
from dotenv import load_dotenv
load_dotenv()

from promptflow.core import AzureOpenAIModelConfiguration
from rag.rag import RAG
from utils.utils import configure_logging, configure_tracing
from promptflow.tracing import trace, start_trace

class ChatFlow:
    
    def __init__(self, model_config: AzureOpenAIModelConfiguration):
        
        configure_tracing(__file__)
        self.logger = configure_logging()
        
        self.logger.info("ChatFlow.__init__")
        # check if the model configuration is valid
        if not model_config:
           model_config = AzureOpenAIModelConfiguration(azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
                                                        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                                                        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
                                                        api_key=os.getenv("AZURE_OPENAI_KEY"))
        self.model_config = model_config
        self.rag = RAG() 
        print(f"Model configuration: {self.model_config}")

    @trace
    def __call__(
        self,
        session_id: str ,
        question: str = "What's Microsoft Fabric?"
    ) -> str:
        """Flow entry function."""
        self.logger.info("ChatFlow.__call__")
        response = self.rag.chat(session_id, question)
        return response


if __name__ == "__main__":
    import uuid
    from promptflow.tracing import start_trace

    start_trace()
    
    flow = ChatFlow(model_config=None)
    
    session_id = str(uuid.uuid4()) 
    result = flow(session_id, "What's Fabric Data Pipeline?")
    print(result)
    result = flow(session_id, "List all data sources it supports?")
    print(result)
    result = flow(session_id, "Does it support Cosmos DB as a data source?")
    print(result)
    
    