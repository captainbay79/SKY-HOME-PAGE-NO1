from pathlib import Path
from PIL import Image
import json

ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'assets/region-pages.json').read_text(encoding='utf-8'))
files=[ROOT/'script.js',ROOT/'tools/build_regions.py']+list((ROOT/'regions').glob('*.html'))
for p in files:
    s=p.read_text(encoding='utf-8')
    if 'v=shadow1' in s: p.write_text(s.replace('v=shadow1','v=shadow2'),encoding='utf-8')
for row in manifest:
    with Image.open(ROOT/row['thumbnail']) as im:
        if im.size!=(800,600): raise ValueError(f'Wrong image size: {row["code"]}: {im.size}')
print(f'PASS: {len(manifest)} thumbnails are 800x600; final cache version updated')
