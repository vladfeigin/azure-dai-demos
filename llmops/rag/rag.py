# python -m rag.rag
#this module encapsulates the RAG (Retrieval Augmented Generation) implementation
#it leverages AIModule class and aisearch module to search for the answer
#create RAG class


#initialize all environment variables from .env file
from dotenv import load_dotenv
import os
load_dotenv()

from aisearch.ai_search import search
from aimodel.ai_model import AIModel

from langchain_core.prompts import HumanMessagePromptTemplate
from langchain_core.prompts import SystemMessagePromptTemplate
from langchain_core.prompts import ChatPromptTemplate

#init Azure open ai env variables

SYSTEM_PROMPT="You are helpful assistant, helping the use nswer questions about Microsoft technologies. \
    You answer questions about Azure, Microsoft 365, Dynamics 365, Power Platform, Azure, Microsoft Fabric and other Microsoft technologies \
        Don't use your internal knowledge, but only provided context in the prompt. \
        Don't answer not related to Microsoft technologies questions. \
        Provide the best answer based on the context in concise and clear manner. \
        Find the main points in a question and emphasize them in the answer. "
        
HUMAN_TEMPLATE=""" Given context: {context},  question: {question}"""


class RAG:
    def __init__(self) -> None:
        self.aimodel = AIModel(
            
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_KEY")
        )
        self.system_prompt_template = SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT)
        self.human_promot_template = HumanMessagePromptTemplate.from_template(HUMAN_TEMPLATE)
        self.chat_prompt_template = ChatPromptTemplate.from_messages([SYSTEM_PROMPT, HUMAN_TEMPLATE])
    
    def answer(self, question, chat_history=None, **kwargs):
        
        context = search(question)
        
        prompt = self.chat_prompt_template.format_prompt(context=context, question=question)
        #print (f" final prompt= {prompt}")
        response = self.aimodel.generate_response(prompt)
        return response.content
        

if __name__ == "__main__":
    # Initialize the RAG model
    
    rag = RAG()
    resp = rag.answer(question="What's Microsoft Fabric?", context="")
    print (f"***response= {resp}")

    
