from build_inputs import inventory
"""Semantic adaptive reports from the same content.json used for PDF."""
from pathlib import Path
import csv, hashlib, html, json, re, shutil
from PIL import Image
from content import REPORTS, BASE_PATH, PUBLIC_BASE_URL

ROOT=Path(__file__).resolve().parent.parent
HERE=ROOT/'reports'; OUT=ROOT/'public/reports'; ASSETS=OUT/'assets'
ASSETS.mkdir(exist_ok=True)
def inline(s):
    # Source permits only controlled report-format inline tags and HTTPS links.
    s=re.sub(r'<link href="([^"]+)"(?: color="[^"]+")?>',r'<a href="\1">',str(s))
    return s.replace('</link>','</a>').replace('<br/>','<br>')
def table(headers,rows,caption=''):
    cap=f'<caption>{inline(caption)}</caption>' if caption else ''
    return '<div class="table-scroll" tabindex="0" role="region" aria-label="Таблиця, доступна для горизонтального прокручування"><table>'+cap+'<thead><tr>'+''.join('<th scope="col">'+inline(v)+'</th>' for v in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join(('<th scope="row">'+inline(v)+'</th>') if i==0 else '<td>'+inline(v)+'</td>' for i,v in enumerate(row))+'</tr>' for row in rows)+'</tbody></table></div>'
def records(name):return list(csv.DictReader((ROOT/'evidence/figure_data'/name).open()))
def figure(kind):
    if kind=='filter':
        rows=[r for r in records('filter_paths.csv') if r['brand']=='NG Group' and int(r['step'])<4]
        assert [int(r['product_count']) for r in rows]==[10,4,2,1]
        return table(['Умова','Товарних карток'],[[r['condition_or_action'],r['product_count']] for r in rows],'Добір NG Group: 10 → 4 → 2 → 1. Повернення через «Вита пара» відкрило 10 карток і скинуло умови.')
    if kind=='history':
        rows=records('technical_rows.csv');data=[]
        for sku in ['MED001988','MED005534','MED000715']:
            pair=[r for r in rows if r['sku']==sku];assert len(pair)==2
            for r in pair:
                date=r['capture_utc'][:10].split('-'); data.append([r['model']+' · '+sku,'.'.join(reversed(date)),r['technical_rows']])
        return table(['Модель / артикул','Дата знімка','Технічних рядків'],data,'Парні історичні вимірювання: 16 → 9, 14 → 0, 30 → 0. Нуль означає відсутність предметних рядків у вибраній таблиці, а не всієї інформації про товар.')
    rows=[r for r in records('nominal_autonomy.csv') if 5<=float(r['load_w'])<=20]
    assert all(abs(float(r['ideal_hours'])-57.72/float(r['load_w']))<1e-5 for r in rows)
    points=' '.join(f'{45+(float(r["load_w"])-5)/15*465:.2f},{215-float(r["ideal_hours"])/12*185:.2f}' for r in rows)
    svg=f'<svg viewBox="0 0 560 260" role="img" aria-label="Час роботи зменшується зі зростанням сталого навантаження. Точні значення наведено в таблиці."><path d="M45 25V215H520" fill="none" stroke="currentColor"/><polyline points="{points}" fill="none" stroke="var(--accent)" stroke-width="3"/><text x="12" y="18">год</text><text x="485" y="247">Вт</text>'
    for p in [5,10,15,20]:svg+=f'<text x="{45+(p-5)/15*465}" y="235" text-anchor="middle">{p}</text>'
    for t in [0,4,8,12]:svg+=f'<text x="35" y="{220-t/12*185}" text-anchor="end">{t}</text>'
    svg+='</svg>'
    return svg+table(['Стале навантаження, Вт','Умовний час, год'],[[r['load_w'].replace('.',','),f'{float(r["ideal_hours"]):.2f}'.replace('.',',')] for r in rows],'t = E/P; E = 57,72 Вт·год. Без втрат, старіння та зміни навантаження; це не результат випробування.')

CSS='''*{box-sizing:border-box}html{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:var(--ink);background:var(--paper);line-height:1.65}body{margin:0}a{color:var(--accent);text-underline-offset:.2em;overflow-wrap:anywhere}a:focus-visible,[tabindex]:focus-visible{outline:3px solid var(--accent);outline-offset:4px}.skip{position:absolute;left:1rem;top:-6rem;background:white;padding:1rem}.skip:focus{top:1rem}header,main,footer{max-width:60rem;margin:auto;padding:1.5rem clamp(1rem,4vw,3rem)}header{padding-top:3rem;border-bottom:3px solid var(--accent)}h1{font-size:clamp(2rem,5vw,3.5rem);line-height:1.14;margin:.5em 0}h2{font-size:clamp(1.65rem,3vw,2.1rem);line-height:1.25}h3{font-size:1.2rem}p,li{font-size:1.1rem}section{padding:2rem 0;border-bottom:1px solid var(--soft)}section>p{max-width:76ch}.section-label{color:var(--accent);font-weight:650}.note,figcaption{font-size:1rem}.callout{border-left:4px solid var(--accent);background:var(--soft);padding:1rem 1.25rem;margin:1.5rem 0}.callout h3{margin-top:0}figure{margin:1.5rem 0}img,svg{max-width:100%;height:auto;display:block;margin:auto}svg{width:100%;font-size:16px}.table-scroll{overflow-x:auto;margin:1.5rem 0}table{width:100%;border-collapse:collapse;font-size:1rem}th,td{text-align:left;vertical-align:top;padding:.75rem;border-bottom:1px solid var(--soft);min-width:6rem;overflow-wrap:anywhere}thead{background:var(--ink);color:white}tbody tr:nth-child(even){background:var(--soft)}caption{text-align:left;font-weight:600;margin-bottom:.75rem}nav a,.action{display:inline-flex;align-items:center;min-height:44px;padding:.3rem .7rem;margin:.2rem .2rem .2rem 0;border:1px solid var(--accent);border-radius:.4rem}nav[aria-label="Зміст"] a{display:block;border:0;padding:.3rem 0}.source{font-size:1rem;overflow-wrap:anywhere}footer{font-size:1rem}@media(max-width:430px){th,td{padding:.6rem;font-size:.95rem}h2{overflow-wrap:anywhere}section{padding:1.3rem 0}}@media print{nav,.skip,.action{display:none}.table-scroll{overflow:visible}section{break-inside:avoid}}'''

