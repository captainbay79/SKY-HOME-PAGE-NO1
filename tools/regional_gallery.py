"""Render the approved, distinct eight-photo combinations from original photos."""
from functools import lru_cache
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def data():
    assignments = json.loads((ROOT / 'assets/region-gallery-assignments.json').read_text(encoding='utf-8'))
    photos = json.loads((ROOT / 'assets/thumbnail-photo-catalog.json').read_text(encoding='utf-8'))
    captions_path=ROOT/'assets/photo-captions.json'
    captions=json.loads(captions_path.read_text(encoding='utf-8')) if captions_path.exists() else {}
    return assignments, {photo['file']: photo for photo in photos}, captions

def gallery_section(code):
    assignments, photos, captions = data()
    figures = []
    for i, file in enumerate(assignments[code]):
        photo = photos[file]
        src = '../assets/watermarked/gallery/' + Path(file).name
        title=escape(captions.get(file,{}).get('title','스카이차와 작업대 배치'))
        figures.append(f'<figure><div><img src="{src}" alt="{title}" width="{photo["width"]}" height="{photo["height"]}" loading="lazy"><span>FIELD / {i+1:02d}</span></div><figcaption><h3>{title}</h3></figcaption></figure>')
    return '<section id="field" class="section light regional-main-gallery"><div class="wrap"><div class="section-heading"><div><p class="eyebrow">03 / ON THE FIELD</p><h2>실제 현장에서,<br>사진으로 확인하세요.</h2></div><p>사진 속 높이보다 중요한 건 현장의 조건.<br>작업 위치와 차량을 세울 공간을 함께 살핍니다.</p></div><div class="field-grid">' + ''.join(figures) + '</div></div></section>'
