# python -m rag.rag
#this module encapsulates the RAG (Retrieval Augmented Generation) implementation
#it leverages AIModule class and aisearch module to search for the answer
#create RAG class


#initialize all environment variables from .env file
from dotenv import load_dotenv
import os
load_dotenv()

from aisearch.ai_search import AISearch
from aimodel.ai_model import AIModel

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain


USER_INTENT_SYSTEM_PROMPT=""" Your goal is to retrieve a user intent. Given a chat history and the latest user question,
    which might reference context in the chat history, formulate a standalone question which can be understood without the chat history. 
    Do NOT answer the question, just reformulate it if needed and otherwise return it as is."""

SYSTEM_PROMPT="""You are helpful assistant, helping the use nswer questions about Microsoft technologies. \
    You answer questions about Azure, Microsoft 365, Dynamics 365, Power Platform, Azure, Microsoft Fabric and other Microsoft technologies \
        Don't use your internal knowledge, but only provided context in the prompt. \
        Don't answer not related to Microsoft technologies questions. \
        Provide the best answer based on the context in concise and clear manner. \
        Find the main points in a question and emphasize them in the answer. \
            
        <context>
        {context}
        </context>
        """
        
HUMAN_TEMPLATE="""question: {input}"""

#RAG class encapsulates the RAG (Retrieval Augmented Generation) implementation
class RAG:
    def __init__(self) -> None:
        
        #init the AIModel class enveloping the Azure OpenAI LLM model
        self.aimodel = AIModel(
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_KEY")
        )
        
        #init the AISearch class , enveloping the Azure Search retriever
        self.aisearch = AISearch()
        
        #create a prompt template for user intent
        self._user_intent_prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", USER_INTENT_SYSTEM_PROMPT),
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
                ("system", SYSTEM_PROMPT),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        
        self._question_answer_chain = create_stuff_documents_chain(self.aimodel.llm(), self._chat_prompt_template)

        self._rag_chain = create_retrieval_chain(self._history_aware_user_intent_retriever, self._question_answer_chain)
    
    def update_chat_history(self, chat_history, question, answer):
        chat_history.extend([
            HumanMessage(content=question),
            AIMessage(content=answer)
        ])
        return chat_history
    
    def chat_stateless(self, question, chat_history=None, **kwargs):
        response = self._rag_chain.invoke({"input": question, "chat_history": chat_history})
        return response["answer"]
    
    def chat(self, question, **kwargs):
       pass
    
        

if __name__ == "__main__":
    # Initialize the RAG class and empty history
    rag = RAG()
    chat_history = []
    
    resp = rag.chat_stateless(question="What's Microsoft Fabric Data Factory?", chat_history=chat_history)
    print (f"***response= {resp}")
    rag.update_chat_history(chat_history, "What's Microsoft Fabric Data Factory?", resp)
    
    resp = rag.chat_stateless(question="List all data sources it supports?", chat_history=chat_history)
    print (f"***response= {resp}")
    rag.update_chat_history(chat_history, "List all data sources it supports?", resp)
    
    resp = rag.chat_stateless(question="Does it support CosmosDB", chat_history=chat_history)
    print (f"***response= {resp}")
    rag.update_chat_history(chat_history, "Does it support CosmosDB?", resp)
    
    resp = rag.chat_stateless(question="List all my previous questions", chat_history=chat_history)
    print (f"***response= {resp}")
    

    
