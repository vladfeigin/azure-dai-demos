from datetime import datetime
from variant import Variant

# create a class EvaluationMetaData which contains following metadata:
# evaluation name
#timestamp ,(type : datetime.datetime)
#evaluation_id
#evaluation description
#user running the evaluation
#application name
#variant of Type Variant
class EvaluationMetaData:
    def __init__(self, evaluation_name: str, timestamp: datetime, evaluation_id: str, evaluation_description: str, user_running_evaluation: str, application_name: str, variant: Variant) -> None:
        self.evaluation_name = evaluation_name
        self.timestamp = datetime.now()
        self.evaluation_id = evaluation_id #prompt flow run id
        self.evaluation_description = evaluation_description
        self.user_running_evaluation = user_running_evaluation
        self.application_name = application_name
        self.variant = variant #evalaution variant, see variant.py for more details
    
    def to_dict(self) -> dict:
        return {
            'evaluation_name': self.evaluation_name,
            'timestamp': self.timestamp.isoformat(), #convert the datetime object to an ISO 8601 formatted string, which is JSON serializable.
            'evaluation_id': self.evaluation_id,
            'evaluation_description': self.evaluation_description,
            'user_running_evaluation': self.user_running_evaluation,
            'application_name': self.application_name,
            'variant': self.variant.to_dict()
        }
        
    def __str__(self) -> str:
        return f"Evaluation Name: {self.evaluation_name}, Timestamp: {self.timestamp}, Evaluation ID: {self.evaluation_id}, Evaluation Description: {self.evaluation_description}, User Running Evaluation: {self.user_running_evaluation}, Application Name: {self.application_name}, Variant: {self.variant}"
    
    def __repr__(self) -> str:
        return f"Evaluation Name: {self.evaluation_name}, Timestamp: {self.timestamp}, Evaluation ID: {self.evaluation_id}, Evaluation Description: {self.evaluation_description}, User Running Evaluation: {self.user_running_evaluation}, Application Name: {self.application_name}, Variant: {self.variant}"

    # create a method which returns the evaluation name
    def get_evaluation_name(self) -> str:
        return self.evaluation_name
    
    # create a method which sets the evaluation name
    def set_evaluation_name(self, evaluation_name: str) -> None:
        self.evaluation_name = evaluation_name
    
    # create a methos return evaluation id
    def get_evaluation_id(self) -> str:
        return self.evaluation_id
    
    #create a method whihch sets the evaluation id
    def set_evaluation_id(self, evaluation_id: str) -> None:
        self.evaluation_id = evaluation_id
        
    #create a method which returns the evaluation description
    def get_evaluation_description(self) -> str:
        return self.evaluation_description
    
    #create a method which sets the evaluation description
    def set_evaluation_description(self, evaluation_description: str) -> None:
        self.evaluation_description = evaluation_description
        
    #create a method which returns the user running the evaluation
    def get_user_running_evaluation(self) -> str:
        return self.user_running_evaluation
        