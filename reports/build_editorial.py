from build_inputs import inventory
"""Rebuild every body page; retain only the unchanged original covers.
Requires Python 3.12+, reportlab, pypdf, Pillow. No network or PyMuPDF.
"""
from pathlib import Path
import csv,io,json,hashlib,html,math,shutil,os
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader,PdfWriter
from pypdf.generic import NameObject,TextStringObject
from PIL import Image
from content import REPORTS, PUBLIC_BASE_URL
ROOT=Path(__file__).resolve().parent.parent
HERE=ROOT/'reports'; OUT=ROOT/'output';OUT.mkdir(exist_ok=True)
W,H=595.2756,841.8898;M=51;CW=W-2*M
THEMES={'ASP24':('#be4b00','#2c211c','#fbefe3','#f07a12'),'NGGroup':('#753697','#251a31','#f1eaf6','#a676c5')}
# Keep the accepted orange graphics; small text needs more contrast on the tint.
TEXT_ACCENTS={'ASP24':'#a84000','NGGroup':'#753697'}
FONT_DIR=Path(os.environ.get('REPORT_FONT_DIR',os.environ.get('PERSPEKTYVA_FONT_DIR',str(HERE/'fonts'))))
for n,f in [('Body','NotoSans-Regular.ttf'),('Bold','NotoSans-Bold.ttf')]:pdfmetrics.registerFont(TTFont(n,str(FONT_DIR/f)))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold',italic='Body',boldItalic='Bold')
pdfmetrics.registerFont(TTFont('Symbols',str(FONT_DIR/'DejaVuSans.ttf')))
def glyphs(text):return str(text).replace('→','<font name="Symbols">→</font>')
LAYOUT=[]
class Page:
 def __init__(self,brand,num,section,title,section_id):
  self.brand,self.num,self.colors=brand,num,THEMES[brand];self.section_id=section_id;self.text_accent=TEXT_ACCENTS[brand];self.buf=io.BytesIO();self.c=canvas.Canvas(self.buf,pagesize=(W,H),invariant=1);self.y=H-88
  self.c.setFillColor(HexColor(self.text_accent));self.c.setFont('Bold',10.5);self.c.drawString(M,H-54,'NG Group' if brand=='NGGroup' else brand)
  self.c.setFillColor(HexColor('#60575c'));self.c.setFont('Body',10);self.c.drawRightString(W-M,H-54,section)
  self.c.setStrokeColor(HexColor(self.colors[2]));self.c.line(M,H-66,W-M,H-66)
  self.p(title,22.2,28,'Bold',13)
 def style(self,size=12,lead=17,font='Body',color=None):return ParagraphStyle('p',fontName=font,fontSize=size,leading=lead,textColor=HexColor(color or self.colors[1]),allowWidows=0,allowOrphans=0)
 def check(self,h,what):
  if self.y-h<57:raise ValueError(f'Overflow {self.brand} p{self.num}: y={self.y-h:.1f}: {what[:75]}')
 def p(self,text,size=12,lead=17,font='Body',space=10,color=None):
  p=Paragraph(glyphs(text),self.style(size,lead,font,color));_,h=p.wrap(CW,1000);self.check(h,text);p.drawOn(self.c,M,self.y-h);self.y-=h+space
 def h(self,text):self.p(text,12.2,17.3,'Bold',6,self.text_accent)
 def note(self,text):self.p(text,10,14.1,space=9,color='#61565c')
 def box(self,title,text):
  ps=[Paragraph(glyphs(title),self.style(12,17,'Bold',self.text_accent)),Paragraph(glyphs(text),self.style(11.6,16.6))];hs=[p.wrap(CW-28,900)[1] for p in ps];h=sum(hs)+30;self.check(h,title)
  self.c.setFillColor(HexColor(self.colors[2]));self.c.rect(M,self.y-h,CW,h,fill=1,stroke=0);self.c.setStrokeColor(HexColor(self.colors[3]));self.c.setLineWidth(1.4);self.c.line(M,self.y,M,self.y-h)
  y=self.y-12
  for p,ph in zip(ps,hs):p.drawOn(self.c,M+14,y-ph);y-=ph+6
  self.y-=h+11
 def table(self,headers,rows,widths=None,size=11.1):
  # More breathing room only in the dense tables with room to spare.
  spacious=self.section_id in ['asp24-10','nggroup-11'] and len(headers)==3
  widths=[CW*x for x in (widths or [1/len(headers)]*len(headers))];ss=self.style(size,size*(1.5 if spacious else 1.42));sh=self.style(size,size*1.42,'Bold','#ffffff')
  data=[[Paragraph(glyphs(v),sh) for v in headers]]+[[Paragraph(glyphs(v),ss) for v in row] for row in rows]
  t=Table(data,colWidths=widths,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor(self.colors[1])),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('ROWBACKGROUNDS',(0,1),(-1,-1),[HexColor('#ffffff'),HexColor(self.colors[2])]),('LINEBELOW',(0,1),(-1,-1),.5,HexColor(self.colors[2]))]))
  if spacious:t.setStyle(TableStyle([('TOPPADDING',(0,1),(-1,-1),9),('BOTTOMPADDING',(0,1),(-1,-1),9)]))
  _,h=t.wrap(CW,1100);self.check(h,'table');t.drawOn(self.c,M,self.y-h);self.y-=h+9
 def image(self,name,height,caption,crop=None,alt=None):
  path=HERE/name;im=Image.open(path);im.load()
  if crop:im=im.crop(tuple(crop))
  w,h=im.size;hh=min(height,CW*h/w);ww=hh*w/h;self.check(hh,'image');self.c.drawImage(ImageReader(im),M+(CW-ww)/2,self.y-hh,ww,hh,mask='auto');self.y-=hh+6
  self.note(caption)
 def figure(self,kind):
  h=124 if kind=='autonomy' else 150 if kind=='history' else 140
  self.check(h,'figure');draw_figure(self.c,kind,M,self.y-h,CW,h,self.colors);self.y-=h+9
 def finish(self):
  LAYOUT.append({'brand':self.brand,'page':self.num,'content_bottom':round(self.y,2)})
  self.c.setFont('Body',10);self.c.setFillColor(HexColor('#60575c'));self.c.drawRightString(W-M,33,str(self.num));self.c.showPage();self.c.save();return self.buf.getvalue()
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
 manifest=[]
 for brand,pages in REPORTS.items():
  writer=PdfWriter();reader=PdfReader(HERE/'covers'/f'{brand}.pdf');writer.add_page(reader.pages[0])
  for num,spec in enumerate(pages,2):
   p=Page(brand,num,spec['section'],spec['title'],spec['id'])
   for index,block in enumerate(spec['blocks']):
    kind,*args=block
    if (spec['id']=='asp24-07' and kind=='h') or (spec['id']=='nggroup-13' and index==len(spec['blocks'])-1):p.y-=6
    if kind=='p':p.p(*args)
    elif kind=='h':p.h(*args)
    elif kind=='note':
     if any(b[0]=='source' for b in spec['blocks']):p.p(args[0],11,15.8,space=11,color='#61565c')
     else:p.note(*args)
    elif kind=='box':p.box(*args)
    elif kind=='table':p.table(*args)
    elif kind=='image':p.image(*args)
    elif kind=='figure':p.figure(*args)
    elif kind=='link':p.p(f'<link href="{html.escape(args[1],quote=True)}" color="{p.text_accent}"><u>{args[0]}</u></link>',11.4,16.5,'Bold')
    elif kind=='source':p.p(*args,11.2,16,space=9)
   writer.add_page(PdfReader(io.BytesIO(p.finish())).pages[0])
  writer.add_metadata({'/Title':f'{"NG Group" if brand == "NGGroup" else brand} — огляд сайту','/Subject':'Технічний каталог, документи й консультація' if brand == 'NGGroup' else 'Пошук, технічний вибір і підготовка закупівлі'})
  writer._root_object[NameObject('/Lang')]=TextStringObject('uk-UA')
  # This engine does not create a validated structure tree. Do not claim PDF/UA.
  dest=OUT/f'{brand}_Огляд.pdf'
  with dest.open('wb') as f:writer.write(f)
  manifest.append({'file':dest.name,'input_digest':inventory()['digest'],'content_sha256':hashlib.sha256((HERE/'content.json').read_bytes()).hexdigest(),'deployment_config_sha256':hashlib.sha256((ROOT/'deployment.config.json').read_bytes()).hexdigest(),'public_base_url':PUBLIC_BASE_URL,'pages':len(writer.pages),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'retained_pages':[1],'regenerated_pages':list(range(2,len(writer.pages)+1))})
  shutil.copy2(dest,ROOT/'public/reports'/('ASP24_Review.pdf' if brand=='ASP24' else 'NGGroup_Review.pdf'))
 (HERE/'pdf-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');(HERE/'layout-check.json').write_text(json.dumps(LAYOUT,ensure_ascii=False,indent=2)+'\n')
 fd=HERE/'figures';fd.mkdir(exist_ok=True)
 for k in ['filter','autonomy','history']:
  c=canvas.Canvas(str(fd/f'{k}.pdf'),pagesize=(CW,150 if k in ['autonomy','history'] else 140),invariant=1);draw_figure(c,k,0,0,CW,150 if k in ['autonomy','history'] else 140,THEMES['ASP24' if k=='history' else 'NGGroup']);c.save()
 print(json.dumps(manifest,ensure_ascii=False,indent=2))
if __name__=='__main__':build()
