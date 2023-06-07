# -*- coding: utf-8 -*-
"""Assignment_4_NLP.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1yLUurJ-h0JR1J5Wfb23aqzMoBBLmq069

installing sentence BERT python library
"""

"""Reading the duplicate questions and xml file (Similar to Assignment-3)"""

import csv
from post_parser_record import PostParserRecord

def read_tsv_test_data(file_path):
  # Takes in the file path for test file and generate a dictionary
  # of question id as the key and the list of question ids similar to it
  # as value. It also returns the list of all question ids that have
  # at least one similar question
  dic_similar_questions = {}
  lst_all_test = []
  with open(file_path) as fd:
    rd = csv.reader(fd, delimiter="\t", quotechar='"')
    for row in rd:
        question_id = int(row[0])
        lst_similar = list(map(int, row[1:]))
        dic_similar_questions[question_id] = lst_similar
        lst_all_test.append(question_id)
        lst_all_test.extend(lst_similar)
  return dic_similar_questions, lst_all_test

dic_similar_questions, lst_all_test = read_tsv_test_data("duplicate_questions.tsv")
post_reader = PostParserRecord("Posts_law.xml")

"""Using pre-trained Quora duplicate question to encode questions and find similar questions"""

from sentence_transformers import SentenceTransformer, util
import torch

# in question one, we are using the pre-trained model on quora with no further fine-tuning
model_name = 'distilbert-base-nli-stsb-quora-ranking'
model = SentenceTransformer(model_name)

# list of text to be indexed (encoded)
corpus = []
# this dictionary is used as key: corpus index [0, 1, 2, ...] and value: corresponding question id
index_to_question_id = {}
idx = 0

# indexing all the questions in the law stack exchange -- only using the question titles
for question_id in post_reader.map_questions:
  question = post_reader.map_questions[question_id]
  text = question.title
  q_id = question.post_id
  corpus.append(text)
  index_to_question_id[idx] = question_id
  idx += 1

# Indexing (embedding) the 
corpus_embeddings = model.encode(corpus, convert_to_tensor=True, show_progress_bar=True)

lst_test_question_ids = list(dic_similar_questions.keys())
top_k = 100

for question_id in lst_test_question_ids:
  query_text = post_reader.map_questions[question_id].title
  query_embedding = model.encode(query_text, convert_to_tensor=True)

  # We use cosine-similarity and torch.topk to find the highest 5 scores
  cos_scores = util.cos_sim(query_embedding, corpus_embeddings)[0]
  top_results = torch.topk(cos_scores, k=top_k)
  for score, idx in zip(top_results[0], top_results[1]):
    index = int(idx)
    # printing question id and similarity score
    print(index_to_question_id[index], "(Score: {:.4f})".format(score))

# Calculate P@1

p = 0
for question_id in dic_similar_questions:
  try:
    if index_to_question_id[question_id] == dic_similar_questions[question_id][0]:
      p = p + 1
  finally:
    continue
p_total = p / len(dic_similar_questions)

print("P@1 : " + str(p_total))

# Calculate MRR

i = 0
j = 0
temp = 0
for i in range(len(dic_similar_questions)):
  for j in range(len(index_to_question_id)):

    if index_to_question_id[j] == dic_similar_questions[i]:
      temp = temp + (1 / j)
      break

    else:
      j = j+1
      continue
  print(i)
  i += 1

print(temp)


