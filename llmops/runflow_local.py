
import os
import pandas as pd
import json
from typing import Tuple
from promptflow.client import PFClient
from promptflow.entities import Run
from aimodel.ai_model import LLMConfig
from rag.rag_main import RAG, RAGConfig
from rag.prompts import USER_INTENT_SYSTEM_PROMPT, SYSTEM_PROMPT, HUMAN_TEMPLATE
from evaluation.evalflow import eval_batch
from utils.utils import configure_logging, configure_tracing, configure_aoai_env


tracing_collection_name = "rag_llmops"
# Configure logging and tracing
logger = configure_logging()
tracer = configure_tracing(collection_name=tracing_collection_name)

flow = "."  # Path to the flow directory
data = "./rag/data.jsonl"  # Path to the data file for batch evaluation

##--------------------------Configuration of the LLM model and RAG--------------------------##

llm_config = LLMConfig(
        flow_name = "rag_llmops::llm_config",
        azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT"), 
        openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION"), 
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
        #api_key=os.getenv("AZURE_OPENAI_KEY"), 
        model_parameters =  {"temperature":0, "seed":42}
    )

rag_config = RAGConfig(
        flow_name = "rag_llmops::rag_config",
        llm_config = llm_config,
        intent_system_prompt = USER_INTENT_SYSTEM_PROMPT,
        chat_system_prompt = SYSTEM_PROMPT,
        human_template = HUMAN_TEMPLATE,
        application_name = "rag_llmops_workshop",
        application_version = "1.0"
    )   

##--------------------------Configuration of the LLM model and RAG--------------------------##

# this function is used to run the RAG flow for batch evaluation
def rag_flow(session_id: str, question: str = " ") -> str:
    with tracer.start_as_current_span("batch::evaluation::rag_flow"):
        rag = RAG(rag_config.to_dict(), os.getenv("AZURE_OPENAI_KEY"))
        return rag(session_id, question)
    
#this function serves for running: pf flow serve --source ./ --port 8080 --host localhost for running chat UI in browser
def rag_flow_test_web(session_id: str, question: str = " ") -> str:
    with tracer.start_as_current_span("rag_flow_web_ui") as span:
        rag = RAG(rag_config.to_dict(), os.getenv("AZURE_OPENAI_KEY"))
        return rag(session_id, question)    

# run the flow
def runflow(dump_output: bool = False) -> Tuple[Run, pd.DataFrame]:
    logger.info("Running the flow for batch.")
    with tracer.start_as_current_span("batch::evaluation::runflow") as span:
        pf = PFClient()
        try:
            base_run = pf.run(
                flow=rag_flow,
                data=data,
                description="Batch evaluation of the RAG application",
                column_mapping={
                    "session_id": "${data.session_id}",
                    "question": "${data.question}",
                    # This ground truth answer is not used in the flow
                    "answer": "${data.answer}",
                    # This context ground truth is not used in the flow
                    "context": "${data.context}",
                },
                model_config=configure_aoai_env(),
                tags={"run_configuraton": rag_config.to_dict()},
                stream=True,  # To see the running progress of the flow in the console
            )
        except Exception as e:
            logger.exception(f"An error occurred during flow execution.{e}")
            print("EXCEPTION: ", e)
            
            return

        # Get run details
        details = pf.get_details(base_run)
        # if dump_to_output True, save the details to the local file called: batch_flow_output_<timestamp>.txt
        # file name must contain a current timestamp
        if dump_output:
            # timestamp = pd.Timestamp.now().strftime("%Y%m%d%H%M%S")
            details.to_csv(f"batch_flow_output.txt", index=False)

        return base_run, details

# the function which runs the batch flow and then evaluates the output
def run_and_eval_flow(dump_output: bool = False):
    with tracer.start_as_current_span("batch::evaluation::run_and_eval_flow") as span:
        # Load the batch output from runflow
        base_run, batch_output = runflow(dump_output=dump_output)
        eval_res, eval_metrics = eval_batch(
            batch_output, dump_output=dump_output)
        
        #serialize the results from dictionary to json
        logger.info(
            json.dumps({
            "name": "batch-evaluation-flow",
            "metadata": base_run._to_dict(),
            "result": eval_res.to_dict(orient='records')
            })
        )
        # Log the batch evaluation flow aggregated metrics
        logger.info(
            json.dumps({
            "name": "batch-evaluation-flow-metrics",
            "metadata": base_run._to_dict(),
            "result": eval_metrics.to_dict(orient='records')
            })
        )
        logger.info(">>>Batch evaluation flow completed successfully.")
from langchain.prompts import ChatPromptTemplate

if __name__ == "__main__": 
    run_and_eval_flow( dump_output=False )
