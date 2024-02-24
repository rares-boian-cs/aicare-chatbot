from sklearn.linear_model import LogisticRegression
import pickle
import pandas as pd
from sklearn.svm import SVC
import numpy as np
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn import metrics
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn.base import TransformerMixin, clone
import os
import argparse
from sklearn.base import BaseEstimator, TransformerMixin

class IdentityTransformer(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, input_array, y=None):
        return self

    def transform(self, input_array, y=None):
        return input_array*1

CHECKPOINTS_PATH = 'checkpoints'
DATA_PATH = 'data/annotated_data'
EMBS_PATH = 'data/embeddings'
REPORT_PATH = 'results'

config = {
    'tfidf': TfidfVectorizer,
    'bow': CountVectorizer,
    'identity': IdentityTransformer,

    'svm': SVC,
    'rf': RandomForestClassifier,
    'lr': LogisticRegression,
    'adaboost': AdaBoostClassifier,

    'cv_params': {
        'svm': {
            'classifier__kernel': ['linear', 'poly', 'rbf', 'sigmoid'],
            'classifier__C': [0.001, 0.01, 0.1, 1, 10, 100],
            'classifier__gamma': [0.0001, 0.001, 0.01, 0.1],
            'classifier__probability': [True]
        },
        'rf': {
            'classifier__bootstrap': [True],
            'classifier__n_jobs': [5],
            'classifier__max_depth': [10, 50, 100, None],
            'classifier__max_features': ['auto'],
            'classifier__min_samples_leaf': [1, 2, 4],
            'classifier__min_samples_split': [2, 5, 10],
            'classifier__n_estimators': [5, 10, 100]
        },
        'lr': {
            'classifier__solver': ['liblinear'],
            'classifier__penalty': ['l1', 'l2'],
            'classifier__C': [0.0001, 0.001, 0.01, 0.1, 1, 10, 100]
        },
        'adaboost': {
            'classifier__n_estimators': [5, 10, 100],
        }
    }
}

def compute_acr_score(y_val, preds_val, questionnaire):
    if questionnaire == 'phq' or questionnaire == 'gad':
        #maximum absolute difference
        mad = 4
    elif questionnaire == 'pcl':
        mad = 5

    difference = np.array(y_val) - np.array(preds_val)
    acr = np.mean((mad - np.absolute(difference)) / mad)

    return acr


def grid_search(X_train, y_train, vectorizer, classifier):

    pipeline = Pipeline([
        ('vectorizer', config[vectorizer]()),
        ('classifier', config[classifier]())
    ])

    parameters = config['cv_params'][classifier]

    grid_search_tune = GridSearchCV(pipeline, parameters, cv=2, n_jobs=15, verbose=3, scoring='f1_macro')
    grid_search_tune.fit(X_train, y_train)

    print("Best parameters set:")
    print(grid_search_tune.best_estimator_.steps)
    print(grid_search_tune.best_params_)

    return clone(grid_search_tune.best_estimator_), grid_search_tune.best_params_, grid_search_tune.best_estimator_.steps


