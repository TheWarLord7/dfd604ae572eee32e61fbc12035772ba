import pandas as pd
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

# --- CONFIGURATION (must match vector.py) ---
CSV_PATH = r"D:\Saigeetha\templeresearch\oldtempleblogspot_new.csv"
DB_LOCATION = r".\vector_data"
COLLECTION_NAME = "ancient_temples"
EMBEDDING_MODEL = 'nomic-embed-text:v1.5'
TEXT_COLUMN = 'page_content'  # Column to embed
# -------------------------------------------

print("Loading CSV...")
df = pd.read_csv(CSV_PATH)

# Extract texts to embed and metadata (all other columns)
texts = df[TEXT_COLUMN].astype(str).tolist()
metadata_cols = [col for col in df.columns if col != TEXT_COLUMN]
metadatas = df[metadata_cols].to_dict('records')

print(f"Loaded {len(texts)} records from CSV")
print(f"Text column: '{TEXT_COLUMN}'")
print(f"Metadata columns: {metadata_cols}")

# Initialize embedding function (same as in vector.py)
print(f"Initializing embedding model: {EMBEDDING_MODEL}")
embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

# Create vector store from texts (automatically persists if persist_directory is set)
print("Creating vector embeddings and storing to ChromaDB...")
vector_store = Chroma.from_texts(
    texts=texts,
    embedding=embeddings,
    metadatas=metadatas,
    collection_name=COLLECTION_NAME,
    persist_directory=DB_LOCATION
)

# NOTE: No need to call .persist() – Chroma.from_texts already persists when persist_directory is given
print(f"✅ Vector store created with {len(texts)} documents")
print(f"Stored at: {DB_LOCATION}")