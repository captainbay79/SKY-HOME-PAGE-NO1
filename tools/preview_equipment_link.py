"""Create an isolated placement proposal; do not change live pages."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
text=(ROOT/'index.html').read_text(encoding='utf-8')
text,count=re.subn(r'<a class="hero-secondary hero-equipment-link"[^>]*>.*?</a>','',text,count=1,flags=re.S)
assert count==1
link='<a class="service-equipment-link" href="#equipment"><span>장비 먼저 살펴보기</span><span class="equipment-down-arrow" aria-hidden="true">↓</span></a>'
text,count=re.subn(r'<a class="service-call"[^>]*>.*?</a>',link,text,count=1,flags=re.S)
assert count==1
text=text.replace('<head>','<head><base href="../">',1)
text=text.replace('<section class="service-band"','<section id="service-preview" class="service-band"',1)
text=text.replace('href="#','href=".preview/equipment-link-preview.html#')
style='''<style>
.service-band{background:#f5f5f1;color:#171a1b;padding:40px 0 30px;border-bottom:1px solid #deded7}
.service-kicker{color:#666a68;font-size:13px;letter-spacing:0}
.service-band h2{font-size:clamp(26px,3.3vw,40px);margin-bottom:28px}
.service-benefits article{border-color:#dddfda;padding-top:20px}
.service-symbol{background:#fff0e5;color:#e8510a;width:40px;height:40px}
.service-benefits h3{font-size:20px}
.service-benefits p{color:#505653;font-size:15px;line-height:1.75}
.service-equipment-link{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px;border-top:1px solid #161a1b55;margin-top:25px;padding:20px 0 0;font-size:21px;font-weight:900;letter-spacing:-.5px;line-height:1.5}
.service-equipment-link .equipment-down-arrow{font-size:36px;line-height:1.15;font-weight:700;color:#e8510a}
.service-equipment-link:hover{color:#e8510a}.service-equipment-link:focus-visible{outline-color:#171a1b}
@media(max-width:760px){.service-band{padding:30px 0 25px}.service-band h2{font-size:27px;line-height:1.4}.service-benefits{gap:18px}.service-benefits article{padding-top:18px}}
@media(max-width:480px){.service-equipment-link{font-size:19px}.service-band h2{font-size:25px}.service-benefits h3{font-size:19px}.service-benefits p{font-size:14px}}
</style>'''
text=text.replace('</head>',style+'</head>',1)
out=ROOT/'.preview/equipment-link-preview.html'
out.write_text(text,encoding='utf-8')
assert 'hero-equipment-link' not in text
assert text.count('class="service-equipment-link"')==1
print('Created placement preview only; live website and deployment unchanged.')
