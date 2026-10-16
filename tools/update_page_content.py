from pathlib import Path
from html import escape
from collections import defaultdict
import json
import re
from faq_content import MAIN_FAQ,regional_faq

ROOT=Path(__file__).resolve().parents[1]
def details(questions):
    return ''.join(f'<details><summary>{escape(q)}</summary><p>{escape(a)}</p></details>' for q,a in questions)

p=ROOT/'index.html'
s=p.read_text(encoding='utf-8')
old='<a class="hero-secondary" href="#equipment">장비 먼저 살펴보기 <span>↓</span></a>'
new='<a class="hero-secondary hero-equipment-link" href="#equipment">장비 먼저 살펴보기 <span>↓</span></a>'
if new not in s:
    if old not in s: raise ValueError('Main equipment link not found')
    s=s.replace(old,'',1)
    tags='<div class="hero-tags"><span>당일배차 · 빠른배차 가능</span><span>1톤부터 대형 장비까지</span><span>카드결제 가능</span></div>'
    s=s.replace(tags,tags+new,1)
s=re.sub(r'<h1(?: class="hero-message")?>.*?</h1>','<h1 class="hero-message">더 높은 곳은<br>더 안전 하게.<em>고객의 안전을 최우선으로 생각합니다.</em></h1>',s,count=1)
s=s.replace('<h2>높은 곳의 일.<br>현장부터 살펴봅니다.</h2>','<h2>높은 곳의 고소작업,<br>안전하게 현장부터<br>확인해야 합니다.</h2>')
for ton,height in [(1,18),(2,23),(3,32),(5,45)]:
    old=f'<div class="equipment-visual" aria-label="대표 모델 최대 작업 높이 {height}미터"><span>WORKING HEIGHT</span><strong>{height}<small>m</small></strong><span>대표 모델 최대 높이</span></div>'
    new=f'<div class="equipment-visual" aria-label="{ton}톤 스카이차"><strong>{ton}<small>T</small></strong></div>'
    s=s.replace(old,new)
s=re.sub(r'<div class="faq"><h3>자주 묻는 질문</h3>.*?</div>','<div class="faq"><h3>자주 묻는 질문</h3>'+details(MAIN_FAQ)+'</div>',s,count=1,flags=re.S)
p.write_text(s,encoding='utf-8')

rows=json.loads((ROOT/'assets/regions.json').read_text(encoding='utf-8'))
children=defaultdict(list)
for row in rows: children[row[2]].append(row)
count=0
for row in rows:
    p=ROOT/'regions'/f'{row[0]}.html'
    s=p.read_text(encoding='utf-8')
    pattern=r'(<div class="wrap regional-faq"><p class="eyebrow">QUESTIONS & ANSWERS</p><h2>.*?</h2>).*?(</div></section>)'
    s,n=re.subn(pattern,lambda m:m[1]+details(regional_faq(row,children[row[0]]))+m[2],s,count=1,flags=re.S)
    if n!=1: raise ValueError(f'FAQ block missing: {p}')
    assert len(re.findall(r'<details>',s))==5,p
    p.write_text(s,encoding='utf-8')
    count+=1
p=ROOT/'tools/build_regions.py'
s=p.read_text(encoding='utf-8')
if 'from faq_content import regional_faq' not in s:
    s=s.replace('from site_watermarks import apply_site_watermarks','from site_watermarks import apply_site_watermarks\nfrom faq_content import regional_faq')
s,n=re.subn(r'        faq=\[.*?\n        \]\n', '        faq=regional_faq(row,own_children)\n',s,count=1,flags=re.S)
if n!=1 and 'faq=regional_faq(row,own_children)' not in s: raise ValueError('Generator FAQ not found')
p.write_text(s,encoding='utf-8')
print(f'PASS: main content updated; 5 tailored FAQs on all {count} regional landing pages and main; generator updated')
