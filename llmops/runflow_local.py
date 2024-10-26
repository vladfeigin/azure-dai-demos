#import sys
#print("sys.path:", sys.path)
import os
from promptflow.client import PFClient
from rag.rag_main import RAG
from evalflow import eval_all
from utils.utils import configure_logging, configure_tracing, configure_env
import pandas as pd

# Configure logging and tracing
logger = configure_logging()
configure_tracing()

flow = "."  # Path to the flow directory
data = "./rag/data.jsonl"  # Path to the data file for batch evaluation

#this function is used to run the RAG flow for batch evaluation
def rag_flow(session_id: str, question: str = " ") -> str:
    rag = RAG()
    return rag(session_id, question)

#run the flow
def runflow(dump_output: bool = False):
    logger.info("Running the flow for batch.") 
    pf = PFClient()
    try:
        base_run = pf.run(
            flow=rag_flow,
            data=data,
            column_mapping={
                "session_id": "${data.session_id}",
                "question": "${data.question}",
                "answer": "${data.answer}", # This ground truth answer is not used in the flow  
                "context": "${data.context}", # This context ground truth is not used in the flow
            },
            model_config=configure_env(),
            stream=True,  # To see the running progress of the flow in the console
        )
    except Exception as e:
        logger.exception("An error occurred during flow execution.")
        return

    # Get run details
    details = pf.get_details(base_run)
    # if dump_to_output True, save the details to the local file called: batch_flow_output_<timestamp>.txt
    #file name must contain a current timestamp
    if dump_output:
        #timestamp = pd.Timestamp.now().strftime("%Y%m%d%H%M%S")
        details.to_csv(f"batch_flow_output.txt", index=False)

    # Log the DataFrame
    logger.info("Run Details:\n%s", details.head(10).to_string())
    return details

#the function which runs the batch flow and then evaluates the output
def run_and_eval_flow(dump_output: bool = False):
    # Load the batch output from runflow
    batch_output = runflow(dump_output=True)
    eval_output = eval_all(batch_output, dump_output=True)
    logger.info(eval_output)

if __name__ == "__main__":
   run_and_eval_flow(dump_output=True)
    