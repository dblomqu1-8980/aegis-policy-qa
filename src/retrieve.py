"""Retrieve nearest passages and retain source metadata and cosine distance."""
import os
from dotenv import load_dotenv
from openai import OpenAI
import chromadb
from corpus import ROOT
from ingest import COLLECTION

def retrieve(question, limit=5):
    load_dotenv(ROOT / '.env')
    if not os.getenv('OPENAI_API_KEY'):
        raise RuntimeError('Set OPENAI_API_KEY in .env before asking a question.')
    col = chromadb.PersistentClient(path=str(ROOT / '.chroma')).get_collection(COLLECTION)
    model = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
    if col.metadata.get('embedding_model') != model:
        raise RuntimeError('Embedding model changed. Rebuild the index with python src/ingest.py.')
    vector = OpenAI().embeddings.create(model=model, input=[question]).data[0].embedding
    result = col.query(query_embeddings=[vector], n_results=min(limit, col.count()),
                       include=['documents', 'metadatas', 'distances'])
    threshold = float(os.getenv('MAX_DISTANCE', '0.65'))
    return [dict(meta, text=doc, distance=distance) for doc, meta, distance in
            zip(result['documents'][0], result['metadatas'][0], result['distances'][0])
            if distance <= threshold]
