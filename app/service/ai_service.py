import os
import pickle
import sys

from sentence_transformers import SentenceTransformer

from common.constant import EvaluationCode
from common.identity_transformer import IdentityTransformer


class AiService:
    def __init__(self):
        path = f"{os.path.dirname(__file__)}/../resources/ai-model"
        self.model: dict[EvaluationCode,] = {}
        sys.modules['__main__'].IdentityTransformer = IdentityTransformer
        self.text_encoder = SentenceTransformer('distilbert-base-uncased').to('cpu')

        for e in [EvaluationCode.PHQ_9, EvaluationCode.GAD_7, EvaluationCode.PCL_5]:
            with open(f"{path}/{e.value}.pkl", "rb") as f:
                self.model[e] = pickle.load(f)

    def predict_answer(self, question: str, lines: list[str], evaluation_code: EvaluationCode):
        if evaluation_code not in self.model:
            return None

        text = " ".join(lines)
        return self.model[evaluation_code].predict_proba([text])
