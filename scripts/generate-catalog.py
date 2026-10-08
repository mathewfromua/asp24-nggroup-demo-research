"""Deterministically regenerate synthetic extension; never changes core products or sources."""
from pathlib import Path
import json,copy,math,hashlib
root=Path(__file__).resolve().parent.parent
b=json.loads((root/'evidence/refinement-20261008/catalog-before.json').read_text())
brands=['KRYNET','OBRYS','TYVRA','DOVRIX','LUNETRA']
targets={'ups':48,'optics':64,'switches':64,'cable':56,'wifi':48,'splitters':40,'meters':32,'injectors':32}
prefix={'ups':'u','optics':'o','switches':'s','cable':'c','wifi':'a','splitters':'p','meters':'m','injectors':'i'}
nf=lambda val,unit,field:{'value':val,'unit':unit,'derivedFrom':field}
fmt=lambda v:str(v).replace('.',',')
items=[]
for group,total in targets.items():
 for n in range(total-8):
  brand=brands[n%len(brands)]; suffix=prefix[group]+f'{n+9:02d}'; sku='DEMO-'+suffix.upper(); props={}; nums={};price=0;unit='шт.';ud={'kind':'piece','integerOnly':True};family=brand+' '+{'ups':'DC','optics':'Optic','switches':'Node','cable':'Line','wifi':'Air','splitters':'Split','meters':'Measure','injectors':'Power'}[group]
  if group=='ups':
   power=[24,36,48,60,72,90,120,150][n%8]; energy=power*2+(n//8)*24; mass=None if n%9==0 else 220+energy*5
   outs=['5 / 9 / 12 В','9 / 12 В','12 / 24 В'][n%3] if power<90 else '12 / 24 В'
   props={'Потужність':f'{power} Вт','Запас енергії':f'{energy} Вт·год','Виходи':outs,'Роз’єм DC':'5,5 × '+('2,5' if power>72 else '2,1')+' мм','Полярність':'Плюс у центрі','Маса':f'{mass} г' if mass else None}
   nums={'powerW':nf(power,'W','Потужність'),'energyWh':nf(energy,'Wh','Запас енергії'),'massG':nf(mass,'g','Маса')};name=f'{brand} DC{power} E{energy}';price=(950+power*20+energy*8+n%5*30)*100
   desc=f'Умовне резервне джерело: {power} Вт загалом і {energy} Вт·год номінальної енергії. Для порівняння потужності та запасу енергії.'
   compat='Вихідна напруга, струм, роз’єм і полярність потребують окремої перевірки. Енергія не є виміряним часом роботи; це не схема підключення.'
  elif group=='optics':
   profiles=[(1,10,'LC duplex','SFP','Одномодове','1310 нм'),(1,20,'SC duplex','SFP','Одномодове','1310 нм'),(1,40,'LC duplex','SFP','Одномодове','1550 нм'),(10,.3,'LC duplex','SFP+','Багатомодове','850 нм'),(10,10,'LC duplex','SFP+','Одномодове','1310 нм'),(10,40,'LC duplex','SFP+','Одномодове','1550 нм'),(25,.1,'LC duplex','SFP28','Багатомодове','850 нм'),(25,10,'LC duplex','SFP28','Одномодове','1310 нм'),(1,20,'LC simplex','SFP','Одномодове','TX 1310 / RX 1550 нм'),(1,20,'LC simplex','SFP','Одномодове','TX 1550 / RX 1310 нм'),(10,20,'LC simplex','SFP+','Одномодове','TX 1270 / RX 1330 нм'),(10,20,'LC simplex','SFP+','Одномодове','TX 1330 / RX 1270 нм'),(100,10,'LC duplex','QSFP28','Одномодове','1271 / 1291 / 1311 / 1331 нм'),(100,.1,'MPO','QSFP28','Багатомодове','850 нм')]
   speed,dist,conn,form,fiber,wave=profiles[n%14]; grade=n//14; temp=['0…+70 °C','−40…+85 °C'][grade%2]
   props={'Швидкість':f'{speed} Гбіт/с','Роз’єм':conn,'Дальність':f'{fmt(dist)} км','Форм-фактор':form,'Волокно':fiber,'Моніторинг':'DDM' if grade<2 else 'DDM + журнал','Довжина хвилі':wave,'Температура':temp}
   nums={'speedGbps':nf(speed,'Gbps','Швидкість'),'distanceKm':nf(dist,'km','Дальність')};name=f'{brand} {form} {speed}G {fmt(dist)}K '+('BX-U' if n%14 in [8,10] else 'BX-D' if n%14 in [9,11] else conn.split()[0])+(' Industrial' if grade%2 else ' Core')+(' Trace' if grade>=2 else '');price=(400+speed*80+int(dist)*45+grade*170)*100
   desc=f'Умовний модуль {form}: {fiber.lower()} волокно, {conn}, {speed} Гбіт/с. Дальність — ознака демонстраційного добору.'
   compat='Порт, волокно, оптичний бюджет і друга сторона лінії потребують звірення. Для BiDi потрібна узгоджена TX/RX-пара. Сумісність реального обладнання не заявлена.'
  elif group=='switches':
   ports=[5,8,16,24,48,8,16,24][n%8];speed=[1,2.5,10][(n//8)%3]; managed=['Некерований','L2','L3'][n%3]; poe=n%3!=0;budget=ports*[15,30,45][n//8%3] if poe else 0;sfp=2 if speed==1 and ports>=8 else 0; sfpp=2 if speed>1 else 0
   props={'LAN-порти':str(ports),'Швидкість':f'{fmt(speed)} Гбіт/с','PoE':f'Так, {budget} Вт' if poe else 'Ні','Керування':managed,'SFP-порти':str(sfp),'SFP+-порти':str(sfpp),'Корпус':'Метал','Бюджет PoE':f'{budget} Вт','Монтаж':'Стійка 19″' if ports>=16 else 'Настільний','Охолодження':'Пасивне' if n//8%2==0 else 'Активне'}
   nums={'lanPorts':nf(ports,'count','LAN-порти'),'speedGbps':nf(speed,'Gbps','Швидкість'),'sfpPorts':nf(sfp,'count','SFP-порти'),'sfpPlusPorts':nf(sfpp,'count','SFP+-порти'),'poeBudgetW':nf(budget,'W','Бюджет PoE')};name=f'{brand} Node {ports} {fmt(speed)}G '+('PoE '+str(budget) if poe else 'Data')+f' R{n//24+1}';price=(800+ports*170+speed*200+budget*14+n*11)*100
   desc=f'Умовний комутатор на {ports} LAN-портів: {managed.lower()}, {fmt(speed)} Гбіт/с. Порти розширення показано окремо.'
   compat='Кількість роз’ємів не означає сумісності SFP/SFP+. Бюджет PoE спільний для всіх портів; режим живлення конкретного пристрою потребує перевірки.'
  elif group=='cable':
   cat=['Cat 5e','Cat 6','Cat 6A'][n%3];length=[100,305,500][(n//3)%3];outside=(n//9)%2==1;shield=['U/UTP','F/UTP','S/FTP'][(n//18)%3];material='CCA' if n%12==0 and not outside and cat=='Cat 5e' else 'Cu';diam=[.48,.51,.56][n%3];shell='PE' if outside else ['PVC','LSZH'][n//18%2]
   props={'Матеріал':material,'Застосування':'Надворі' if outside else 'У приміщенні','Категорія':cat,'Пари':'4','Оболонка':shell,'Довжина бухти':f'{length} м','Екранування':shield,'Діаметр провідника':f'{fmt(diam)} мм'}
   nums={'pairs':nf(4,'count','Пари'),'reelM':nf(length,'m','Довжина бухти')};unit=f'бухта {length} м';ud={'kind':'reel','lengthM':length,'integerOnly':True};name=f'{brand} Line {cat.replace("Cat ","C")} {shield} '+('Field' if outside else 'Core')+f' {length}'+(' Alloy' if material=='CCA' else '');price=int(length*(15+6*(n%3)+4*(n//18)+3*outside)+n%5*70)*100
   desc=f'Умовний кабель {cat}, {material}, {shield}; '+('для зовнішнього прокладання' if outside else 'для прокладання у приміщенні')+f'. Ціла бухта {length} м.'
   compat=f'Одна одиниця кошика — бухта {length} м, не метр. Матеріал і категорія тут навчальні ознаки, не сертифікація. Реальна придатність і пожежні вимоги потребують документа.'
  elif group=='wifi':
   gen=[5,6,'6E',7][n%4];ether=[1,2.5,5,10][(n//4)%4];power=[8,13,22,32][n%4];env='Надворі' if n//16%2 else 'Приміщення';mount=['Стеля','Стіна','Настільне'][n//4%3];bands='2,4 / 5 / 6 ГГц' if gen in ['6E',7] else '2,4 / 5 ГГц';poe='802.3af' if power<=13 else '802.3at' if power<=25.5 else '802.3bt'
   props={'Стандарт Wi-Fi':f'Wi-Fi {gen}','Діапазони':bands,'Ethernet':f'{fmt(ether)} Гбіт/с','Живлення PoE':poe,'Монтаж':mount,'Середовище':env,'Гранична споживана потужність':f'{power} Вт','Потоки MIMO':'2×2' if n<24 else '4×4'}
   nums={'ethernetGbps':nf(ether,'Gbps','Ethernet'),'powerInputMaxW':nf(power,'W','Гранична споживана потужність')};name=f'{brand} Air {gen} {fmt(ether)}G '+('Outdoor' if env=='Надворі' else mount.replace('Стеля','Ceiling').replace('Стіна','Wall').replace('Настільне','Desk'))+(' Pro' if n>=24 else '');price=int(1800+n%4*950+ether*300+n*35)*100
   desc=f'Умовна точка доступу Wi-Fi {gen}; {env.lower()}, монтаж: {mount.lower()}. Ethernet і живлення показано незалежно від радіостандарту.'
   compat='Радіостандарт не гарантує швидкості, покриття чи дозволу на використання діапазону. PoE і вимоги середовища звіряють перед реальним монтажем.'
  elif group=='splitters':
   outputs=[2,4,8,16,32,64][n%6];case=['ABS','Касета LGX','Міні-корпус','Касета для боксу'][(n//6)%4];conn=['SC/UPC','SC/APC','LC/UPC'][n//12%3];loss=None if n%7==0 else round(10*math.log10(outputs)+.8+(n//6%4)*.15,2)
   props={'Коефіцієнт ділення':f'1×{outputs}','Виконання':case,'Роз’єм':conn,'Волокно':'Одномодове','Довжини хвиль':'1260–1650 нм','Внесені втрати':f'{fmt(loss)} дБ' if loss else None,'Монтаж':'Оптичний бокс' if case!='Касета LGX' else 'Панель LGX'}
   nums={'outputs':nf(outputs,'count','Коефіцієнт ділення')};name=f'{brand} Split 1×{outputs} {case.replace("Касета ","").replace("Міні-корпус","Mini").replace("для боксу","Box")} {conn}';price=(200+outputs*55+n//6*100)*100
   desc=f'Умовний PLC-дільник 1×{outputs}: {case.lower()}, {conn}. Технологія, корпус і роз’єм — різні ознаки.'
   compat='Внесені втрати — синтетичний приклад, не протокол вимірювання; невказані значення не прирівняні до нуля. Монтаж і торці роз’ємів потрібно перевірити.'
  elif group=='meters':
   low=[-70,-65,-60,-50][n%4];high=[10,26][n//4%2];mem=[0,100,500,1000][n//4%4];expo='Немає' if mem==0 else ['USB','CSV','USB / CSV'][n//4%3];adapters=['SC / FC','SC / FC / LC','SC / FC / ST'][n//8%3]
   props={'Діапазон':f'−{abs(low)}…+{high} dBm','Адаптери':adapters,'Експорт':expo,'Довжини хвиль':'850 / 1300 / 1310 / 1490 / 1550 / 1625 нм','Пам’ять вимірів':str(mem),'Похибка':None if n%5==0 else '±0,25 дБ','Клас приладу':'Вимірювач оптичної потужності'}
   nums={'memorySamples':nf(mem,'count','Пам’ять вимірів')};name=f'{brand} Measure {abs(low)}-{high} M{mem}'+(' Link' if 'LC' in adapters else ' Field');price=(1000+mem*3+(high-10)*40+n*35)*100
   desc=f'Умовний вимірювач оптичної потужності: {props["Діапазон"]}, {adapters}. Приклад зіставлення діапазону, адаптерів і пам’яті.'
   compat='Діапазон залежить від довжини хвилі й виконання. Похибка не є роздільною здатністю; ці умовні числа не замінюють калібрування чи паспорта.'
  elif group=='injectors':
   pmax=[15.4,30,60,90][n%4];ports=[1,2,4][n//4%3];speed=[1,2.5,10][n//8%3];poe=['802.3af','802.3at','802.3bt Type 3','802.3bt Type 4'][n%4];budget=round(ports*pmax,1)
   props={'PoE':poe,'Сумарна вихідна потужність':f'{fmt(budget)} Вт','Потужність на порт':f'{fmt(pmax)} Вт','Швидкість':f'{fmt(speed)} Гбіт/с','PoE-порти':str(ports),'Вхідне живлення':'100–240 В AC','Узгодження живлення':'Автоматичне','Тип':'Активний'}
   nums={'budgetW':nf(budget,'W','Сумарна вихідна потужність'),'portMaxW':nf(pmax,'W','Потужність на порт'),'speedGbps':nf(speed,'Gbps','Швидкість'),'ports':nf(ports,'count','PoE-порти')};name=f'{brand} Power {ports}P {fmt(pmax)}W {fmt(speed)}G';price=int(350+ports*pmax*18+speed*80+n*11)*100
   desc=f'Умовний PoE-інжектор: {ports} {'порт' if ports==1 else 'порти'}, {fmt(pmax)} Вт на порт, спільна межа {fmt(budget)} Вт.'
   compat='Значення задано на стороні джерела, без гарантії потужності після кабелю. Потрібні узгоджені режими обох пристроїв; пасивне й узгоджуване живлення не взаємозамінні.'
  price=int(price);available=n%7!=0;ng=True;nums['priceCents']=nf(price,'UAH_cent','price')
  row={'id':suffix,'group':group,'name':name,'code':suffix.upper(),'sku':sku,'price':price,'available':available,'props':props,'desc':desc,'compat':compat,'ng':ng,'unit':unit,'unitDefinition':ud,'revision':'D1','aliases':[],'family':family,'manufacturer':brand,'typeLabel':b['groups'][group]['typeLabel'],'isDemo':True,'sourceKind':'synthetic-ui-fixture','legacyId':False,'titleLines':[name,b['groups'][group]['typeLabel']],'sourceNote':'Умовний виробник і модель; синтетичні параметри для перевірки інтерфейсу. Не паспорт реального обладнання.','storyId':group+'-origin','demoDocument':{'id':suffix+'-D1','revision':'D1','type':'Демонстраційний технічний опис','language':'uk','source':'generate_from_catalog','containsCertification':False},'availabilityState':'available' if available else 'unavailable','numericFacets':nums,'knownMissingFields':[k for k,v in props.items() if v is None],'tags':[group,brand.lower()]+(['in-stock'] if available else [])}
  items.append(row)
# Reject collisions, don't quietly rename models to hide a data problem.
allrows=b['products']+items
for key in ['id','sku','name']:
 vals=[p[key] for p in allrows]
 assert len(vals)==len(set(vals)),(key,[v for v in set(vals) if vals.count(v)>1])
(root/'catalog-expanded.js').write_text('// Deterministic fictional catalogue extension. Source: scripts/generate-catalog.py.\nexport const expandedProducts = '+json.dumps(items,ensure_ascii=False,indent=2)+';\n')
(root/'evidence/refinement-20261008/catalog-summary.json').write_text(json.dumps({'total':len(allrows),'preserved':len(b['products']),'added':len(items),'targets':targets,'syntheticManufacturers':sorted(set(p.get('manufacturer',p['family']) for p in allrows)),'seed':'deterministic-v1-no-random','realProductClaims':False},ensure_ascii=False,indent=2))
print('Created catalogue',len(allrows),'models',len(items),'new')
