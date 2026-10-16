"""Apply the approved square thumbnail layout without regenerating page content.

Keeps an uncompressed local checkpoint. Does not publish or create archives.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import re
import shutil
from thumbnail_design import make_thumbnail

ROOT=Path(__file__).resolve().parents[1]
CHECKPOINT=ROOT/'.recovery/before-square-thumbnails-20261016'
VERSION='square-approved1'

def backup(path):
    dest=CHECKPOINT/path.relative_to(ROOT)
    if not dest.exists():
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(path,dest)

def update_markup(text):
    def image(m):
        tag=m[0]
        if 'region-thumbnails/' not in tag: return tag
        tag=re.sub(r'\b(width|height)="\d+"',lambda n:n[1]+'="1200"',tag)
        return re.sub(r'(region-thumbnails/[^"?<>]+\.jpg)(?:\?[^"<>]*)?',r'\1?v='+VERSION,tag)
    text=re.sub(r'<img\b[^>]*>',image,text)
    text=re.sub(r'(<meta property="og:image:(?:width|height)" content=")\d+("[^>]*>)',r'\g<1>1200\2',text)
    text=re.sub(r'(region-thumbnails/[^"?<>]+\.jpg)(?:\?[^"<>]*)?',r'\1?v='+VERSION,text)
    text=re.sub(r'region\.css(?:\?[^"<>]*)?', 'region.css?v='+VERSION,text)
    text=text.replace('styles.css?v=hero-proof6','styles.css?v='+VERSION)
    text=re.sub(r'script\.js\?v=[^"<>]+', 'script.js?v='+VERSION,text)
    return text

def main():
    rows=json.loads((ROOT/'assets/regions.json').read_text(encoding='utf-8'))
    by_id={r[0]:r for r in rows}
    manifest=json.loads((ROOT/'assets/region-pages.json').read_text(encoding='utf-8'))
    groups=json.loads((ROOT/'assets/region-name-groups.json').read_text(encoding='utf-8'))['by_code']
    pages=[ROOT/'index.html',*sorted((ROOT/'regions').glob('*.html'))]
    for page in pages: backup(page)
    for item in manifest: backup(ROOT/item['thumbnail'])
    print('Checkpoint saved for all page and thumbnail files',flush=True)
    representatives=[p for p in manifest if groups.get(p['code'],p['code'])==p['code']]
    def render(item):
        target=ROOT/item['thumbnail']
        temp=target.with_suffix('.square-tmp.jpg')
        make_thumbnail(by_id[item['code']],{'file':item['thumbnail_photo']},temp)
        temp.replace(target)
        return item['code']
    with ThreadPoolExecutor(max_workers=4) as pool:
        for i,code in enumerate(pool.map(render,representatives),1):
            if i%250==0 or i==len(representatives): print(f'Rendered {i}/{len(representatives)} distinct-name thumbnails',flush=True)
    for item in manifest:
        code=item['code']; canonical=groups.get(code,code)
        if code!=canonical:
            shutil.copyfile(ROOT/f'assets/region-thumbnails/{canonical}.jpg',ROOT/item['thumbnail'])
    for page in pages:
        text=page.read_text(encoding='utf-8')
        updated=update_markup(text)
        if text!=updated: page.write_text(updated,encoding='utf-8')
    summary={'version':VERSION,'size':[1200,1200],'thumbnails':len(manifest),
             'distinct_names':len(representatives),'pages':len(pages),
             'files':[str(p.relative_to(ROOT)) for p in pages]+[i['thumbnail'] for i in manifest]}
    (CHECKPOINT/'checkpoint.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Applied {len(manifest)} square thumbnails and updated {len(pages)} page references; no publication.',flush=True)

if __name__=='__main__': main()
