from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
import time
import json
import csv
import os

# KEY = os.getenv('OPENROUTER3')

embeddings = OllamaEmbeddings(model='nomic-embed-text:v1.5')
# embeddings = OpenAIEmbeddings(
#     model="nvidia/nemotron-3-embed-1b:free",
#     base_url="https://openrouter.ai/api/v1",
#     api_key=KEY,
#     check_embedding_ctx_length=False
# )


db_loc = './vector_data'

vector_store = Chroma(
    collection_name='ancient_temples',
    persist_directory = db_loc,
    embedding_function=embeddings
)

# docs = []
# ids = []

# with open('t2.csv') as f:
#     reader = csv.reader(f)
#     next(reader)

#     while True:
#         try:
#             data = next(reader)
#             docs.append(
#                 Document(
#                     data[-1],
#                     metadata = {'temple_name': data[3], 'deities': data[4], 'location': data[5], 'nearby_town': data[6],
#                                 'district': data[7], 'dynasty': data[8], 'condition': data[9], 
#                                 'functional_status': data[10], 'accessability': data[11]},
#                     id=str(data[0])
#                 )
#             )
#             ids.append(str(data[0]))

#         except StopIteration:
#             vector_store.add_documents(documents=docs, ids=ids)


retreiver = vector_store.as_retriever(
    search_kwargs = {'k':35}
)