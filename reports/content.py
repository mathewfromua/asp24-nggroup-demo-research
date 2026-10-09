"""One canonical manuscript and deployment URL for PDF and semantic HTML."""
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
DEPLOYMENT = json.loads((ROOT / "deployment.config.json").read_text(encoding="utf-8"))
PUBLIC_BASE_URL = DEPLOYMENT["PUBLIC_BASE_URL"]
BASE_PATH = DEPLOYMENT["BASE_PATH"]
url = urlsplit(PUBLIC_BASE_URL)
if url.scheme != "https" or not url.netloc or url.path != BASE_PATH or not BASE_PATH.endswith("/"):
    raise ValueError("PUBLIC_BASE_URL must be HTTPS and match the trailing-slash BASE_PATH")


PUBLICATION = json.loads((ROOT / "publication.json").read_text(encoding="utf-8"))
CASES = {c["caseId"]: c for c in PUBLICATION["cases"]}

def resolve(value):
    if isinstance(value, str):
        value = value.replace("{{PUBLIC_BASE_URL}}", PUBLIC_BASE_URL)
        for id,c in CASES.items():
            value=value.replace("{{CASE:"+id+"}}", PUBLIC_BASE_URL+f'cases/{id}/v{c["caseVersion"]}/')
        return value
    if isinstance(value, list):
        return [resolve(item) for item in value]
    if isinstance(value, dict):
        return {key: resolve(item) for key, item in value.items()}
    return value


REPORTS = resolve(json.loads((ROOT / "reports/content.json").read_text(encoding="utf-8")))
