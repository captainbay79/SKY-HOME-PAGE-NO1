"""Prepare the supplied photographs and assign different photos within sibling lists."""
from pathlib import Path
from PIL import Image, ImageOps
import hashlib
import json
import random

ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path(r'C:\Users\Over kim\Documents\홈페이지 제작용 이미지\광고기획 작업사진')

def prepare():
    files=sorted(SOURCE.glob('advertising-work-*.jpg'))
    if not files: raise ValueError('No supplied work photographs found')
    out=ROOT/'assets/thumbnail-photos'
    out.mkdir(exist_ok=True)
    catalog_path=ROOT/'assets/thumbnail-photo-catalog.json'
    if catalog_path.exists():
        cached=json.loads(catalog_path.read_text(encoding='utf-8'))
        by_name={p['original_filename']:p for p in cached}
        if len(cached)==len(files) and all(source.name in by_name and
                (ROOT/by_name[source.name]['file']).exists() and
                (ROOT/by_name[source.name]['file']).stat().st_mtime>=source.stat().st_mtime for source in files):
            print(f'Reused {len(cached)} prepared original photos',flush=True)
            return cached
    catalog=[]
    for i,source in enumerate(files):
        destination=out/f'{source.stem}.jpg'
        with Image.open(source) as raw:
            raw.draft('RGB',(1800,1800))
            im=ImageOps.exif_transpose(raw).convert('RGB')
            im.thumbnail((1400,1400))
            # Store natural geometry; no image reconstruction or object movement.
            im.save(destination,quality=80,optimize=True)
            width,height=im.size
        catalog.append({'file':destination.relative_to(ROOT).as_posix(),'original_filename':source.name,
                        'source':'user_provided_folder','sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                        'width':width,'height':height,'region':None,'focal_point':[.5,.75],
                        'processing':'EXIF orientation, proportional resize and JPEG compression only'})
        if (i+1)%100==0: print(f'Prepared {i+1}/{len(files)} original photos',flush=True)
    (ROOT/'assets/thumbnail-photo-catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf-8')
    return catalog

def assign(children,photos):
    # Duplicate copies of one original must not appear as different photos.
    pool=list({photo['sha256']:photo for photo in photos}.values())
    random.Random(20261013).shuffle(pool)
    mapping={}
    cursor=0
    def group(parent):
        nonlocal cursor
        siblings=children[parent]
        used=set()
        if parent in mapping: used.add(mapping[parent]['sha256'])
        for row in siblings:
            for _ in range(len(pool)):
                photo=pool[cursor%len(pool)]
                cursor+=1
                if photo['sha256'] not in used: break
            else: raise ValueError('More sibling regions than available different photographs')
            used.add(photo['sha256'])
            mapping[row[0]]=photo
        for row in siblings: group(row[0])
    group(None)
    return mapping
