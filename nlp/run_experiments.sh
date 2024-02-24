#!/bin/bash
set -e

python classification_experiments_cross_validation.py --vectorizer bow --classifier rf --questionnaire gad
python classification_experiments_cross_validation.py --vectorizer tfidf --classifier lr --questionnaire gad
python classification_experiments_cross_validation.py --vectorizer tfidf --classifier rf --questionnaire gad
python classification_experiments_cross_validation.py --vectorizer tfidf --classifier svm --questionnaire gad

python classification_experiments_cross_validation.py --vectorizer bow --classifier rf --questionnaire phq
python classification_experiments_cross_validation.py --vectorizer tfidf --classifier lr --questionnaire phq
python classification_experiments_cross_validation.py --vectorizer tfidf --classifier rf --questionnaire phq
python classification_experiments_cross_validation.py --vectorizer tfidf --classifier svm --questionnaire phq

python classification_experiments_cross_validation.py --vectorizer bow --classifier rf --questionnaire pcl
python classification_experiments_cross_validation.py --vectorizer tfidf --classifier lr --questionnaire pcl
python classification_experiments_cross_validation.py --vectorizer tfidf --classifier rf --questionnaire pcl
python classification_experiments_cross_validation.py --vectorizer tfidf --classifier svm --questionnaire pcl

python classification_experiments_cross_validation.py --vectorizer bow --classifier naive_bayes --questionnaire gad
python classification_experiments_cross_validation.py --vectorizer tfidf --classifier naive_bayes --questionnaire gad

python classification_experiments_cross_validation.py --embeddings_type bert --vectorizer identity --classifier lr --questionnaire gad
python classification_experiments_cross_validation.py --embeddings_type bert --vectorizer identity --classifier rf --questionnaire gad
python classification_experiments_cross_validation.py --embeddings_type bert --vectorizer identity --classifier svm --questionnaire gad
python classification_experiments_cross_validation.py --embeddings_type bert --vectorizer identity --classifier adaboost --questionnaire gad

python classification_experiments_cross_validation.py --embeddings_type distilbert --vectorizer identity --classifier lr --questionnaire gad
python classification_experiments_cross_validation.py --embeddings_type distilbert --vectorizer identity --classifier rf --questionnaire gad
python classification_experiments_cross_validation.py --embeddings_type distilbert --vectorizer identity --classifier svm --questionnaire gad
python classification_experiments_cross_validation.py --embeddings_type distilbert --vectorizer identity --classifier adaboost --questionnaire gad

python classification_experiments_cross_validation.py --embeddings_type roberta --vectorizer identity --classifier lr --questionnaire gad
python classification_experiments_cross_validation.py --embeddings_type roberta --vectorizer identity --classifier rf --questionnaire gad
python classification_experiments_cross_validation.py --embeddings_type roberta --vectorizer identity --classifier svm --questionnaire gad
python classification_experiments_cross_validation.py --embeddings_type roberta --vectorizer identity --classifier adaboost --questionnaire gad

python classification_experiments_cross_validation.py --embeddings_type minilm --vectorizer identity --classifier lr --questionnaire gad
python classification_experiments_cross_validation.py --embeddings_type minilm --vectorizer identity --classifier rf --questionnaire gad
python classification_experiments_cross_validation.py --embeddings_type minilm --vectorizer identity --classifier svm --questionnaire gad
python classification_experiments_cross_validation.py --embeddings_type minilm --vectorizer identity --classifier adaboost --questionnaire gad

python classification_experiments_cross_validation.py --embeddings_type mental-bert --vectorizer identity --classifier lr --questionnaire gad
python classification_experiments_cross_validation.py --embeddings_type mental-bert --vectorizer identity --classifier rf --questionnaire gad
python classification_experiments_cross_validation.py --embeddings_type mental-bert --vectorizer identity --classifier svm --questionnaire gad
python classification_experiments_cross_validation.py --embeddings_type mental-bert --vectorizer identity --classifier adaboost --questionnaire gad

python classification_experiments_cross_validation.py --embeddings_type mental-roberta --vectorizer identity --classifier lr --questionnaire gad
python classification_experiments_cross_validation.py --embeddings_type mental-roberta --vectorizer identity --classifier rf --questionnaire gad
python classification_experiments_cross_validation.py --embeddings_type mental-roberta --vectorizer identity --classifier svm --questionnaire gad
python classification_experiments_cross_validation.py --embeddings_type mental-roberta --vectorizer identity --classifier adaboost --questionnaire gad
