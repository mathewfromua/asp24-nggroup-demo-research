"""Build structured PDF/HTML reports with the accepted vector/text covers.
Pinned WeasyPrint export plus ReportLab vector-figure assets. No network.
"""
from pathlib import Path
import csv,json,shutil,os
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
ROOT=Path(__file__).resolve().parent.parent
HERE=ROOT/'reports'; OUT=ROOT/'output';OUT.mkdir(exist_ok=True)
W,H=595.2756,841.8898;M=51;CW=W-2*M
THEMES={'ASP24':('#be4b00','#2c211c','#fbefe3','#f07a12'),'NGGroup':('#753697','#251a31','#f1eaf6','#a676c5')}
FONT_DIR=Path(os.environ.get('REPORT_FONT_DIR',os.environ.get('PERSPEKTYVA_FONT_DIR',str(HERE/'fonts'))))
for n,f in [('Body','NotoSans-Regular.ttf'),('Bold','NotoSans-Bold.ttf')]:pdfmetrics.registerFont(TTFont(n,str(FONT_DIR/f)))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold',italic='Body',boldItalic='Bold')
pdfmetrics.registerFont(TTFont('Symbols',str(FONT_DIR/'DejaVuSans.ttf')))
def draw_figure(c,kind,x,y,w,h,colors):
 c.saveState();c.translate(x,y);c.setFillColor(HexColor(colors[1]));c.setFont('Body',10.5)
 if kind=='filter':
  rows=list(csv.DictReader((ROOT/'evidence/figure_data/filter_paths.csv').open()))
  vals=[int(r['product_count']) for r in rows if r['brand']=='NG Group' and int(r['step'])<4];assert vals==[10,4,2,1];labels=['Категорія','+ Мідь Cu','+ Зовнішнє застосування','+ Чотири пари']
  for j,(v,l) in enumerate(zip(vals,labels)):
   yy=h-24-j*27;c.setFillColor(HexColor(colors[1]));c.drawString(0,yy,l);c.setFillColor(HexColor(colors[2]));c.rect(200,yy-3,w-235,16,fill=1,stroke=0);c.setFillColor(HexColor(colors[0]));c.rect(200,yy-3,(w-235)*v/10,16,fill=1,stroke=0);c.setFillColor(HexColor(colors[1]));c.setFont('Bold',11);c.drawRightString(w,yy,str(v));c.setFont('Body',10.5)
  c.drawString(0,4,'Повернення через «Вита пара»: знову 10 карток, умови скинуто.')
 elif kind=='history':
  # Paired values, not a shared timeline: every selected SKU has its own dates.
  rows=list(csv.DictReader((ROOT/'evidence/figure_data/technical_rows.csv').open()))
  labels={'MED001988':'RG-EW1200G Pro','MED005534':'XPON Stick','MED000715':'Cu-кабель'}
  def date(value):
   yyyy,mm,dd=value[:10].split('-');return f'{dd}.{mm}.{yyyy}'
  for j,sku in enumerate(labels):
   pair=[v for v in rows if v['sku']==sku];assert len(pair)==2
   before=next(v for v in pair if v['side']=='before');after=next(v for v in pair if v['side']=='after')
   top=h-15-j*47
   c.setFillColor(HexColor(colors[1]));c.setFont('Bold',10);c.drawString(0,top,labels[sku])
   c.setFont('Body',9);c.drawString(0,top-14,sku)
   for row,yy,filled in [(before,top,False),(after,top-17,True)]:
    n=int(row['technical_rows']);xx=267;bw=(w-xx-25)*n/30
    c.setFont('Body',10.5);c.setFillColor(HexColor(colors[1]));c.drawString(151,yy,date(row['capture_utc']))
    c.setStrokeColor(HexColor(colors[0]));c.setFillColor(HexColor(colors[0]));c.setLineWidth(1)
    if n:c.rect(xx,yy-2,bw,10,fill=int(filled),stroke=1)
    else:c.line(xx,yy-2,xx,yy+8)
    c.setFillColor(HexColor(colors[1]));c.setFont('Bold',10);c.drawString(xx+bw+6,yy,str(n))
 elif kind=='autonomy':
  left,bot,pw,ph=40,32,w-57,h-48
  def pt(p,t):return left+(p-5)/15*pw,bot+t/12*ph
  c.setStrokeColor(HexColor('#ded6e3'));c.setLineWidth(.6)
  for t in [0,4,8,12]:
   yy=pt(5,t)[1];c.line(left,yy,left+pw,yy);c.setFillColor(HexColor(colors[1]));c.drawRightString(left-8,yy-3,str(t))
  for p in [5,10,15,20]:xx=pt(p,0)[0];c.drawCentredString(xx,15,str(p))
  c.drawString(0,h-8,'год');c.drawRightString(w,0,'Стале навантаження, Вт')
  path=c.beginPath()
  for i in range(151):
   p=5+i*.1;xx,yy=pt(p,57.72/p)
   if i==0:path.moveTo(xx,yy)
   else:path.lineTo(xx,yy)
  c.setStrokeColor(HexColor(colors[0]));c.setLineWidth(1.8);c.drawPath(path)
  for p,label,dy,dx in [(13,'13 Вт: 4,44 год',18,-83),(15,'15 Вт: 3,85 год',-18,10)]:
   xx,yy=pt(p,57.72/p);c.setFillColor(HexColor(colors[0]));c.circle(xx,yy,3,fill=1,stroke=0);c.setFillColor(HexColor(colors[1]));c.drawString(xx+dx,yy+dy,label)
 c.restoreState()
def build():
 import subprocess,sys
 from build_tagged import build as structured_build
 # Always derive the PDF input from the current single manuscript. Existing
 # workflows may still call build_html.py afterwards; that is deterministic.
 subprocess.run([sys.executable,str(HERE/'build_html.py')],check=True)
 generated=structured_build(OUT/'structured',FONT_DIR)
 manifest=[]
 for record in generated:
  brand=record['brand'];dest=OUT/f'{brand}_Огляд.pdf'
  shutil.copy2(OUT/'structured'/record['file'],dest)
  shutil.copy2(dest,ROOT/'public/reports'/f'{brand}_Review.pdf')
  manifest.append({**record,'file':dest.name,'retained_vector_cover_pages':[1],
                   'regenerated_structure_pages':list(range(1,record['pages']+1))})
 (HERE/'pdf-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 layout=[{'brand':record['brand'],'section':section,'page':page,'renderer':'WeasyPrint 70.0'}
         for record in generated for section,page in record['section_pages'].items()]
 (HERE/'layout-check.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2)+'\n')
 fd=HERE/'figures';fd.mkdir(exist_ok=True)
 for k in ['filter','autonomy','history']:
  c=canvas.Canvas(str(fd/f'{k}.pdf'),pagesize=(CW,150 if k in ['autonomy','history'] else 140),invariant=1);draw_figure(c,k,0,0,CW,150 if k in ['autonomy','history'] else 140,THEMES['ASP24' if k=='history' else 'NGGroup']);c.save()
 print(json.dumps(manifest,ensure_ascii=False,indent=2))
if __name__=='__main__':build()