def k_fold_cross_validation(X, y, embeddings_type, vectorizer, classifier):

    X_texts = X
    if embeddings_type:
        with open(f'{EMBS_PATH}/{questionnaire}/{embeddings_type}_train.pkl', 'rb') as f:
            X = pickle.load(f)

    skf = StratifiedKFold(n_splits = 5, random_state = 42, shuffle = True)

    val_scores = []
    precision_scores = []
    recall_scores = []
    f1_scores_macro = []
    f1_scores_weighted = []
    acr_scores = []

    report_dict = {'questionnaire': [], 'vectorizer': [], 'embeddings_type': [], 'classifier': [], 'accuracy': [], 'precision': [], 'recall': [], 'f1_weighted': [], 'f1_macro': [], 'acr': []}

    for idx, (train_index, val_index) in enumerate(skf.split(X, y)):
        X_train_texts, X_val_texts = X_texts[train_index], X_texts[val_index]
        X_train, X_val = X[train_index], X[val_index]
        y_train, y_val = y[train_index], y[val_index]

        best_estimator, params1, params2 = grid_search(X_train, y_train, vectorizer, classifier)

        best_estimator.fit(X_train, y_train.astype(np.float32))

        print('Fold ', idx)
        print('Vectorizer ', vectorizer)
        if embeddings_type:
            print('Embeddings', embeddings_type)
        print('Classifier ', classifier)

        preds_val = best_estimator.predict(X_val)
        preds_proba_val = best_estimator.predict_proba(X_val)

        print("Train score", best_estimator.score(X_train, y_train))
        print("Val score", best_estimator.score(X_val, y_val))
        print("Precision", metrics.precision_score(y_val, preds_val, average = 'weighted'))
        print("Recall", metrics.recall_score(y_val, preds_val, average = 'weighted'))
        val_f1_macro = metrics.f1_score(y_val, preds_val, average = 'macro')
        val_f1_weighted = metrics.f1_score(y_val, preds_val, average = 'weighted')
        print("F1 score macro", val_f1_macro)
        print("F1 score weighted", val_f1_weighted)

        acr = compute_acr_score(y_val, preds_val, questionnaire)

        if embeddings_type:
            current_path = f'{CHECKPOINTS_PATH}/{questionnaire}/f={idx}-{vectorizer}-{classifier}-{embeddings_type}_f1={np.round(val_f1_macro, 4)}.pkl'
        else:
            current_path = f'{CHECKPOINTS_PATH}/{questionnaire}/f={idx}-{vectorizer}-{classifier}_f1={np.round(val_f1_macro, 4)}.pkl'
        os.makedirs(f'{CHECKPOINTS_PATH}/{questionnaire}', exist_ok = True)

        with open(current_path, 'wb') as f:
            pickle.dump(best_estimator, f)

        classification_report = metrics.classification_report(y_val, preds_val)

        os.makedirs(f'{REPORT_PATH}/{questionnaire}', exist_ok = True)

        with open(f'{REPORT_PATH}/{questionnaire}/classification_reports.txt', 'at') as f:
            f.write(f'fold_idx={idx}\nbest model: \n{classifier}/f={idx}-{vectorizer}-{classifier}-{embeddings_type}_f1={np.round(val_f1_macro, 4)}.pkl\nparams:\n{params1}\n{params2}\n\n{classification_report}\n\n')

        errors = {'answer': [], 'prediction': [], 'prediction_proba': [], 'groundtruth': []}
        for idx_item in np.argwhere(preds_val != y_val).ravel():
            print(X_val_texts[idx_item], f'{preds_val[idx_item]} ({np.round(preds_proba_val[idx_item], 4)}) / {y_val[idx_item]}')
            errors['answer'].append(X_val_texts[idx_item])
            errors['prediction_proba'].append(np.round(preds_proba_val[idx_item], 4))
            errors['prediction'].append(preds_val[idx_item])
            errors['groundtruth'].append(y_val[idx_item])
        errors_df = pd.DataFrame.from_dict(errors)
        errors_df.to_csv(f'{REPORT_PATH}/{questionnaire}/{vectorizer}-{classifier}-{embeddings_type}_fold_idx={idx}_errors={len(errors_df)}.csv', index = False)

        val_scores.append(best_estimator.score(X_val, y_val))
        precision_scores.append(metrics.precision_score(y_val, preds_val, average = 'weighted'))
        recall_scores.append(metrics.recall_score(y_val, preds_val, average = 'weighted'))
        f1_scores_macro.append(val_f1_macro)
        f1_scores_weighted.append(val_f1_weighted)
        acr_scores.append(acr)

    mean_acc = np.round(np.mean(val_scores), 4)
    print("Mean Val score", mean_acc)
    mean_prec = np.round(np.mean(precision_scores), 4)
    print("Mean Precision", mean_prec)
    mean_rec = np.round(np.mean(recall_scores), 4)
    print("Mean Recall", mean_rec)
    mean_f1_macro = np.round(np.mean(f1_scores_macro), 4)
    print("Mean F1 score macro", mean_f1_macro)
    mean_f1_weighted = np.round(np.mean(f1_scores_weighted), 4)
    print("Mean F1 score weighted", mean_f1_weighted)
    mean_acr = np.round(np.mean(acr_scores), 4)
    print("Mean ACR", mean_acr)

    report_dict['vectorizer'].append(vectorizer)
    report_dict['classifier'].append(classifier)
    report_dict['embeddings_type'].append(embeddings_type)
    report_dict['accuracy'].append(mean_acc)
    report_dict['precision'].append(mean_prec)
    report_dict['recall'].append(mean_rec)
    report_dict['f1_macro'].append(mean_f1_macro)
    report_dict['f1_weighted'].append(mean_f1_weighted)
    report_dict['acr'].append(mean_acr)

    csv_report_path = f'{REPORT_PATH}/{questionnaire}/mean_classification_reports.csv'
    if(not os.path.exists(csv_report_path)):
         with open(csv_report_path, 'at') as f:
            f.write(f'vectorizer,classifier,embeddings_type,accuracy,precision,recall,f1_weighted,f1_macro\n')

    with open(csv_report_path, 'at') as f:
        f.write(f'{vectorizer},{classifier},{embeddings_type},{mean_acc},{mean_prec},{mean_rec},{mean_f1_weighted},{mean_f1_macro}, {mean_acr}\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--embeddings_type', type = str, required = False)
    parser.add_argument('--vectorizer', type = str, required = True)
    parser.add_argument('--classifier', type = str, required = True)
    parser.add_argument('--questionnaire', type = str, required = True)

    args = parser.parse_args()
    embeddings_type = args.embeddings_type
    vectorizer = args.vectorizer
    classifier = args.classifier
    questionnaire = args.questionnaire

    data_df = pd.read_csv(f'{DATA_PATH}/{questionnaire}_train.csv')

    X = data_df['answer'].values
    y = data_df['label'].values

    k_fold_cross_validation(X, y, embeddings_type, vectorizer, classifier)
