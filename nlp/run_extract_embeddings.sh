#!/bin/bash
set -e

python extract_embeddings.py --embeddings_type bert --questionnaire phq
python extract_embeddings.py --embeddings_type bert --questionnaire gad
python extract_embeddings.py --embeddings_type bert --questionnaire pcl

python extract_embeddings.py --embeddings_type distilbert --questionnaire phq
python extract_embeddings.py --embeddings_type distilbert --questionnaire gad
python extract_embeddings.py --embeddings_type distilbert --questionnaire pcl

python extract_embeddings.py --embeddings_type roberta --questionnaire phq
python extract_embeddings.py --embeddings_type roberta --questionnaire gad
python extract_embeddings.py --embeddings_type roberta --questionnaire pcl

python extract_embeddings.py --embeddings_type minilm --questionnaire phq
python extract_embeddings.py --embeddings_type minilm --questionnaire gad
python extract_embeddings.py --embeddings_type minilm --questionnaire pcl

python extract_embeddings.py --embeddings_type mental-bert --questionnaire phq
python extract_embeddings.py --embeddings_type mental-bert --questionnaire gad
python extract_embeddings.py --embeddings_type mental-bert --questionnaire pcl

python extract_embeddings.py --embeddings_type mental-roberta --questionnaire phq
python extract_embeddings.py --embeddings_type mental-roberta --questionnaire gad
python extract_embeddings.py --embeddings_type mental-roberta --questionnaire pcl
