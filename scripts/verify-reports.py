from pathlib import Path
import json,hashlib,re,urllib.request,sys
from pypdf import PdfReader
from html.parser import HTMLParser
from html import escape
from argparse import ArgumentParser
R=Path(__file__).resolve().parent.parent
parser=ArgumentParser(description='Verify same-source reports and actual preview HTTP bytes.')
parser.add_argument('--evidence-dir',default='output/verification/reports')
parser.add_argument('--base-url',help='Actual HTTP(S) root of this build, including its deployment subpath.')
args=parser.parse_args()
E=R/args.evidence_dir;E.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(R/'reports'))
from content import REPORTS, PUBLIC_BASE_URL, BASE_PATH
d=REPORTS
class Text(HTMLParser):
 def __init__(self):super().__init__();self.parts=[]
 def handle_data(self,s):self.parts.append(s)
 def handle_starttag(self,tag,attrs):
  if tag in {'p','div','section','header','footer','nav','main','h1','h2','h3','li','tr','th','td','caption','figcaption','br'}:self.parts.append(' ')
 def handle_endtag(self,tag):
  if tag in {'p','div','section','header','footer','nav','main','h1','h2','h3','li','tr','th','td','caption','figcaption'}:self.parts.append(' ')
def plain(s):
 t=Text();t.feed(s);return re.sub(r'\s+',' ',''.join(t.parts)).strip()
class Semantics(HTMLParser):
 def __init__(self):
  super().__init__();self.ids=[];self.citations=[];self.regions=[];self.headings=[];self.in_heading=False
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if a.get('id'):self.ids.append(a['id'])
  if tag=='h1':self.in_heading=True;self.headings.append('')
  if tag=='a' and 'citation' in a.get('class','').split():self.citations.append(a)
  if any(c in a.get('class','').split() for c in ['table-scroll','chart-scroll']):self.regions.append(a)
 def handle_data(self,s):
  if self.in_heading:self.headings[-1]+=s
 def handle_endtag(self,tag):
  if tag=='h1':self.in_heading=False
def texts(block):
 k,*a=block
 if k in ['p','h','note','source','link']:return [a[0]]
 if k=='box':return a[:2]
 if k=='table':return a[0]+[v for row in a[1] for v in row]
 if k=='image':return [a[2]]
 return []
records=[]
for brand,pages in d.items():
 f=R/f'public/reports/{brand}_Review.pdf';pdf=PdfReader(f);ht=(R/f'public/reports/{brand}_Review.html').read_text();ph=plain(ht);assert len(pdf.pages)==len(pages)+1
 assert pdf.trailer['/Root']['/Lang']=='uk-UA';assert not pdf.trailer['/Root'].get('/StructTreeRoot')
 assert '{{PUBLIC_BASE_URL}}' not in ht and 'perspektyva.mathew-from-ua.chatgpt.site' not in ht
 assert 'href="../">До оглядів і прикладів' in ht
 semantics=Semantics();semantics.feed(ht)
 brandlabel='NG Group' if brand=='NGGroup' else brand
 subject='Від пошуку до підготовки закупівлі' if brand=='ASP24' else 'Від технічної інформації до вибору рішення'
 assert semantics.headings==[f'{brandlabel} — {subject}'],(brand,'Report heading must name its subject')
 assert len(semantics.ids)==len(set(semantics.ids)),(brand,'Duplicate document anchors')
 expected_sources={f'source-{re.search(r"\[(\d+)\]",block[1])[1]}' for page in pages for block in page['blocks'] if block[0]=='source'}
 assert expected_sources.issubset(semantics.ids),(brand,'Source record anchors missing')
 assert semantics.citations,(brand,'Citation navigation missing')
 for citation in semantics.citations:
  target=citation.get('href','').removeprefix('#')
  assert target in expected_sources,(brand,'Unresolved citation',citation)
  assert citation.get('aria-label')=='Джерело '+target.removeprefix('source-'),(brand,'Citation lacks a source name')
 for region in semantics.regions:
  assert region.get('role')=='region' and region.get('tabindex')=='0',(brand,'Scroll region is not keyboard accessible')
  assert region.get('aria-label') and region['aria-label']!='Таблиця, доступна для горизонтального прокручування',(brand,'Scroll region lacks a subject')
 htext=[]
 for i,page in enumerate(pages,2):
  assert plain(page['title']) in ph,(brand,i,'title');pt=plain(pdf.pages[i-1].extract_text());assert '\ufffd' not in pt
  for block in page['blocks']:
   if block[0]=='image' and len(block)>5:
    assert f'alt="{escape(block[5],quote=True)}"' in ht,(brand,i,'Explicit image alternative missing')
    assert plain(block[5])!=plain(block[3]),(brand,i,'Image alternative duplicates caption')
   for t in texts(block):
    assert plain(t) in ph,(brand,i,t[:60])
    compact=lambda v:re.sub(r'\s+','',plain(v))
    assert compact(t) in compact(pt),(brand,i,'PDF text missing',t[:80])
  htext.append({'page':i,'characters':len(pt),'annotations':len(pdf.pages[i-1].get('/Annots',[]))})
 records.append({'brand':brand,'pages':len(pdf.pages),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'lang':'uk-UA','struct_tree':False,'html_source_text_all_blocks':'PASS','html_semantics':{'status':'PASS','citation_links':len(semantics.citations),'source_anchors':len(expected_sources),'named_scroll_regions':len(semantics.regions)},'body_pages':htext,'pdf_ua':'NOT_CLAIMED','reading_order':'Untagged PDF; visual review recorded separately in reports/migration-review.json'})
(E/'pdf-html-structure.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
if not args.base_url:
 print('PASS same-source HTML blocks and PDF structural checks; HTTP NOT_RUN (no --base-url).')
 raise SystemExit(0)
base=args.base_url.rstrip('/')+'/';files=[]
for f in sorted((R/'dist').rglob('*')):
 if not f.is_file():continue
 name=f.relative_to(R/'dist').as_posix()
 with urllib.request.urlopen(base+name,timeout=15) as r:raw=r.read();ct=r.headers.get('Content-Type')
 assert raw==f.read_bytes(),name
 if name.endswith('.pdf'):assert raw.startswith(b'%PDF-')
 files.append({'path':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'content_type':ct})
scope='PUBLIC_HTTPS_BYTES' if base==PUBLIC_BASE_URL else 'SUPPLIED_HTTP_BASE_BYTES'
(E/'http-assets.json').write_text(json.dumps({'status':'PASS','scope':scope,'base_url':base,'browser_interactions':'NOT_TESTED_BY_THIS_SCRIPT','files':files},ensure_ascii=False,indent=2)+'\n')
print('PASS same-source HTML blocks, PDF structural checks, exact HTTP assets:',len(files),scope)
