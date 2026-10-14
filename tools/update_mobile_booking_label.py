from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
files=[ROOT/'index.html',ROOT/'tools/build_regions.py']+list((ROOT/'regions').glob('*.html'))
old='<span>장비 · 견적 전화 상담</span>'
new='<span>장비 예약 친절 상담</span>'
count=0
for p in files:
    text=p.read_text(encoding='utf-8')
    if old in text:
        p.write_text(text.replace(old,new),encoding='utf-8')
        count+=1
print(f'Updated booking label in {count} files')
