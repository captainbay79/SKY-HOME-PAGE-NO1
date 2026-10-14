"""Check all generated pages, local links, images, headings and JSON-LD."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json
import re
from functools import lru_cache
from html import escape

ROOT = Path(__file__).resolve().parents[1]

@lru_cache(maxsize=None)
def exists(path):
    return path.exists()

class Inspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]; self.h1=0; self.ld=[]; self.in_ld=False; self.buffer=''
        self.robots=None; self.description=None; self.images=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='h1': self.h1+=1
        if tag=='a' and a.get('href'): self.links.append(a['href'])
        if tag=='link' and a.get('href') and a.get('rel')!='canonical': self.links.append(a['href'])
        if tag=='img':
            self.links.append(a['src']); self.images.append(a)
        if tag=='script' and a.get('src'): self.links.append(a['src'])
        if tag=='script' and a.get('type')=='application/ld+json': self.in_ld=True; self.buffer=''
        if tag=='meta' and a.get('name')=='robots': self.robots=a.get('content')
        if tag=='meta' and a.get('name')=='description': self.description=a.get('content')
    def handle_data(self,data):
        if self.in_ld: self.buffer+=data
    def handle_endtag(self,tag):
        if tag=='script' and self.in_ld:
            self.ld.append(json.loads(self.buffer)); self.in_ld=False

manifest=json.loads((ROOT/'assets/region-pages.json').read_text(encoding='utf-8'))
errors=[]
files=[ROOT/'index.html',ROOT/'regions/index.html']+[ROOT/r['page'] for r in manifest]
for i,p in enumerate(files):
    html=p.read_text(encoding='utf-8')
    page=Inspector(); page.feed(html)
    if 'class="service-band"' in html:
        if html.count('class="service-equipment-link"') != 1:
            errors.append(f'{p.name}: missing equipment navigation at consultation end')
        if 'hero-equipment-link' in html or 'class="service-call"' in html:
            errors.append(f'{p.name}: old consultation navigation remains')
        if 'styles.css?v=service-soft5' not in html:
            errors.append(f'{p.name}: outdated consultation stylesheet')
    if html.count('class="wrap business-info"')!=1: errors.append(f'{p.name}: missing or repeated business details')
    for value in ['417-16-27305','mailto:skyhi0482@gmail.com','카드결제시 사전요청, VAT별도','<dt>상호</dt><dd>스카이차</dd>']:
        if value not in html: errors.append(f'{p.name}: missing footer value {value}')
    for value in ['extra-field-heading','장비 배치 참고 사진 0','작업 위치와 차량 설치 공간을 참고하세요.','직접 제공해 주신 실제 현장 사진입니다. 촬영 지역이 확인되지 않아 특정 지역의 작업 사례로 표시하지 않습니다.']:
        if value in html: errors.append(f'{p.name}: removed text remains {value}')
    if page.h1!=1: errors.append(f'{p.name}: h1 count {page.h1}')
    if not page.description: errors.append(f'{p.name}: description missing')
    for href in page.links:
        uri=urlsplit(href)
        if uri.scheme or not uri.path: continue
        target=(ROOT/uri.path.lstrip('/')) if uri.path.startswith('/') else p.parent/unquote(uri.path)
        if not exists(target): errors.append(f'{p.name}: missing {href}')
    for image in page.images:
        if 'alt' not in image: errors.append(f'{p.name}: missing image alt')
        if 'assets/work/' in image['src'] or 'assets/regional-photos/' in image['src']:
            errors.append(f'{p.name}: unmarked live work photograph')
        if 'region-thumbnails/' in image['src'] and 'watermarked/' in image['src']:
            errors.append(f'{p.name}: thumbnail incorrectly watermarked')
    if (i+1)%1000==0: print(f'{i+1}/{len(files)} pages: links, assets, metadata and recent changes checked',flush=True)

main_html=(ROOT/'index.html').read_text(encoding='utf-8')
main_field=re.search(r'<section id="field".*?</section>',main_html,re.S)[0]
if main_field.count('class="field-grid"')!=1 or main_field.count('<figure>')!=8:
    errors.append('Main page: expected one continuous eight-photo gallery')
captions=json.loads((ROOT/'assets/photo-captions.json').read_text(encoding='utf-8'))
gallery_plan_path=ROOT/'assets/region-gallery-assignments.json'
gallery_plan=json.loads(gallery_plan_path.read_text(encoding='utf-8')) if gallery_plan_path.exists() else None
gallery_sets=set()
for row in manifest:
    if not (ROOT/row['thumbnail']).is_file(): errors.append(f'{row["code"]}: missing thumbnail')
    html=(ROOT/row['page']).read_text(encoding='utf-8')
    if 'class="regional-thumbnail"' not in html: errors.append(f'{row["code"]}: hero thumbnail missing')
    if 'og:image:width" content="800"' not in html or 'og:image:height" content="600"' not in html:
        errors.append(f'{row["code"]}: incorrect OG image dimensions')
    if gallery_plan:
        field=re.search(r'<section id="field".*?</section>',html,re.S)
        gallery_files=re.findall(r'<img src="([^"]+)"',field[0]) if field else []
        expected=['../assets/watermarked/gallery/'+Path(source).name for source in gallery_plan[row['code']]]
        if gallery_files!=expected or len(set(gallery_files))!=8: errors.append(f'{row["code"]}: incorrect eight-photo gallery')
        key=tuple(sorted(gallery_files))
        if key in gallery_sets: errors.append(f'{row["code"]}: repeated gallery combination')
        gallery_sets.add(key)
        if html.count('<span class="equipment-number">')!=4: errors.append(f'{row["code"]}: missing number styling')
        expected_titles=[escape(captions[source]['title']) for source in gallery_plan[row['code']]]
        actual_titles=re.findall(r'<figcaption><h3>(.*?)</h3></figcaption>',field[0]) if field else []
        if actual_titles!=expected_titles: errors.append(f'{row["code"]}: incorrect photograph captions')
        if field[0].count('class="field-grid"')!=1: errors.append(f'{row["code"]}: fragmented gallery')
        if html.count('<summary>')!=5: errors.append(f'{row["code"]}: expected five local FAQ entries')
        for value in ['class="service-band"','id="equipment"','id="services"','equipment-large','regional-main-gallery','id="equipment-dialog"']:
            if value not in html: errors.append(f'{row["code"]}: missing shared section {value}')
if (ROOT/'assets/thumbnail-photo-catalog.json').exists():
    catalog=json.loads((ROOT/'assets/thumbnail-photo-catalog.json').read_text(encoding='utf-8'))
    hashes={p['file']:p['sha256'] for p in catalog}
    mappings={r['code']:r for r in manifest}
    rows=json.loads((ROOT/'assets/regions.json').read_text(encoding='utf-8'))
    grouped={}
    for row in rows: grouped.setdefault(row[2],[]).append(row[0])
    for parent,codes in grouped.items():
        assignments=[hashes[mappings[code]['thumbnail_photo']] for code in codes]
        if len(set(assignments))!=len(assignments): errors.append(f'{parent}: repeated sibling photos')
if errors:
    print('\n'.join(errors[:30])); raise SystemExit(f'{len(errors)} failures')
print(f'PASS: {len(files)} HTML pages, {len(manifest)} thumbnails, local links, H1, meta descriptions, image alt text, JSON-LD')
print(f'PASS: footer details, deleted text, main continuous gallery, {len(gallery_sets)} distinct regional eight-photo galleries, photograph captions and equipment styling')
