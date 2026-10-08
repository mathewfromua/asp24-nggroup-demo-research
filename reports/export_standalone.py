"""Package the generated semantic HTML for offline reading, without duplicating text."""
from pathlib import Path
import base64, hashlib, json, re
from content import BASE_PATH, PUBLIC_BASE_URL
ROOT=Path(__file__).resolve().parent.parent
out=ROOT/'output/standalone';out.mkdir(exist_ok=True)
manifest=[]
for brand in ['ASP24','NGGroup']:
 src=ROOT/f'public/reports/{brand}_Review.html';text=src.read_text()
 def embed(match):
  file=src.parent/match[1]
  return 'src="data:image/png;base64,'+base64.b64encode(file.read_bytes()).decode()+'"'
 text=re.sub(r'src="(assets/[^"/]+\.png)"',embed,text)
 text=text.replace('href="../"',f'href="{PUBLIC_BASE_URL}"')
 dest=out/src.name;dest.write_text(text)
 (out/f'{brand}_Review.pdf').write_bytes((ROOT/f'public/reports/{brand}_Review.pdf').read_bytes())
 manifest.append({'html':str(dest.relative_to(ROOT)),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'public_html_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'content_sha256':hashlib.sha256((ROOT/'reports/content.json').read_bytes()).hexdigest(),'deployment_config_sha256':hashlib.sha256((ROOT/'deployment.config.json').read_bytes()).hexdigest(),'public_base_url':PUBLIC_BASE_URL,'derivation':'Identical generated text; local PNG images embedded for offline reading; home link points to the project origin.'})
(ROOT/'reports/standalone-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
