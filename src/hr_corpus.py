"""Active sample HR policies; PDF, Word and Markdown ingestion."""
import json
import hashlib
import re
from pathlib import Path
from pypdf import PdfReader
from docx import Document

ROOT = Path(__file__).resolve().parents[1]
HR_ROOT = (ROOT / "data" / "hr").resolve()
HEADING = re.compile(r"^\d+(?:\.\d+)*\.\s+\S")

def document_lines(path):
    if path.suffix == ".docx":
        return [p.text.strip() for p in Document(path).paragraphs if p.text.strip()]
    if path.suffix == ".pdf":
        return [line.strip() for p in PdfReader(str(path)).pages for line in (p.extract_text() or "").splitlines() if line.strip()]
    if path.suffix == ".md":
        return [line.strip().lstrip("# ").strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    raise ValueError("Unsupported HR file")

def load_hr_chunks():
    manifest = json.loads((HR_ROOT / "manifest.json").read_text(encoding="utf-8"))
    chunks, active_ids = [], set()
    for entry in manifest:
        if entry["status"] != "active":
            continue
        if entry["document_id"] in active_ids:
            raise ValueError("Duplicate active document")
        active_ids.add(entry["document_id"])
        if entry["audience"] not in ("employee", "hr"):
            raise ValueError("Unknown audience")
        path = (HR_ROOT / entry["file"]).resolve()
        if not path.is_relative_to(HR_ROOT) or not path.is_file():
            raise ValueError("Invalid path")
        section, body, count = None, [], 0
        for line in document_lines(path) + ["9999. End"]:
            if HEADING.match(line):
                if section and body:
                    text = " ".join(body)
                    digest = hashlib.sha256((entry["document_id"] + entry["version"] + section).encode()).hexdigest()[:16]
                    chunks.append(dict(
                        id=entry["document_id"] + "::" + digest, text=text,
                        title=entry["title"], section=section, version=entry["version"],
                        audience=entry["audience"], effective_date=entry["effective_date"],
                        source="https://github.com/dblomqu1-8980/aegis-policy-qa/blob/main/data/hr/" + entry["file"],
                        file=entry["file"],
                    ))
                    count += 1
                section, body = line, []
            elif section:
                body.append(line)
        if not count:
            raise ValueError("No HR policy sections: " + entry["file"])
    return chunks
