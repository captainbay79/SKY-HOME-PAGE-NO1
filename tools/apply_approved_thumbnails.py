"""Update all existing regional thumbnails without changing photo assignments."""
from pathlib import Path
from PIL import Image
import json
from thumbnail_design import make_thumbnail

ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'assets/region-pages.json').read_text(encoding='utf-8'))
rows={r[0]:r for r in json.loads((ROOT/'assets/regions.json').read_text(encoding='utf-8'))}
for i,entry in enumerate(manifest):
    path=ROOT/entry['thumbnail']
    make_thumbnail(rows[entry['code']],{'file':entry['thumbnail_photo']},path)
    with Image.open(path) as im:
        if im.size!=(800,600): raise ValueError(f'Wrong thumbnail dimensions: {path.name}')
    if (i+1)%1000==0: print(f'Updated {i+1}/{len(manifest)} approved thumbnails',flush=True)
for p in [ROOT/'script.js',ROOT/'tools/build_regions.py']+list((ROOT/'regions').glob('*.html')):
    s=p.read_text(encoding='utf-8')
    for version in ['v=shadow1','v=shadow2','v=approved-bold1','v=approved-outline2']:
        s=s.replace(version,'v=approved-final3')
    p.write_text(s,encoding='utf-8')
status_path=ROOT/'assets/region-build.json'
status=json.loads(status_path.read_text(encoding='utf-8'))
status['thumbnail_design']='approved-heavier-region-all-text-black-outline-shadow'
status_path.write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'PASS: applied {len(manifest)} approved thumbnails and updated page cache versions',flush=True)
