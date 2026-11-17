"""Rebuild the local vector index from the checked-in sample corpus."""
import os
import hashlib
import json
import threading
from dotenv import load_dotenv
from openai import OpenAI
import chromadb
from corpus import ROOT, load_chunks

COLLECTION = 'policy_qa'
INDEX_LOCK = threading.Lock()

def fingerprint(chunks, model):
    return hashlib.sha256(json.dumps([model, chunks], sort_keys=True).encode()).hexdigest()

def ensure_index():
    load_dotenv(ROOT / '.env')
    with INDEX_LOCK:
        chunks = load_chunks()
        model = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
        db = chromadb.PersistentClient(path=str(ROOT / '.chroma'))
        try:
            col = db.get_collection(COLLECTION)
            if col.count() == len(chunks) and col.metadata.get('corpus_hash') == fingerprint(chunks, model):
                return
        except (ValueError, chromadb.errors.NotFoundError):
            pass
        ingest()

def ingest():
    load_dotenv(ROOT / '.env')
    if not os.getenv('OPENAI_API_KEY'):
        raise RuntimeError('Set OPENAI_API_KEY in .env before indexing.')
    chunks = load_chunks()
    model = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
    client = OpenAI(timeout=30, max_retries=0)
    embeddings = client.embeddings.create(model=model, input=[x['text'] for x in chunks]).data
    db = chromadb.PersistentClient(path=str(ROOT / '.chroma'))
    # Recreate to avoid retaining deleted or outdated document chunks.
    try:
        db.delete_collection(COLLECTION)
    except (ValueError, chromadb.errors.NotFoundError):
        pass
    col = db.create_collection(COLLECTION, metadata={'hnsw:space': 'cosine', 'embedding_model': model, 'corpus_hash': fingerprint(chunks, model)})
    col.add(ids=[x['id'] for x in chunks], documents=[x['text'] for x in chunks],
            metadatas=[{k:x[k] for k in ('title','section','source')} for x in chunks],
            embeddings=[x.embedding for x in embeddings])
    print(f'Indexed {len(chunks)} sections from {len(set(x["title"] for x in chunks))} documents.')
    for x in chunks:
        print(f'  {x["title"]} — {x["section"]}')

if __name__ == '__main__':
    ingest()
