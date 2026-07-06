from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import time
import json
import os

embeddings = OllamaEmbeddings(model='nomic-embed-text:v1.5')

db_loc = './vector_data'

vector_store = Chroma(
    collection_name='ancient_temples',
    persist_directory = db_loc,
    embedding_function=embeddings
)

retreiver = vector_store.as_retriever(
    search_kwargs = {'k':5}
)
