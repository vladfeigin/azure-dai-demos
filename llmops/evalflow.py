
#TODO - currently the code uses default prompty files for each evaluator,e.g azure/ai/evaluation/_evaluators/_relevance/relevance.prompty
# if you need to use custom prompty files, you can create them, create custom evalutor class whihc inherits from corresponding evaluator class 
# and override the PROMPTY_FILE attribute with the path to the custom prompty file
#for example: 

"""
#pip install typing_extensions
 class CustomGroundednessEvaluator(GroundednessEvaluator):

    PROMPTY_FILE = "custom_groundedness.prompty"  # Name of your custom prompty file
    @override
    def __init__(self, model_config: dict):
        # Determine the path to the custom prompty file
        current_dir = os.path.dirname(__file__)
        custom_prompty_path = os.path.join(current_dir, self.PROMPTY_FILE)
        
        # Check if the custom prompty file exists
        if not os.path.exists(custom_prompty_path):
            raise FileNotFoundError(f"Custom prompty file not found at: {custom_prompty_path}")
        
        # Initialize the base class with the custom prompty file
        super().__init__(model_config=model_config)
        
        # log the prompty file path
        logger = logging.getLogger(__name__)
        logger.info(f"Using custom prompty file for GroundednessEvaluator: {custom_prompty_path}")
        """

import os
from dotenv import load_dotenv
load_dotenv()

from azure.ai.evaluation import (
    RelevanceEvaluator,
    GroundednessEvaluator,
    SimilarityEvaluator,
    CoherenceEvaluator,
)
#from  azure.ai.evaluation import AzureOpenAIModelConfiguration

from utils.utils import configure_logging, configure_tracing, configure_env
import pandas as pd

# Configure logging
logger = configure_logging()
configure_tracing()

# run the evaluation on batch output from runflow function

#get LLM configuration
model_config = configure_env()

#initialize dictiobary with all 4 evaluators
evaluators = {
        "relevance": RelevanceEvaluator(model_config),
        "groundedness": GroundednessEvaluator(model_config),
        "similarity": SimilarityEvaluator(model_config),
        "coherence": CoherenceEvaluator(model_config),
}

# Function to verify prompty file paths
def verify_prompty_files(evaluators: dict):
    for name, evaluator in evaluators.items():
        # Access the _prompty_file attribute
        prompty_file = getattr(evaluator, '_prompty_file', None)
        if prompty_file:
            if os.path.exists(prompty_file):
                logger.info(f"Evaluator '{name}' is using existing prompty file: {prompty_file}")
            else:
                logger.error(f"Evaluator '{name}' is using missing prompty file: {prompty_file}")
        else:
            logger.warning(f"Evaluator '{name}' does not have a '_prompty_file' attribute.")

    
def relevancy(batch_output: pd.DataFrame, res_df: pd.DataFrame):
    
    # write code which iterates on batch_output and evaluate each row for relevance
    # pandas schema is : inputs.session_id, inputs.question, inputs.answer, inputs.context, outputs.output
    # evalaute Relevance, it has following paraeter response should be maped to outputs.output,  context should be mapped to inputs.context, query 
    # should be mapped to inputs.question
    # keep score per line in an output array and then evalute caclulate the average score for the batch and return it
    # evaluluate relevance average score
    
    #relevance scores
    relevance_scores = []
    relevancy_evaluator = evaluators["relevance"]
    
    for index, row in batch_output.iterrows():
        relevance_score =relevancy_evaluator(
            response=row["outputs.output"],
            context=row["inputs.context"],
            query=row["inputs.question"]
        )
        
        new_row = pd.DataFrame ([{
            "response": row["outputs.output"],
            "context": row["inputs.context"],
            "question": row["inputs.question"],
            "relevance": relevance_score["gpt_relevance"]
        }])
        res_df = pd.concat([res_df, new_row], ignore_index=True)  
        relevance_scores.append(relevance_score["gpt_relevance"])
        
    #calculate average score
    avg_relevance_score = sum(relevance_scores) / len(relevance_scores)
    return avg_relevance_score, res_df

# add method for groundedness evaluation, note that groundedness evaluator receives 2 parameter : response and context 
def groundedness(batch_output: pd.DataFrame, res_df: pd.DataFrame):
    # write code which iterates on batch_output and evaluate each row for groundedness
    # pandas schema is : inputs.session_id, inputs.question, inputs.answer, inputs.context, outputs.output
    # evalaute Groundedness, it has following paraeter response should be mapoed to outputs.output,  context should be mapped to inputs.context
    # keep score per line in an output array and then evalute caclulate the average score for the batch and return it
    # evaluluate groundedness average score
    
    #groundedness scores
    groundedness_scores = []
    groundedness_evaluator = evaluators["groundedness"]
    for index, row in batch_output.iterrows():
        
        groundedness_score =groundedness_evaluator(
            response=row["outputs.output"],
            context=row["inputs.context"]
        )
        new_row = pd.DataFrame([{
            "response": row["outputs.output"],
            "context": row["inputs.context"],
            "groundeness": groundedness_score["gpt_groundedness"]
        }])
        res_df = pd.concat([res_df, new_row], ignore_index=True)
        groundedness_scores.append(groundedness_score["gpt_groundedness"])
        
    #calculate average score
    avg_groundedness_score = sum(groundedness_scores) / len(groundedness_scores)
    return avg_groundedness_score, res_df

