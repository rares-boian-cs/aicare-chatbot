from sentence_transformers import SentenceTransformer
import os
import torch
import pickle
import argparse
import pandas as pd

parser = argparse.ArgumentParser(description='Do stuff.')
parser.add_argument('--embeddings_type', type = str, required = True)
parser.add_argument('--questionnaire', type = str, required = True)

args = parser.parse_args()
embeddings_type = args.embeddings_type
questionnaire = args.questionnaire

DATA_PATH = 'data/annotated_data'
EMBS_PATH = 'data/embeddings/'

if embeddings_type == 'bert':
	model_name = 'bert-base-uncased'

if embeddings_type == 'distilbert':
	model_name = 'distilbert-base-uncased'

elif embeddings_type == 'roberta':
	model_name = 'roberta-base'

elif embeddings_type == 'minilm':
	model_name = 'all-MiniLM-L12-v2'

elif embeddings_type == 'mental-bert':
	model_name = 'local-models/mental-bert-base-uncased'

elif embeddings_type == 'mental-roberta':
	model_name = 'local-models/mental-roberta-base'

text_encoder = SentenceTransformer(model_name).cuda()
text_encoder.eval()
text_encoder.train(False)

for split in ['train', 'test']:

	data_df = pd.read_csv(f'{DATA_PATH}/{questionnaire}_{split}.csv')
	data = data_df['answer']

	with torch.no_grad():
		encoded_texts = text_encoder.encode(data, batch_size = 128, show_progress_bar = True)

	os.makedirs(f'{EMBS_PATH}/{questionnaire}', exist_ok = True)

	with open(f'{EMBS_PATH}/{questionnaire}/{embeddings_type}_{split}.pkl', 'wb') as f:
		pickle.dump(encoded_texts, f)
