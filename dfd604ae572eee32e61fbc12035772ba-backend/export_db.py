import csv
import os
from vector import vector_store

def export_database_to_csv():
    output_filename = "vectordb_export.csv"
    
    print("=" * 60)
    print("VECTOR DATABASE EXPORT TO SPREADSHEET")
    print("=" * 60)
    
    # 1. Fetch ALL documents from the collection
    print("[*] Extracting all entries from Chroma collection 'ancient_temples'...")
    try:
        # include elements cleanly
        all_data = vector_store.get(include=["documents", "metadatas"])
        
        ids = all_data.get('ids', [])
        documents = all_data.get('documents', [])
        metadatas = all_data.get('metadatas', [])
        
        total_records = len(ids)
        print(f"[*] Found {total_records} total document chunks to export.")
        
        if total_records == 0:
            print("[!] Database is empty. Aborting export.")
            return

        # 2. Write structural contents out to CSV
        print(f"[*] Compiling rows and writing to {output_filename}...")
        
        with open(output_filename, mode='w', encoding='utf-8', newline='') as csv_file:
            # Dynamically determine column names based on metadata keys found plus core fields
            fieldnames = ['Chunk ID', 'Character Count', 'Temple Name Metadata', 'Raw Text Content']
            
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            
            for i in range(total_records):
                text_content = documents[i] if documents else ""
                metadata = metadatas[i] if metadatas else {}
                
                # Extract temple name dynamically if it exists
                temple_name = metadata.get('Temple Name', 'N/A')
                
                # Format text content nicely for standard row representation
                clean_text = text_content.strip()
                
                writer.writerow({
                    'Chunk ID': ids[i],
                    'Character Count': len(clean_text),
                    'Temple Name Metadata': temple_name,
                    'Raw Text Content': clean_text
                })
                
        print(f"[✓] SUCCESS! Data successfully exported to: {os.path.abspath(output_filename)}")
        print("[*] You can now open this file directly in Excel to inspect or clean the records.")

    except Exception as e:
        print(f"[!] Critical structural failure during extraction: {e}")

if __name__ == "__main__":
    export_database_to_csv()