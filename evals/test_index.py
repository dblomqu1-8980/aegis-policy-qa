"""Exercise real local Chroma storage with a fake embedding provider."""
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import ingest

def test_index_reuses_unchanged_corpus_and_rebuilds_changed_corpus(tmp_path, monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY','test-placeholder')
    monkeypatch.setattr(ingest,'ROOT',tmp_path)
    chunks=[dict(id='policy::one',title='Policy',section='One',source='sample',text='Sample approved policy content.')]
    monkeypatch.setattr(ingest,'load_chunks',lambda:chunks)
    client=MagicMock()
    client.embeddings.create.return_value=SimpleNamespace(data=[SimpleNamespace(embedding=[1.,0.,0.])])
    monkeypatch.setattr(ingest,'OpenAI',lambda **kwargs:client)
    ingest.ensure_index()
    ingest.ensure_index()
    assert client.embeddings.create.call_count==1
    chunks[0]['text']='Updated policy content.'
    ingest.ensure_index()
    assert client.embeddings.create.call_count==2
