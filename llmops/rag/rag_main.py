# python -m rag.rag
#this module encapsulates the RAG (Retrieval Augmented Generation) implementation
#it leverages AIModule class and aisearch module to search for the answer
#create RAG class


#initialize all environment variables from .env file
import os
from dotenv import load_dotenv
load_dotenv()

from aisearch.ai_search import AISearch
from aimodel.ai_model import AIModel, LLMConfig
from rag.session_store import SimpleSessionStore
from flow_configuration.flow_config import FlowConfiguration
from utils.utils import configure_tracing, get_credential, configure_logging

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from opentelemetry import trace

#tracing_collection_name = "rag_llmops"

# Configure tracing
#tracer = configure_tracing(collection_name=tracing_collection_name)
tracer = trace.get_tracer(__name__)
logger = configure_logging()

 
class RAGConfig(FlowConfiguration):
    def __init__(self, flow_name: str, llm_config: LLMConfig, **kwargs) -> None:
        super().__init__(flow_name, **kwargs)
        self.llm_config = llm_config
        # Initialize other attributes from kwargs
        #for key, value in kwargs.items():
        #    setattr(self, key, value)

    def to_dict(self) -> dict:
        # Start with the dictionary from the parent class
        config_dict = super().to_dict()

        # Add the llm_config serialized to a dictionary
        config_dict['llm_config'] = self.llm_config.to_dict()

        return config_dict
     
      
#RAG class encapsulates the RAG (Retrieval Augmented Generation) implementation
class RAG:
    #RAGConfig class encapsulates the configuration for both user intent and chat since those could diffrent models
    def __init__(self, rag_config: RAGConfig, api_key:str) -> None:
             
        #check if ragConfig is not None - throw exception
        if rag_config is None or api_key is None:
            raise ValueError("RAGConfig and api_key are required")
        
        self.rag_config = rag_config
        llm_config = rag_config.llm_config
                 
        #init the AIModel class enveloping the Azure OpenAI LLM model
        self.aimodel = AIModel(
            azure_deployment = llm_config.azure_deployment,
            openai_api_version = llm_config.openai_api_version,
            azure_endpoint = llm_config.azure_endpoint,
            api_key = api_key
        )
        #init the AISearch class , enveloping the Azure Search retriever
        self.aisearch = AISearch()
        #initiate the session store
        self._session_store = SimpleSessionStore()
        
        #create a prompt template for user intent
        self._user_intent_prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", rag_config.intent_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
                
            ]
        )
        #create history aware retriever to build a search query for the user intent
        self._history_aware_user_intent_retriever = \
            create_history_aware_retriever(self.aimodel.llm(), 
                                           self.aisearch.retriever(), 
                                                self._user_intent_prompt_template
        )
        
        #prepare final chat chain with history aware retriever 
        self._chat_prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", rag_config.chat_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        
        self._question_answer_chain = create_stuff_documents_chain(self.aimodel.llm(), self._chat_prompt_template)
        self._rag_chain = create_retrieval_chain(self._history_aware_user_intent_retriever, self._question_answer_chain)
        
        #create a chain with message history automartic handling
        self._conversational_rag_chain = RunnableWithMessageHistory(
        self._rag_chain,
        self.get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
        ) 
         
    def __call__(
        self,
        session_id: str ,
        question: str = " "
    ) -> str:
        """>>>RAG Flow entry function."""
        with tracer.start_as_current_span("RAG.__call__") as span:
            logger.info("RAG.__call__start_chat")
            span.set_attribute("session_id", session_id)
            
            response = self.chat(session_id, question)
            
            logger.info(f"RAG.__call__#response= {response}")
            return response
        
    def get_chat_prompt_template(self):
        return self._chat_prompt_template
    
    def update_chat_history(self, chat_history, question, answer):
        chat_history.extend([
            HumanMessage(content=question),
            AIMessage(content=answer)
        ])
        return chat_history
  

    def get_session_history(self, session_id:str) -> BaseChatMessageHistory:
        
        #self.logger.info(f"get_session_history#session_id= {session_id}")
        if session_id not in self._session_store.get_all_sessions_id():
            self._session_store.create_session(session_id)
            
        return self._session_store.get_session(session_id)
  
          
    def chat_stateless(self, question, chat_history=None, **kwargs):
        response = self._rag_chain.invoke({"input": question, "chat_history": chat_history})
        return response["answer"]
    
    
    def chat(self, session_id, question, **kwargs):  
        
        logger.info(f"chat#session_id= {session_id}, question= {question}")
        with tracer.start_as_current_span("RAG.__chat__") as span:
            
            span.set_attribute("session_id", session_id)
            span.set_attribute("application_id", "303474")
            span.set_attribute("application_name", "ethernity2")
            
            try:
                response = self._conversational_rag_chain.invoke( {"input": question},
                                                          config={"configurable": {"session_id": session_id}}
                                                        )
            except Exception as e:
                logger.error(f"chat#exception= {e}")
            
            return response["answer"]
    
if __name__ == "__main__":
    
    # Initialize the RAG class and empty history
    import uuid
    rag = RAG()
    
    session_id = str(uuid.uuid4())
    resp = rag(session_id, "What's Microsoft Fabric?")
    print (f"***response1 = {resp}")
    
"""
    resp = rag.chat(session_id, question="What's Microsoft Fabric Data Factory?")
    print (f"***response1 = {resp}")
    
    resp = rag.chat(session_id, question="List all data sources it supports?")
    print (f"***response2 = {resp}")
    
    resp = rag.chat(session_id, question="Does it support CosmosDB?")
    print (f"***response3 = {resp}")
    
    resp = rag.chat(session_id, question="List all my previous questions.")
    print (f"***response4 = {resp}")

    new_session_id = str(uuid.uuid4())
    resp = rag.chat(new_session_id, question="List all my previous questions.")
    print (f"***response5 = {resp}")

"""
