"""Read Markdown documents and retain a citation for every heading-based chunk."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    'policies/ai-acceptable-use.md': ('Northwoods AI Acceptable-Use Policy', 'Fictional sample document'),
    'policies/employee-handbook-ai.md': ('Northwoods Employee Handbook: AI', 'Fictional sample document'),
    'nist/ai-rmf-excerpts.md': ('NIST AI RMF 1.0', 'https://doi.org/10.6028/NIST.AI.100-1'),
}

def load_chunks():
    chunks = []
    for filename, (title, source) in SOURCES.items():
        content = (ROOT / 'data' / filename).read_text(encoding='utf-8')
        parts = re.split(r'^##\s+(.+)$', content, flags=re.MULTILINE)
        for heading, body in zip(parts[1::2], parts[2::2]):
            text = body.strip()
            if text:
                chunks.append({'id': f'{filename}::{heading}', 'title': title,
                               'section': heading.strip(), 'source': source, 'text': text})
    return chunks
