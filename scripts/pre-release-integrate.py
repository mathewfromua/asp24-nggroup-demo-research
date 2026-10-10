"""One-time bounded historical DEPS citation correction; no external or Git changes."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
p=R/'reports/content.json'
data=json.loads(p.read_text())
def section(key):return next(s for s in data['NGGroup'] if s['id']==key)
# A PATCH-03: the old hyperlink behavior is secondarily attested, not reproduced here.
block=section('nggroup-12')['blocks'][2]
assert block[0]=='box'
old='У перевіреній картці DEPS підпис Quattro-II вів до PDF MultiPlus-II; сусіднє посилання відкривало правильний Quattro-II. Зручний перелік файлів сам по собі не гарантує відповідності.'
new='За попереднім оглядом DEPS підпис Quattro-II вів до PDF MultiPlus-II, а сусіднє посилання — до Quattro-II. Первинний click trace і обидва PDF тут не відновлено; це обмежене історичне спостереження.'
assert block[2].count(old)==1
block[2]=block[2].replace(old,new)
source=section('nggroup-16')['blocks'][3]
assert source[0]=='source' and source[1].startswith('<b>[11]</b>')
old='DEPS: сторінки й текст PDF 04.10.2026. Quattro-II та помилково підписаний MultiPlus-II — окремі файли у протоколі.'
new='DEPS: за попереднім протоколом від 04.10.2026, Quattro-II і MultiPlus-II — окремі PDF; поточного повторного click-test не проводили.'
assert source[1].count(old)==1
source[1]=source[1].replace(old,new)
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
claim=R/'reports/claim-map-editorial.json'
c=json.loads(claim.read_text())
assert c['manuscript_sha256']=='7a11a8b2bb3d24de104b0b40a5b577a76c08fbec3cab325d0e8ad2a10ce69813'
assert c['sources']['NGGroup:11']['printed_source_note']!=source[1]
c['sources']['NGGroup:11']['printed_source_note']=source[1]
c['manuscript_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
c['integration_evidence_limit']['quattro_link_experience']='HISTORICAL_REVIEW_ONLY_NO_RAW_CLICK_TRACE'
claim.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
ledger=R/'docs/INTEGRATION_LEDGER.md';s=ledger.read_text()
a='Retain existing historical wording; 97-ID A ledger explicitly distinguishes PRIMARY/SECONDARY/OPEN'
b='Quattro-II/MultiPlus-II now explicitly attributed to prior DEPS review; 97-ID A ledger distinguishes PRIMARY/SECONDARY/OPEN'
assert s.count(a)==1
ledger.write_text(s.replace(a,b))
print(json.dumps({'status':'PATCHED_BOUNDED_ONLY','current_manuscript_sha256':c['manuscript_sha256'],'claim':'NGGroup:11','no_primary_capture':True}))
