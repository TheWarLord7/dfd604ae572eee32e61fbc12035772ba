import pprint
from vector import vector_store

def run_diagnostics():
    print("=" * 60)
    print("CHROMA VECTOR DATABASE DIAGNOSTIC UTILITY")
    print("=" * 60)

    # 1. Fetch total count of embedded documents
    try:
        total_chunks = vector_store._collection.count()
        print(f"[*] Total Document Chunks in 'ancient_temples': {total_chunks}")
    except Exception as e:
        print(f"[!] Failed to fetch collection count: {e}")
        return

    if total_chunks == 0:
        print("[!] WARNING: The vector database collection is completely empty.")
        print("    You must run an ingestion/population script before querying.")
        return

    # 2. Inspect a structural sample of records (Modify limit to see more)
    print(f"\n[*] Fetching a sample of data chunks to inspect format...")
    try:
        # We fetch IDs, documents (text contents), and metadata
        db_contents = vector_store.get(limit=5, include=["documents", "metadatas"])
        
        for i in range(len(db_contents['ids'])):
            chunk_id = db_contents['ids'][i]
            document_text = db_contents['documents'][i] if db_contents['documents'] else "No text content available"
            metadata_dict = db_contents['metadatas'][i] if db_contents['metadatas'] else {}

            print(f"\n--- [Sample Record {i+1}] ID: {chunk_id} ---")
            print("▶ METADATA KEY/VALUES:")
            if metadata_dict:
                pprint.pprint(metadata_dict)
            else:
                print("  (No metadata found attached to this chunk - pure vector search dependent)")
                
            print("▶ TEXT CONTENT (First 350 chars):")
            # Cleaning up string views for readability
            clean_text = document_text.replace('\n', ' ').strip()
            print(f"  \"{clean_text[:350]}...\"")
            print("-" * 50)

    except Exception as e:
        print(f"[!] Error while dumping database elements: {e}")

    # 3. Targeted string inspection to diagnose the "Uthiramerur" issue
    target_keyword = "Uthiramerur"
    print(f"\n[*] Searching database for exact keyword reference: '{target_keyword}'...")
    
    try:
        # Local search directly via SQLite text matching rather than embedding vectors
        all_data = vector_store.get(include=["documents"])
        matching_count = 0
        
        for text in all_data['documents']:
            if target_keyword.lower() in text.lower():
                matching_count += 1
                
        print(f"[*] Result: Found the word '{target_keyword}' in {matching_count} data chunks.")
        if matching_count == 0:
            print(f"    [!] CRITICAL: The data layer does not contain any records for '{target_keyword}'.")
            print("        This is why your retriever is returning empty documents to the LLM.")
            
    except Exception as e:
        print(f"[!] Keyword scan dropped: {e}")

if __name__ == "__main__":
    run_diagnostics()