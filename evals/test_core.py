import sys
from pathlib import Path
from unittest.mock import MagicMock
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from corpus import load_chunks
from answer import ask, validate_response, REFUSAL

def test_chunks_have_sources_and_sections():
    chunks = load_chunks()
    assert len(chunks) == 10
    assert all(c['title'] and c['section'] and c['source'] and c['text'] for c in chunks)
    assert len({c['id'] for c in chunks}) == len(chunks)

def test_valid_quote_is_attached_to_real_source():
    passage = {'text':'A qualified employee must review the draft.', 'title':'Policy', 'section':'Review', 'source':'sample'}
    result = validate_response('{"answer":"Review is required.","citations":[{"passage":1,"quote":"A qualified employee must review"}]}', [passage])
    assert result['citations'][0]['title'] == 'Policy'

def test_invalid_or_missing_citations_refuse():
    p = [{'text':'A qualified employee must review the draft.'}]
    for raw in ['{}', 'not json', '{"answer":"Yes","citations":[]}', '{"answer":"Yes","citations":[{"passage":1,"quote":"made up quotation"}]}']:
        assert validate_response(raw, p)['answer'] == REFUSAL

def test_no_retrieval_does_not_call_model():
    client = MagicMock()
    assert ask('What are the holidays?', search=lambda _: [], client=client)['answer'] == REFUSAL
    client.chat.completions.create.assert_not_called()
