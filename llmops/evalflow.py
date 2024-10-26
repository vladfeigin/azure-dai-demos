
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
    
def relevancy(batch_output: pd.DataFrame):
    
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
        relevance_scores.append(relevance_score['gpt_relevance'])
    #calculate average score
    avg_relevance_score = sum(relevance_scores) / len(relevance_scores)
    return avg_relevance_score

# add method for groundedness evaluation, note that groundedness evaluator receives 2 parameter : response and context 
def groundedness(batch_output: pd.DataFrame):
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
        groundedness_scores.append(groundedness_score['gpt_groundedness'])
    #calculate average score
    avg_groundedness_score = sum(groundedness_scores) / len(groundedness_scores)
    return avg_groundedness_score

def similarity(batch_output: pd.DataFrame):
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
        similarity_scores.append(similarity_score['gpt_similarity'])
    #calculate average score
    avg_similarity_score = sum(similarity_scores) / len(similarity_scores)
    return avg_similarity_score


# add method for coherence evaluation, note that coherence evaluator receives 2 parameter : response and context
def coherence(batch_output: pd.DataFrame):
    # write code which iterates on batch_output and evaluate each row for coherence
    # pandas schema is : inputs.session_id, inputs.question, inputs.answer, inputs.context, outputs.output
    # evalaute Coherence, it has following paraeter response should be mapoed to outputs.output,  context should be mapped to inputs.context
    # keep score per line in an output array and then evalute caclulate the average score for the batch and return it
    # evaluluate coherence average score
    
    #coherence scores
    coherence_scores = []
    coherence_evaluator = evaluators["coherence"]
    for index, row in batch_output.iterrows():
        coherence_score =coherence_evaluator(
            response=row["outputs.output"],
            query=row["inputs.question"]
        )
        coherence_scores.append(coherence_score['gpt_coherence'])
    #calculate average score
    avg_coherence_score = sum(coherence_scores) / len(coherence_scores)
    return avg_coherence_score

# add function eva_all which calls all 4 evaluation functions and returns the average score for each
def eval_all(batch_output: pd.DataFrame, dump_output: bool = False):
    
    avg_relevance_score = relevancy(batch_output)
    avg_groundedness_score = groundedness(batch_output)
    avg_similarity_score = similarity(batch_output) 
    avg_coherence_score = coherence(batch_output)
    # create a pandas dataframe which contains all the metrics and return it
    metrics = pd.DataFrame(
        {
            "metric": ["relevance", "groundedness", "similarity", "coherence"],
            "score": [avg_relevance_score, avg_groundedness_score, avg_similarity_score, avg_coherence_score],
        }
    )
    # if dump_to_output True, save the details to the local file called: batch_evaluation_output_<timestamp>.txt
    if dump_output:
        timestamp = pd.Timestamp.now().strftime("%Y%m%d%H%M%S")
        batch_output.to_csv(f"batch_output_{timestamp}.txt", index=False)
        metrics.to_csv(f"batch_eval_output_{timestamp}.txt", index=False)
    return dump_output

from runflow_local import runflow

# add main function to run the evaluation
if __name__ == "__main__":
    # Load the batch output from runflow
    batch_output = runflow(dump_output=True)
    eval_output = eval_all(batch_output, dump_output=True)
    logger.info(eval_output)
    
   