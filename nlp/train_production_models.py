import pickle
import pandas as pd
from sklearn.svm import SVC
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.base import TransformerMixin, clone
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn import metrics


MODEL_PATHS = 'checkpoints/production_models'
EMBS_PATH = 'data/embeddings'
DATA_PATH = 'data/annotated_data'

class IdentityTransformer(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, input_array, y=None):
        return self

    def transform(self, input_array, y=None):
        return input_array*1

config = {
    'tfidf': TfidfVectorizer,
    'identity': IdentityTransformer,

    'svm': SVC,
    'lr': LogisticRegression
}

config_parameters = {
    'phq-tfidf-lr-None': {'C': 10, 'penalty': 'l1', 'solver': 'liblinear'},
    'gad-tfidf-svm-None': {'C': 100, 'gamma': 0.1, 'kernel': 'rbf', 'probability': True},
    'pcl-tfidf-svm-None': {'C': 10, 'gamma': 0.1, 'kernel': 'rbf', 'probability': True}
}


def train():
    #train one model for each questionnaire
    for questionnaire in ['phq', 'gad', 'pcl']:

        print('Training model for...', questionnaire)
        
        data_df = pd.read_csv(f'{DATA_PATH}/{questionnaire}_train.csv')
        test_df = pd.read_csv(f'{DATA_PATH}/{questionnaire}_test.csv')

        X_train = data_df['answer'].values
        y_train = data_df['label'].values

        X_test = test_df['answer'].values
        y_test = test_df['label'].values

        questionnaire_dict = {k: v for k, v in config_parameters.items() if k.startswith(questionnaire)}
        
        _, vectorizer, classifier, embeddings_type = list(questionnaire_dict)[0].split('-')
       
        if embeddings_type != 'None':
            with open(f'{EMBS_PATH}/{questionnaire}/{embeddings_type}_train.pkl', 'rb') as f:
                X_train = pickle.load(f)
            with open(f'{EMBS_PATH}/{questionnaire}/{embeddings_type}_test.pkl', 'rb') as f:
                X_test = pickle.load(f)

        print('classifier', type(config[classifier]()))
        print('vectorizer', type(config[vectorizer]()))

        parameters = list(questionnaire_dict.values())[0]

        pipeline = Pipeline([
            ('vectorizer', config[vectorizer]()),
            ('classifier', config[classifier](**parameters))
        ])

        print('Training model..')
        pipeline.fit(X_train, y_train)

        preds_val = pipeline.predict(X_test)

        print("Train score", pipeline.score(X_train, y_train))
        print("Val score", pipeline.score(X_test, y_test))
        print("Precision", metrics.precision_score(y_test, preds_val, average = 'weighted'))
        print("Recall", metrics.recall_score(y_test, preds_val, average = 'weighted'))
        test_f1_macro = metrics.f1_score(y_test, preds_val, average = 'macro')
        test_f1_weighted = metrics.f1_score(y_test, preds_val, average = 'weighted')
        print("F1 score macro", test_f1_macro)
        print("F1 score weighted", test_f1_weighted)

        print('Saving model..')
        print('\n\n')

        with open(f'{MODEL_PATHS}/{questionnaire}.pkl', 'wb') as f:
            pickle.dump(pipeline, f)

if __name__ == '__main__':
    train()