manifest=[]
assets=[]
for brand,pages in REPORTS.items():
    brandlabel='NG Group' if brand=='NGGroup' else brand
    palette=('#be4b00','#2c211c','#fbefe3') if brand=='ASP24' else ('#753697','#251a31','#f1eaf6')
    body=[];block_count=0
    for page in pages:
        parts=[f'<section id="{page["id"]}" aria-labelledby="h-{page["id"]}"><p class="section-label">{inline(page["section"])}</p><h2 id="h-{page["id"]}">{inline(page["title"])}</h2>']
        for bi,b in enumerate(page['blocks']):
            kind,*a=b;block_count+=1
            if kind in ['p','note','source']:parts.append(f'<p class="{kind}">{inline(a[0])}</p>')
            elif kind=='h':parts.append('<h3>'+inline(a[0])+'</h3>')
            elif kind=='box':parts.append('<aside class="callout"><h3>'+inline(a[0])+'</h3><p>'+inline(a[1])+'</p></aside>')
            elif kind=='table':parts.append(table(a[0],a[1]))
            elif kind=='link':parts.append(f'<p><a class="action" href="{html.escape(a[1],quote=True)}">{inline(a[0])}</a></p>')
            elif kind=='figure':parts.append('<figure>'+figure(a[0])+'</figure>')
            elif kind=='image':
                im=Image.open(HERE/a[0]);im.load()
                if len(a)>3 and a[3]:im=im.crop(tuple(a[3]))
                name=f'{brand}-{page["id"]}-{bi}.png';im.save(ASSETS/name)
                assets.append(f'reports/assets/{name}')
                cap=inline(a[2]);alt=html.escape(re.sub('<[^>]+>','',a[2]),quote=True)
                parts.append(f'<figure><img src="assets/{name}" width="{im.width}" height="{im.height}" alt="{alt}" loading="lazy"><figcaption>{cap}</figcaption></figure>')
            else:raise ValueError(kind)
        parts.append('</section>');body.append(''.join(parts))
    title=brandlabel+' · Огляд сайту'
    subtitles={'ASP24':'Від пошуку до підготовки закупівлі','NGGroup':'Від технічної інформації до вибору рішення'}
    document=f'''<!doctype html><html lang="uk"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="report-source-sha256" content="{hashlib.sha256((HERE/'content.json').read_bytes()).hexdigest()}"><title>{title}</title><style>:root{{--accent:{palette[0]};--ink:{palette[1]};--soft:{palette[2]};--paper:#fff}}{CSS}</style></head><body><a class="skip" href="#report">До тексту огляду</a><header><p class="section-label">{brandlabel}</p><h1>Огляд сайту</h1><p>{subtitles[brand]}</p><nav aria-label="Подання огляду"><a href="{brand}_Review.pdf">Завантажити PDF · {len(pages)+1} сторінок</a><a href="../">До демо</a></nav></header><main id="report"><nav aria-label="Зміст">{''.join(f'<a href="#{p["id"]}">{inline(p["title"])}</a>' for p in pages)}</nav>{''.join(body)}</main><footer>HTML і PDF сформовано з одного джерела тексту. ASP24 / NG Group — Demo &amp; Research — демонстрація на умовних даних; локальні дії не надсилаються компаніям.</footer></body></html>'''
    dest=OUT/f'{brand}_Review.html';dest.write_text(document)
    manifest.append({'brand':brand,'html':dest.relative_to(ROOT).as_posix(),'sections':len(pages),'blocks':block_count,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'input_digest':inventory()['digest'],'content_sha256':hashlib.sha256((HERE/'content.json').read_bytes()).hexdigest(),'deployment_config_sha256':hashlib.sha256((ROOT/'deployment.config.json').read_bytes()).hexdigest(),'public_base_url':PUBLIC_BASE_URL})
(HERE/'html-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(manifest,ensure_ascii=False,indent=2))

(HERE/'html-public-assets.json').write_text(json.dumps(sorted(assets+[f'reports/{brand}_Review.html' for brand in REPORTS]),indent=2)+'\n')
