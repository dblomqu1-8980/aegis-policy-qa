import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from hr_corpus import load_hr_chunks
from hr_engine import allowed_audiences, ask_hr, SENSITIVE

def test_ingest_real_docx_pdf_active_version_only():
    chunks=load_hr_chunks()
    assert any(c["file"].endswith(".pdf") for c in chunks)
    assert any(c["file"].endswith(".docx") for c in chunks)
    assert any("$600" in c["text"] for c in chunks)
    assert all("$300" not in c["text"] for c in chunks)
    assert all(c["version"]!="1.0" for c in chunks if c["title"]=="Northwoods Employee Handbook")

def test_roles_fail_closed_and_sensitive_route():
    assert allowed_audiences("employee")==["employee"]
    assert allowed_audiences("hr")==["employee","hr"]
    assert SENSITIVE.search("I need to report harassment")
    assert not SENSITIVE.search("How much sick time do I get?")
    assert ask_hr("I need to report harassment")["escalation"] is True
