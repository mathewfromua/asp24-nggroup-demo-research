"""Current report structure, unchanged covers and active deployment links.
This verifies files, not Safari, phone interactions or public deployment.
"""
from pathlib import Path
import hashlib,json,re,sys
from pypdf import PdfReader
root=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(root/'reports'))
from content import REPORTS,PUBLIC_BASE_URL
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
results=[]
for brand,expected_pages in [('ASP24',14),('NGGroup',16)]:
    file=root/'public/reports'/f'{brand}_Review.pdf'
    reader=PdfReader(file);cover=PdfReader(root/'reports/covers'/f'{brand}.pdf')
    assert len(reader.pages)==expected_pages==len(REPORTS[brand])+1
    assert reader.pages[0].get_contents().get_data()==cover.pages[0].get_contents().get_data()
    texts=[' '.join(p.extract_text().split()) for p in reader.pages]
    assert all('\x00' not in t and '\ufffd' not in t for t in texts)
    assert not any(re.search('Перспектив',t,re.I) for t in texts)
    assert reader.trailer['/Root']['/Lang']=='uk-UA'
    links=[]
    for n,page in enumerate(reader.pages,1):
        for obj in page.get('/Annots',[]):
            action=obj.get_object().get('/A',{})
            if '/URI' in action:
                url=str(action['/URI']);assert not re.search(r'\s',url)
                assert '{{' not in url and 'perspektyva.mathew-from-ua.chatgpt.site' not in url
                links.append({'page':n,'url':url})
    demo=[x for x in links if x['url'].startswith(PUBLIC_BASE_URL)]
    assert demo and all(x['url'].startswith(PUBLIC_BASE_URL+'#/') for x in demo)
    if brand=='ASP24':
        assert all(s in texts[10] for s in ['УТП002164','УТП002165'])
        assert 'https://asp24.ua/akumuliator-dlia-dbzh-mini-ups-ng-power-m1550-c-35w-15600-mah/' in [x['url'] for x in links]
    else:
        assert 'У редакційному дослідженні 08.10.2026 додатково' not in texts[6]
        assert '08.10.2026' in texts[14] and 'десяти' in texts[14]
    dist=root/'dist/reports'/file.name
    dist_match=sha(file)==sha(dist) if dist.exists() else None
    results.append({'file':file.relative_to(root).as_posix(),'sha256':sha(file),'pages':expected_pages,'cover_content_unchanged':True,'unicode_extraction':'PASS','active_demo_links':demo,'dist_bytes_match':dist_match,'pdf_ua':'NOT_CLAIMED','scope':'OFFLINE_FILE_VERIFICATION'})
print(json.dumps(results,ensure_ascii=False,indent=2))
