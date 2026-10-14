from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
count=0
for p in (ROOT/'regions').glob('*.html'):
    if p.name=='index.html': continue
    s=p.read_text(encoding='utf-8')
    s=re.sub(r'<a\b[^>]*\bdownload="[^"]*"[^>]*>이 지역 썸네일 다운로드 ↓</a>','',s)
    sections=list(re.finditer(r'<section\b[^>]*>.*?</section>',s,re.S))
    directory=next((m for m in sections if 'AREA DIRECTORY' in m.group()),None)
    gallery=next((m for m in sections if 'REAL FIELD PHOTOGRAPHS' in m.group()),None)
    if directory and gallery and directory.start()<gallery.start():
        block=directory.group()
        s=s[:directory.start()]+s[directory.end():]
        gallery=next(m for m in re.finditer(r'<section\b[^>]*>.*?</section>',s,re.S) if 'REAL FIELD PHOTOGRAPHS' in m.group())
        s=s[:gallery.end()]+block+s[gallery.end():]
    if '이 지역 썸네일 다운로드' in s: raise ValueError(f'Download removal failed: {p}')
    if directory:
        if s.index('AREA DIRECTORY')<s.index('REAL FIELD PHOTOGRAPHS'): raise ValueError(f'Wrong order: {p}')
    p.write_text(s,encoding='utf-8')
    count+=1
p=ROOT/'tools/build_regions.py'
s=p.read_text(encoding='utf-8')
s=s.replace('{child_section}<section class="section light"><div class="wrap"><div class="section-heading"><div><p class="eyebrow">REAL FIELD PHOTOGRAPHS', '<section class="section light"><div class="wrap"><div class="section-heading"><div><p class="eyebrow">REAL FIELD PHOTOGRAPHS')
s=re.sub(r'<a class="region-back" href="../assets/region-thumbnails/\{code\}.jpg" download="\{escape\(full\)\}-스카이차-썸네일.jpg">이 지역 썸네일 다운로드 ↓</a>','',s)
anchor='<section class="section light"><div class="wrap regional-faq"><p class="eyebrow">QUESTIONS & ANSWERS'
if '\n{child_section}'+anchor not in s: s=s.replace(anchor,'{child_section}'+anchor)
p.write_text(s,encoding='utf-8')
print(f'PASS: removed downloads on {count} regional pages; all directory sections follow gallery; generator updated')
