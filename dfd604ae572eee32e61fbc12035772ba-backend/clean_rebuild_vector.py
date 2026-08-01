import re
import shutil
from pathlib import Path

import pandas as pd
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

BASE_DIR = Path(__file__).resolve().parent
RAW_CSV_PATH = BASE_DIR / 'oldtempleblogspot_new.csv'
CSV_PATH = BASE_DIR / 'vectordb_export.csv'
CLEAN_CSV_PATH = BASE_DIR / 'vectordb_export_clean.csv'
DB_LOCATION = BASE_DIR / 'vector_data'
COLLECTION_NAME = 'ancient_temples'
MODEL_NAME = 'nomic-embed-text:v1.5'

NOISE_PATTERNS = [
    r'(?i)\bcan\s*[\'’]t\s+load\s+alternatives\b',
    r'(?i)\btry\s+again\b',
    r'(?i)\bcan\s*[\'’]t\s+load\s+alternatives\s+try\s+again\b',
    r'(?i)\bcan\s*[\'’]t\s+load\s+alternatives\s*try\s*again\b',
    r'(?i)\bcan\s*[\'’]t\s+load\s+alternatives\s*\*\s*try\s+again\b',
]


def dedupe_repeated_sentences(text: str) -> str:
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    cleaned = []
    prev = None
    for part in parts:
        part = re.sub(r'\s+', ' ', part.strip())
        if not part:
            continue
        lower = part.lower()
        if 'can\'t load alternatives' in lower or 'try again' in lower:
            continue
        if prev is not None and lower == prev.lower():
            continue
        cleaned.append(part)
        prev = part
    return ' '.join(cleaned).strip()


def normalize_text(value: str) -> str:
    text = str(value or '').replace('\u00a0', ' ')
    text = text.replace('\\n', ' ')
    text = text.replace('\n', ' ')
    text = text.replace('\r', ' ')
    text = text.replace('“', ' ').replace('”', ' ')
    for pattern in NOISE_PATTERNS:
        text = re.sub(pattern, ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'(?i)(\b[^.!?]+\b)(?:\s+\1)+', r'\1', text)
    text = re.sub(r'\s+([,.;:!?])', r'\1', text)
    text = dedupe_repeated_sentences(text)
    text = re.sub(r'\s+([,.;:!?])', r'\1', text)
    text = re.sub(r'\.{2,}', '.', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()


def load_clean_dataframe() -> pd.DataFrame:
    source_path = RAW_CSV_PATH if RAW_CSV_PATH.exists() else CSV_PATH
    if not source_path.exists():
        raise FileNotFoundError(f'CSV source not found: {source_path}')

    df = pd.read_csv(source_path)

    if 'page_content' in df.columns:
        text_col = 'page_content'
    elif 'Raw Text Content' in df.columns:
        text_col = 'Raw Text Content'
    else:
        raise ValueError(f'CSV does not contain a usable text column: {source_path}')

    original_count = len(df)
    df = df[[text_col]].copy()
    df.columns = ['text']
    df['text'] = df['text'].fillna('').astype(str)
    df['normalized'] = df['text'].map(normalize_text)
    df = df[df['normalized'].str.len() > 40].copy()
    df = df.drop_duplicates(subset='normalized', keep='first').reset_index(drop=True)

    print(f'CSV rows before cleaning: {original_count}')
    print(f'CSV rows after cleaning: {len(df)}')
    print(f'Duplicates removed: {original_count - len(df)}')
    print(f'Using source CSV: {source_path.name}')

    return df[['normalized']].rename(columns={'normalized': 'text'})


def rebuild_vector_store(clean_df: pd.DataFrame):
    if DB_LOCATION.exists():
        backup_dir = BASE_DIR / 'vector_data_backup_before_clean'
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        shutil.move(str(DB_LOCATION), str(backup_dir))
        print(f'Backed up old DB to: {backup_dir}')

    texts = clean_df['text'].astype(str).tolist()
    embeddings = OllamaEmbeddings(model=MODEL_NAME)
    Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(DB_LOCATION),
    )
    print(f'Rebuilt clean vector database at: {DB_LOCATION}')
    print(f'Inserted record count: {len(texts)}')


def main():
    clean_df = load_clean_dataframe()
    clean_df.to_csv(CLEAN_CSV_PATH, index=False)
    print(f'Clean CSV written to: {CLEAN_CSV_PATH}')
    rebuild_vector_store(clean_df)


if __name__ == '__main__':
    main()
