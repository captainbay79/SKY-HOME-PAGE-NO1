"""Apply approved text styling and gallery combinations without changing thumbnails."""
from pathlib import Path
import json
import re
from regional_gallery import gallery_section
from site_watermarks import watermark

ROOT = Path(__file__).resolve().parents[1]
plan = json.loads((ROOT / '.preview/regional-gallery-plan.json').read_text(encoding='utf-8'))
catalog = json.loads((ROOT / 'assets/thumbnail-photo-catalog.json').read_text(encoding='utf-8'))
by_file = {photo['file']: photo for photo in catalog}
assert len(plan) == 5351
assert len({tuple(sorted(by_file[file]['sha256'] for file in files)) for files in plan.values()}) == len(plan)
assert all(len(files) == len(set(files)) == 8 for files in plan.values())
(ROOT / 'assets/region-gallery-assignments.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding='utf-8')
watermark_path = ROOT / 'assets/watermark-catalog.json'
watermark_catalog = json.loads(watermark_path.read_text(encoding='utf-8'))
watermark_catalog = [entry for entry in watermark_catalog if not entry['file'].startswith('assets/watermarked/gallery/')]
for i, photo in enumerate(catalog):
    source = ROOT / photo['file']
    destination = ROOT / 'assets/watermarked/gallery' / source.name
    if not destination.exists(): watermark(source, destination)
    watermark_catalog.append({'source':photo['file'], 'file':destination.relative_to(ROOT).as_posix(),
                              'style':'C-repeated', 'opacity':.15, 'text':'키다리스카이차', 'thumbnail_excluded':True})
    if (i+1) % 100 == 0: print(f'{i+1}/{len(catalog)} gallery watermark copies', flush=True)
watermark_path.write_text(json.dumps(watermark_catalog, ensure_ascii=False, indent=2), encoding='utf-8')
main = ROOT / 'index.html'
pages = [main] + [ROOT / 'regions' / f'{code}.html' for code in plan]
for i, path in enumerate(pages):
    text = path.read_text(encoding='utf-8')
    thumb_before = re.search(r'<img class="regional-thumbnail"[^>]+>', text) if path != main else None
    text = re.sub(r'(<div class="equipment-visual"[^>]*><strong>)([1235])(<small>톤</small></strong>)',
                  r'\1<span class="equipment-number">\2</span>\3', text)
    if path != main:
        text, count = re.subn(r'<section id="field".*?</section>', gallery_section(path.stem), text, count=1, flags=re.S)
        assert count == 1
        assert thumb_before[0] == re.search(r'<img class="regional-thumbnail"[^>]+>', text)[0]
        assert text.count('<summary>') == 5
    text = text.replace('?v=regional-main3', '?v=regional-refinement4')
    path.write_text(text, encoding='utf-8')
    if (i+1) % 1000 == 0: print(f'{i+1}/{len(pages)} pages updated', flush=True)
styles = ROOT / 'styles.css'
styles.write_text(styles.read_text(encoding='utf-8') + "\n.equipment-visual strong{font-family:'Malgun Gothic',sans-serif;align-items:center;line-height:1;gap:6px}.equipment-visual .equipment-number{line-height:1;-webkit-text-stroke:1.2px #171a1b;paint-order:stroke fill;text-shadow:2px 3px 3px #0005}.equipment-visual strong small{font-family:inherit;font-size:.6em;line-height:1;font-weight:900}\n", encoding='utf-8')
styles = ROOT / 'region.css'
styles.write_text(styles.read_text(encoding='utf-8') + '\n.regional-main-hero .hero-message small{font-size:30px;font-weight:900;letter-spacing:-1px}.regional-main-gallery .field-grid img{object-fit:contain;background:#e5e5e0;aspect-ratio:4/3}@media(max-width:760px){.regional-main-hero .hero-message small{font-size:28px}}@media(max-width:480px){.regional-main-hero .hero-message small{font-size:25px}}\n', encoding='utf-8')
print(f'Applied approved refinements: {len(plan)} distinct eight-photo galleries; thumbnails preserved.', flush=True)