def similarity(batch_output: pd.DataFrame, res_df: pd.DataFrame):
    # write code which iterates on batch_output and evaluate each row for similarity
    # pandas schema is : inputs.session_id, inputs.question, inputs.answer, inputs.context, outputs.output
    # evalaute Similarity, it has following paraeter response should be mapoed to outputs.output,  context should be mapped to inputs.context
    # keep score per line in an output array and then evalute caclulate the average score for the batch and return it
    # evaluluate similarity average score
    
    #similarity scores
    similarity_scores = []
    similarity_evaluator = evaluators["similarity"]
    for index, row in batch_output.iterrows():
        similarity_score =similarity_evaluator(
            response=row["outputs.output"],
            ground_truth=row["inputs.answer"],
            query=row["inputs.question"]
        )
        new_row = pd.DataFrame([{
            "response": row["outputs.output"],
            "ground_truth": row["inputs.answer"],
            "question": row["inputs.question"],
            "similarity": similarity_score["gpt_similarity"]
        }])
        res_df = pd.concat([res_df, new_row], ignore_index=True)
        similarity_scores.append(similarity_score["gpt_similarity"])
        
    #calculate average score
    avg_similarity_score = sum(similarity_scores) / len(similarity_scores)
    return avg_similarity_score, res_df


# add method for coherence evaluation, note that coherence evaluator receives 2 parameter : response and context
def coherence(batch_output: pd.DataFrame,res_df: pd.DataFrame):
    # write code which iterates on batch_output and evaluate each row for coherence
    # pandas schema is : inputs.session_id, inputs.question, inputs.answer, inputs.context, outputs.output
    # evalaute Coherence, it has following paraeter response should be mapoed to outputs.output,  context should be mapped to inputs.context
    # keep score per line in an output array and then evalute caclulate the average score for the batch and return it
    # evaluluate coherence average score
    
    #coherence scores
    coherence_scores = []
    coherence_evaluator = evaluators["coherence"]
    #create pandas dataframe which contains: 
    for index, row in batch_output.iterrows():
        coherence_score =coherence_evaluator(
            response=row["outputs.output"],
            query=row["inputs.question"]
        )
        new_row = pd.DataFrame([{
            "response": row["outputs.output"],
            "question": row["inputs.question"],
            "coherence": coherence_score['gpt_coherence']
        }])
        
        res_df = pd.concat([res_df, new_row], ignore_index=True)
        coherence_scores.append(coherence_score['gpt_coherence'])
        
    #calculate average score
    avg_coherence_score = sum(coherence_scores) / len(coherence_scores)
    return avg_coherence_score, res_df

# add function eva_all which calls all 4 evaluation functions and returns the average score for each
def eval_all(batch_output: pd.DataFrame, dump_output: bool = False):
    
    # Verify prompty files after initializing evaluators
    logger.info("Verifying prompty files availability for evaluators.")
    verify_prompty_files(evaluators)
    
    # create a pandas dataframe which contains follwoing columns: question, ground_truth, context, output, groundeness, relevance, similarity, coherence
    eval_res = pd.DataFrame(columns=["question", "ground_truth", "context", "response", "groundeness", "relevance", "similarity", "coherence"])
    
    avg_relevance_score,eval_res = relevancy(batch_output, eval_res)
    avg_groundedness_score,eval_res = groundedness(batch_output, eval_res)
    avg_similarity_score,eval_res = similarity(batch_output, eval_res) 
    avg_coherence_score,eval_res = coherence(batch_output, eval_res)
    
    # create a pandas dataframe which contains all the metrics and return it
    eval_metrics = pd.DataFrame(
        {
            "metric": ["relevance", "groundedness", "similarity", "coherence"],
            "score": [avg_relevance_score, avg_groundedness_score, avg_similarity_score, avg_coherence_score],
        }
    )
    # if dump_to_output True, save the details to the local file called: batch_evaluation_output_<timestamp>.txt
    if dump_output:
        timestamp = pd.Timestamp.now().strftime("%Y%m%d%H%M%S")
        #batch_output.to_json(f"batch_output_{timestamp}.txt", index=False)
        eval_metrics_output= eval_metrics.to_json(f"batch_eval_output_{timestamp}.json", orient='records', lines=True)
        eval_res_output = eval_res.to_json(f"eval_results_{timestamp}.json", orient='records', lines=True)
    return eval_res_output, eval_metrics_output

from runflow_local import runflow

# add main function to run the evaluation
if __name__ == "__main__":
    # Load the batch output from runflow
    batch_output = runflow(dump_output=True)

    eval_res, eval_metrics = eval_all(batch_output, dump_output=True)
    #logger.info(eval_res)
    #logger.info(eval_metrics)
    
   