from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate

#create a base class Variant which contains following metadata:
# variant id
# variant name
# variant description

class Variant:
    def __init__(self, variant_id: str, variant_name: str, variant_description: str) -> None:
        self.variant_id = variant_id
        self.variant_name = variant_name
        self.variant_description = variant_description
        
    def to_dict(self) -> dict:
        return {
            'variant_id': self.variant_id,
            'variant_name': self.variant_name,
            'variant_description': self.variant_description
    }    

    def __str__(self) -> str:
        return f"Variant ID: {self.variant_id}, Variant Name: {self.variant_name}, Variant Description: {self.variant_description}"

    def __repr__(self) -> str:
        return f"Variant ID: {self.variant_id}, Variant Name: {self.variant_name}, Variant Description: {self.variant_description}"

# create a class VariantLLM which inherits from Variant and contains following metadata:
# llm model name
# llm model description
# llm model version
# PromptTemplate object
# dictionary of model parameters

class VariantLLM(Variant):
    # TODO add  prompt_template: ChatPromptTemplate parameter
    def __init__(self, variant_id: str, variant_name: str, variant_description: str, llm_model_name: str, llm_model_description: str, llm_model_version: str, aoai_api_version: str, aoai_endpoint:str , model_parameters: dict) -> None:
        super().__init__(variant_id, variant_name, variant_description)
        self.llm_model_name = llm_model_name
        self.llm_model_description = llm_model_description
        self.llm_model_version = llm_model_version
        self.aoai_api_version = aoai_api_version
        self.aoai_endpoint = aoai_endpoint
        #self.prompt_template = prompt_template
        self.model_parameters = model_parameters

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        base_dict.update({
            'llm_model_name': self.llm_model_name,
            'llm_model_description': self.llm_model_description,
            'llm_model_version': self.llm_model_version,
            'aoai_api_version': self.aoai_api_version,
            'aoai_endpoint': self.aoai_endpoint,
            #'prompt_template': self.prompt_template.pretty_repr(),
            'model_parameters': self.model_parameters
        })
        return base_dict
    
    def __str__(self) -> str:
        return f"{super().__str__()}, LLM Model Name: {self.llm_model_name}, LLM Model Description: {self.llm_model_description}, LLM Model Version: {self.llm_model_version}, Prompt Template: {self.prompt_template}, Model Parameters: {self.model_parameters}"

    def __repr__(self) -> str:
        return f"{super().__repr__()}, LLM Model Name: {self.llm_model_name}, LLM Model Description: {self.llm_model_description}, LLM Model Version: {self.llm_model_version}, Prompt Template: {self.prompt_template}, Model Parameters: {self.model_parameters}"

    