
import os
import pandas as pd
from typing import Tuple
from promptflow.client import PFClient
from promptflow.entities import Run
from rag.rag_main import RAG
from evaluation.variant import VariantLLM
from evaluation.evalflow import eval_batch
from utils.utils import configure_logging, configure_tracing, configure_aoai_env


tracing_collection_name = "rag_llmops"
# Configure logging and tracing
logger = configure_logging()
tracer = configure_tracing(collection_name=tracing_collection_name)

flow = "."  # Path to the flow directory
data = "./rag/data.jsonl"  # Path to the data file for batch evaluation

# this function is used to run the RAG flow for batch evaluation
def rag_flow(session_id: str, question: str = " ") -> str:
    with tracer.start_as_current_span("rag_flow"):
        rag = RAG()
        return rag(session_id, question)

# run the flow

def runflow(variant:VariantLLM,  dump_output: bool = False) -> Tuple[Run, pd.DataFrame]:
    logger.info("Running the flow for batch.")
    with tracer.start_as_current_span("runflow"):
        pf = PFClient()
        try:
            base_run = pf.run(
                flow=rag_flow,
                data=data,
                column_mapping={
                    "session_id": "${data.session_id}",
                    "question": "${data.question}",
                    # This ground truth answer is not used in the flow
                    "answer": "${data.answer}",
                    # This context ground truth is not used in the flow
                    "context": "${data.context}",
                },
                model_config=configure_aoai_env(),
                tags={"variant": variant.to_dict()},
                stream=True,  # To see the running progress of the flow in the console
            )
        except Exception as e:
            logger.exception("An error occurred during flow execution.")
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
def run_and_eval_flow(variant:VariantLLM, dump_output: bool = False):
    with tracer.start_as_current_span("run_and_eval_flow") as span:
        # Load the batch output from runflow
        base_run, batch_output = runflow(variant, dump_output=dump_output)
        eval_res, eval_metrics = eval_batch(
            batch_output, dump_output=dump_output)
        logger.info(
            f"<BATCH-EVALUATION-FLOW> Metadata: {base_run._to_dict()} result: {eval_res.to_dict(orient='records')}")
        logger.info(
            f"<BATCH-EVALUATION-FLOW-AGGREGATED-METRICS> Metadata: {base_run._to_dict()} result: {eval_metrics.to_dict(orient='records')}")



from langchain.prompts import ChatPromptTemplate

if __name__ == "__main__":

    # variant
    variant = VariantLLM(
        variant_id="01",
        variant_name="gpt4o-2024-05-13-api-2024-08-01-preview",
        variant_description="testing variant: gpt4o-2024-05-13-api-2024-08-01-preview",
        llm_model_description="testing gpt4o ver. 2024-05-13 model.. ",
        llm_model_name="gpt4o",
        llm_model_version="2024-05-13",
        model_parameters={"seed": 42, "max_tokens": 2000, "temperature": 0.0},
        aoai_api_version='2024-08-01-preview',
        aoai_endpoint="https://openai-api.azurewebsites.net",
        #prompt_template="Empty prompt template!",
        
    )

    run_and_eval_flow(variant, dump_output=False)
