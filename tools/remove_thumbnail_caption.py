from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
pattern=r'<figcaption>실제 작업 사진 · 장비 배치 참고용<br>촬영 지역 미확인 / .*?</figcaption>'
count=0
for p in [ROOT/'index.html']+list((ROOT/'regions').glob('*.html'))+[ROOT/'tools/build_regions.py']:
    s=p.read_text(encoding='utf-8')
    s,n=re.subn(pattern,'',s)
    if n:
        p.write_text(s,encoding='utf-8')
        count+=n
    if '실제 작업 사진 · 장비 배치 참고용' in s:
        raise ValueError(f'Caption remains in {p}')
print(f'PASS: removed {count} thumbnail captions from pages and generator')
