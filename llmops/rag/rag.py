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

from langchain_core.prompts import HumanMessagePromptTemplate
from langchain_core.prompts import SystemMessagePromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import  create_history_aware_retriever
from langchain.chains import  create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

#init Azure open ai env variables

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


class RAG:
    def __init__(self) -> None:
        #init the AIModel class
        self.aimodel = AIModel(
            
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_KEY")
        )
        self.system_prompt_template = SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT)
        self.human_promot_template = HumanMessagePromptTemplate.from_template(HUMAN_TEMPLATE)
        self.chat_prompt_template = ChatPromptTemplate.from_messages([SYSTEM_PROMPT, HUMAN_TEMPLATE])
        #init the AISearch class
        self.aisearch = AISearch()
     
    def answer_1(self, question, chat_history=None, **kwargs):
        #call the search function to get the context
        context = self.aisearch.search(query=question)
        
        prompt = self.chat_prompt_template.format_prompt(context=context, input=question)
        
        #print (f" final prompt= {prompt}")
        response = self.aimodel.generate_response(prompt)
        #chain = self.aimodel.llm | prompt
        #response = chain.invoke()
        return response.content
    
    def answer_no_history(self, question, chat_history=None, **kwargs):
        #call the search to get the context
        combine_docs_chain = create_stuff_documents_chain(self.aimodel.llm(), self.chat_prompt_template)
        chain = create_retrieval_chain(self.aisearch.retriever(), combine_docs_chain)
        response = chain.invoke({"input": question, "chat_history": chat_history})
        return response
        

if __name__ == "__main__":
    # Initialize the RAG model
    
    rag = RAG()
    #resp = rag.answer_1(question="What's Microsoft Fabric?", context="")
    resp = rag.answer_no_history(question="What's Microsoft Fabric?", context="")
    print (f"***response type = {type(resp)}")
    print (f"***response= {resp['answer']}")

    
