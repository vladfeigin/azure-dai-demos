import sys
print("sys.path:", sys.path)
import os
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from promptflow.core import  AzureOpenAIModelConfiguration
from promptflow.azure import PFClient

flow = "."  # Path to the flow directory
data = "./rag/data.jsonl"  # Path to the data file

def get_credential():
    
        try:
            credential = DefaultAzureCredential()
            # Check if given credential can get token successfully.
            credential.get_token("https://management.azure.com/.default")
            return credential 
        except Exception as ex:
            # Fall back to InteractiveBrowserCredential in case DefaultAzureCredential does not work
            credential = InteractiveBrowserCredential()
        

def runflow(credential):
    
    model_config = AzureOpenAIModelConfiguration(
        connection="openai-australia-east-303474",
        azure_deployment="gpt-4o-2"
    )
        
    pf = PFClient.from_config(credential=credential)
    print(pf)
    my_project_path=os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    print(f" my project path = {my_project_path}") 
    #with tracer.start_as_current_span('genai-request') as span:
    try:
            base_run = pf.run(
            flow=flow,
            data=data,
            column_mapping={
                "question": "${data.question}",
                "answer": "${data.answer}",
                "context": "${data.context}",
            },
            model_config=model_config,
            environment_variables={
                "AZURE_OPENAI_API_KEY": "${openai-australia-east-303474.api_key}",
                "AZURE_OPENAI_ENDPOINT": "${openai-australia-east-303474.api_base}",
                "PYTHONPATH": f"{my_project_path}{os.pathsep}{os.environ.get('PYTHONPATH', '')}"
            },
            stream=True,
        )
    except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    
    print(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    #set PYTHONPATH environment variable to the root of the project:
    #os.environ["PYTHONPATH"] = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    credential = get_credential()
    
    runflow(credential)
    print("Done")

    