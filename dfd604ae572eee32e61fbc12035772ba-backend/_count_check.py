import sqlite3
db = r'./vector_data/chroma.sqlite3'
con = sqlite3.connect(db)
cur = con.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print('TABLES:', [r[0] for r in cur.fetchall()])
cur.execute("SELECT id, name FROM collections")
print('COLLECTIONS:', cur.fetchall())
try:
    cur.execute("SELECT COUNT(*) FROM embeddings")
    print('embeddings count (vector rows):', cur.fetchone()[0])
except Exception as e:
    print('embeddings err:', e)
try:
    cur.execute("SELECT COUNT(DISTINCT id) FROM embedding_metadata")
    print('embedding_metadata distinct ids:', cur.fetchone()[0])
except Exception as e:
    print('embedding_metadata err:', e)
con.close()
