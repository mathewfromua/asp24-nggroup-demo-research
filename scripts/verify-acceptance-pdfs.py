"""Current report structure, unchanged cover artwork and active deployment links.
This verifies files, not Safari, phone interactions or public deployment.
"""
from pathlib import Path
import hashlib,io,json,re,sys
from pypdf import PdfReader
from pypdf.generic import ContentStream
root=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(root/'reports'))
from content import REPORTS,PUBLIC_BASE_URL
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def drawing_operations(page, reader):
    # Accessible covers add marked-content boundaries to the accepted vector/text
    # artwork. Those boundaries do not paint; every painting/text operation must
    # still match. Do not accept a raster replacement that merely looks similar.
    # Compare both using pypdf's numeric serialization: transplanting the stream
    # rewrites FloatObjects to that precision even when their value is unchanged.
    operations=[]
    for operands,operator in ContentStream(page.get_contents(),reader).operations:
        if operator in {b'BMC',b'BDC',b'EMC'}:
            continue
        serialized=io.BytesIO()
        for operand in operands:
            operand.write_to_stream(serialized)
            serialized.write(b' ')
        operations.append((serialized.getvalue(),operator))
    return operations

manifests=json.loads((root/'reports/pdf-manifest.json').read_text())
expected_counts={entry['file'].split('_')[0]:entry['pages'] for entry in manifests}
results=[]
for brand in ['ASP24','NGGroup']:
    file=root/'public/reports'/f'{brand}_Review.pdf'
    reader=PdfReader(file);cover=PdfReader(root/'reports/covers'/f'{brand}.pdf')
    expected_pages=expected_counts[brand]
    assert len(reader.pages)==expected_pages and expected_pages>1
    assert drawing_operations(reader.pages[0],reader)==drawing_operations(cover.pages[0],cover),(brand,'Accepted cover artwork changed')
    texts=[' '.join(p.extract_text().split()) for p in reader.pages]
    assert all('\x00' not in t and '\ufffd' not in t for t in texts)
    assert not any(re.search('Перспектив',t,re.I) for t in texts)
    assert reader.trailer['/Root']['/Lang']=='uk-UA'
    assert reader.trailer['/Root'].get('/StructTreeRoot')
    marked=reader.trailer['/Root'].get('/MarkInfo',{}).get('/Marked')
    assert getattr(marked,'value',marked) is True
    assert reader.outline,(brand,'Document bookmarks missing')
    links=[]
    for n,page in enumerate(reader.pages,1):
        for obj in page.get('/Annots',[]):
            action=obj.get_object().get('/A',{})
            if '/URI' in action:
                url=str(action['/URI']);assert not re.search(r'\s',url)
                assert '{{' not in url and 'perspektyva.mathew-from-ua.chatgpt.site' not in url
                links.append({'page':n,'url':url})
    demo=[x for x in links if x['url'].startswith(PUBLIC_BASE_URL)]
    assert demo and all(x['url'].startswith(PUBLIC_BASE_URL) for x in demo)
    assert any(x['url'].startswith(PUBLIC_BASE_URL+'reports/'+brand+'_Review.html') for x in demo)
    if brand=='ASP24':
        assert all(s in ' '.join(texts) for s in ['УТП002164','УТП002165'])
        assert 'https://asp24.ua/akumuliator-dlia-dbzh-mini-ups-ng-power-m1550-c-35w-15600-mah/' in [x['url'] for x in links]
    else:
        assert 'У редакційному дослідженні 08.10.2026 додатково' not in ' '.join(texts)
        assert '08.10.2026' in ' '.join(texts) and 'десяти' in ' '.join(texts)
    dist=root/'dist/reports'/file.name
    dist_match=sha(file)==sha(dist) if dist.exists() else None
    results.append({'file':file.relative_to(root).as_posix(),'sha256':sha(file),'pages':expected_pages,'cover_painting_operations_unchanged':True,'unicode_extraction':'PASS','active_demo_links':demo,'dist_bytes_match':dist_match,'pdf_ua':'NOT_CONFIRMED_BY_THIS_SCRIPT','scope':'OFFLINE_FILE_VERIFICATION; full tag validation is a separate required gate'})
print(json.dumps(results,ensure_ascii=False,indent=2))
