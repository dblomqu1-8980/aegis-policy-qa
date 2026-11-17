"""End-to-end evaluation against the checked-in 12-question dataset.

Run: RUN_LIVE_EVALS=1 python -m pytest evals/test_eval.py -v
Requires an API key, installed dependencies, and a populated local Chroma index.
These are deliberately skipped in ordinary offline test runs.
"""
import os
from pathlib import Path
import sys

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
CASES = yaml.safe_load((ROOT / "evals/questions.yaml").read_text(encoding="utf-8"))

@pytest.mark.skipif(os.getenv("RUN_LIVE_EVALS") != "1", reason="Live API evaluations are opt-in")
@pytest.mark.parametrize("case", CASES, ids=[str(i+1) for i in range(len(CASES))])
def test_policy_question(case):
    from answer import ask, REFUSAL
    result = ask(case["question"])
    answer = result["answer"]
    citations = result["citations"]
    if case.get("refuse"):
        assert answer == REFUSAL, f"Expected refusal; got: {answer}"
        assert not citations
        return
    assert answer != REFUSAL, f"Unexpected refusal: {case['question']}"
    assert citations, "No citations returned"
    assert any(c["title"] == case["source"] for c in citations), (
        f"Required source {case['source']!r} not found in citations"
    )
    assert all(c.get("quote") and c["quote"] in c["text"] for c in citations)
    # Human review remains necessary for the substantive 'check' field.
