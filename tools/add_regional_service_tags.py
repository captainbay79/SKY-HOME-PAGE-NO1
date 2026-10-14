from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
tags='<div class="hero-tags"><span>당일배차 · 빠른배차 가능</span><span>1톤부터 대형 장비까지</span><span>카드결제 가능</span></div>'
anchor='장비 제원 살펴보기 ↓</a>'
count=0
for p in (ROOT/'regions').glob('*.html'):
    if p.name=='index.html': continue
    s=p.read_text(encoding='utf-8')
    if tags not in s:
        if anchor not in s: raise ValueError(f'Missing insertion point: {p}')
        s=s.replace(anchor,anchor+tags,1)
        p.write_text(s,encoding='utf-8')
    if s.count(tags)!=1: raise ValueError(f'Incorrect tag block count: {p}')
    count+=1
p=ROOT/'tools/build_regions.py'
s=p.read_text(encoding='utf-8')
if tags not in s: s=s.replace(anchor,anchor+tags,1)
p.write_text(s,encoding='utf-8')
print(f'PASS: all {count} regional landing pages have the three service tags; generator updated')
