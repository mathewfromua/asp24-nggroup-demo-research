#!/usr/bin/env python3
"""Bounded R42 pilot: semantic HTML section to tagged PDF, never replaces reports."""
from pathlib import Path
import hashlib,json,re
from weasyprint import HTML,CSS,__version__
from pypdf import PdfReader
root=Path(__file__).resolve().parents[1]
source=root/'public/reports/NGGroup_Review.html'
text=source.read_text()
section=re.search(r'<section\b[^>]*id="nggroup-06".*?</section>',text,re.S).group()
style=re.search(r'<style>(.*?)</style>',text,re.S).group(1)
html=f'<!doctype html><html lang="uk-UA"><head><meta charset="utf-8"><title>R42 контроль: NG Group — умови застосування</title><style>{style}</style></head><body><main>{section}</main></body></html>'
out=root/'output/tagged-pilot';out.mkdir(parents=True,exist_ok=True)
(out/'pilot.html').write_text(html)
HTML(string=html,base_url=source.parent.as_uri()+'/').write_pdf(out/'pilot.pdf',pdf_tags=True,stylesheets=[CSS(string='@page {size:A4; margin:18mm} body{font-family:DejaVu Sans,sans-serif} .page{box-shadow:none;margin:0;padding:0;border:0} nav{display:none}')])
reader=PdfReader(out/'pilot.pdf');tree=reader.trailer['/Root'].get('/StructTreeRoot');tags={}
seen=set()
def walk(obj):
 obj=obj.get_object() if hasattr(obj,'get_object') else obj
 if isinstance(obj,dict):
  if id(obj) in seen:return
  seen.add(id(obj))
  if '/S' in obj:tags[str(obj['/S'])]=tags.get(str(obj['/S']),0)+1
  if '/K' in obj:walk(obj['/K'])
 elif isinstance(obj,list):
  for child in obj:walk(child)
if tree:walk(tree)
result={'status':'EXPERIMENTAL_NOT_ACCEPTED','renderer':'WeasyPrint '+__version__,'input':str(source.relative_to(root)),'section':'nggroup-06','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'pdf_sha256':hashlib.sha256((out/'pilot.pdf').read_bytes()).hexdigest(),'pages':len(reader.pages),'structure_tags':tags,'lang':str(reader.trailer['/Root'].get('/Lang')),'pdf_ua_validator':'NOT_RUN','assistive_reading':'NOT_RUN','cover_merge':'NOT_TESTED','limit':'One semantic section only; final ReportLab reports remain untagged. Tag presence is not logical reading order, figure alternatives or PDF/UA acceptance.'}
(out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False))
