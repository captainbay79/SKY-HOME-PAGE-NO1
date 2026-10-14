"""Prepare approval previews; live pages and thumbnail assets remain untouched."""
from pathlib import Path
from html import escape
import hashlib
import json
import random
import re
from site_watermarks import watermark

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.preview'
rows = json.loads((ROOT / 'assets/regions.json').read_text(encoding='utf-8'))
photos = json.loads((ROOT / 'assets/thumbnail-photo-catalog.json').read_text(encoding='utf-8'))
manifest = {row['code']: row for row in json.loads((ROOT / 'assets/region-pages.json').read_text(encoding='utf-8'))}
# Reuse the approved source pool, but use a different eight-photo combination per page.
combinations = set()
assignments = {}
for row in rows:
    rng = random.Random(int(hashlib.sha256(('gallery-v2-' + row[0]).encode()).hexdigest(), 16))
    pool = [photo for photo in photos if photo['file'] != manifest[row[0]]['thumbnail_photo']]
    while True:
        chosen = rng.sample(pool, 8)
        key = tuple(sorted(photo['sha256'] for photo in chosen))
        if key not in combinations:
            combinations.add(key)
            break
    assignments[row[0]] = [photo['file'] for photo in chosen]
assert len(combinations) == len(rows)
(OUT / 'regional-gallery-plan.json').write_text(json.dumps(assignments, ensure_ascii=False, indent=2), encoding='utf-8')
code = '4400000000'
by_file = {photo['file']: photo for photo in photos}
figures = []
for i, file in enumerate(assignments[code]):
    photo = by_file[file]
    destination = OUT / 'gallery-watermarked' / Path(file).name
    watermark(ROOT / file, destination)
    figures.append(f'<figure><div><img src="../.preview/gallery-watermarked/{destination.name}" alt="실제 스카이차 작업 사진 {i+1} · 장비 배치 참고" width="{photo["width"]}" height="{photo["height"]}" loading="lazy"><span>FIELD / {i+1:02d}</span></div><figcaption><h3>장비 배치 참고 사진 {i+1:02d}</h3><p>작업 위치와 차량 설치 공간을 참고하세요.</p></figcaption></figure>')
gallery = '<section id="field" class="section light"><div class="wrap"><div class="section-heading"><div><p class="eyebrow">03 / ON THE FIELD</p><h2>실제 현장에서,<br>사진으로 확인하세요.</h2></div><p>사진 속 높이보다 중요한 건 현장의 조건.<br>작업 위치와 차량을 세울 공간을 함께 살핍니다.</p></div><div class="field-grid">' + ''.join(figures) + '</div></div></section>'
page = (ROOT / 'regions' / f'{code}.html').read_text(encoding='utf-8')
page = page.replace('<head>', '<head><base href="../regions/">', 1)
page = re.sub(r'<section id="field".*?</section>', gallery, page, count=1, flags=re.S)
page = re.sub(r'(<div class="equipment-visual"[^>]*><strong>)([1235])(<small>톤</small></strong>)', r'\1<span class="equipment-number">\2</span>\3', page)
style = '''<style>
.regional-main-hero .hero-message small{font-size:30px;font-weight:900;letter-spacing:-1px}
.equipment-visual strong{font-family:'Malgun Gothic',sans-serif;align-items:center;line-height:1;gap:6px}
.equipment-visual .equipment-number{line-height:1;-webkit-text-stroke:1.2px #171a1b;paint-order:stroke fill;text-shadow:2px 3px 3px #0005}
.equipment-visual strong small{font-family:inherit;font-size:.6em;line-height:1;font-weight:900}
@media(max-width:760px){.regional-main-hero .hero-message small{font-size:28px}}
@media(max-width:480px){.regional-main-hero .hero-message small{font-size:25px}}
</style>'''
page = page.replace('</head>', style + '</head>', 1)
(OUT / 'regional-refinements.html').write_text(page, encoding='utf-8')
# An eight-photo overview makes the proposed gallery easy to review at a glance.
overview = f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><base href="../regions/"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="../styles.css?v=regional-main3"><style>body{{background:#f3f2ee;padding:28px}}h1{{font-size:27px;margin-bottom:12px}}.field-grid{{grid-template-columns:repeat(2,1fr);gap:18px}}.field-grid img{{aspect-ratio:4/3;object-fit:contain;background:#e5e5e0}}.field-grid h3{{font-size:14px}}.field-grid p{{font-size:11px}}.field-grid figcaption{{padding-top:8px}}.intro{{font-size:13px;line-height:1.7;margin-bottom:20px}}</style></head><body><h1>충청남도 페이지 · 작업사진 구성 시안</h1><p class="intro">지역마다 서로 다른 원본 8장 조합 · 기존 C 워터마크 15%<br>촬영 지역을 확인하지 않은 장비 배치 참고 사진입니다.</p><div class="field-grid">{''.join(figures)}</div></body></html>'''
(OUT / 'regional-gallery-overview.html').write_text(overview, encoding='utf-8')
print(f'Prepared preview only; {len(combinations)} distinct gallery combinations, 8 photos each.')

