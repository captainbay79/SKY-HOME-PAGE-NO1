"""Apply the approved service band and clarified equipment labels."""
import ast
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
preview = ast.parse((root / 'tools/preview_service_band.py').read_text(encoding='utf-8'))
parts = {node.targets[0].id: ast.literal_eval(node.value)
         for node in preview.body if isinstance(node, ast.Assign)
         and isinstance(node.targets[0], ast.Name) and node.targets[0].id in ('band', 'style')}
page = root / 'index.html'
text = page.read_text(encoding='utf-8')
text, count = re.subn(r'<div class="spec-band">.*?</div></div>\s*(?=<section id="equipment")',
                      parts['band'].replace('해<br>', '해 <br>').replace('살펴<br>', '살펴 <br>').replace('날짜로<br>', '날짜로 <br>'),
                      text, count=1, flags=re.S)
assert count == 1
text = text.replace('<small>고소작업 전문 업체</small>더 높은 곳은', '더 높은 곳은')
for tonne in (1, 2, 3, 5):
    text = text.replace(f'<strong>{tonne}<small>T</small></strong>', f'<strong>{tonne}<small>톤</small></strong>')
    text = text.replace(f'<h3>{tonne}톤 스카이차', f'<h3>{tonne}t 스카이차')
large = '''<article class="equipment-card equipment-large"><div class="large-equipment-heading"><p class="eyebrow">LARGE / SPECIAL EQUIPMENT</p><h3>5톤 초과 대형·특수 장비</h3><p>높은 작업 지점과 대형 현장도 상담하세요.</p></div><div class="large-equipment-details"><p>필요한 작업 높이와 거리, 탑승 인원·하중, 차량 진입로와 설치 공간을 알려주세요. 현장 조건에 맞는 장비 종류와 배차 가능 여부를 확인해 안내합니다.</p><a href="tel:01047400482">대형 장비 전화 상담 <span aria-hidden="true">↗</span></a></div></article>'''
text = text.replace('  </div><p class="equipment-note">표시 높이는', large + '\n  </div><p class="equipment-note">표시 높이는', 1)
text = text.replace('styles.css?v=content1', 'styles.css?v=equipment2')
page.write_text(text, encoding='utf-8')
css = root / 'styles.css'
style = parts['style'].removeprefix('<style>').removesuffix('</style>')
style += '''
.hero .hero-message em{font-size:clamp(30px,3vw,40px);font-weight:900;line-height:1.4;max-width:720px}
.equipment-large{grid-column:1/-1;display:grid;grid-template-columns:1fr 1.2fr;gap:32px;padding:30px;border-left:4px solid var(--orange);background:#fff}
.equipment-large .eyebrow{margin-bottom:12px}.equipment-large h3{font-size:27px;line-height:1.35;letter-spacing:-1px}
.large-equipment-heading>p:last-child,.large-equipment-details>p{font-size:14px;line-height:1.8;margin-top:12px;color:var(--muted)}
.large-equipment-details>a{display:flex;justify-content:space-between;align-items:center;border-top:1px solid #ddd;margin-top:20px;padding-top:16px;font-size:15px;font-weight:800}.large-equipment-details>a span{color:var(--orange);font-size:25px}
@media(max-width:760px){.hero .hero-message em{font-size:30px}.equipment-large{grid-template-columns:1fr;gap:10px;padding:24px}.equipment-large h3{font-size:24px}}
@media(max-width:480px){.hero .hero-message em{font-size:27px}}
'''
css.write_text(css.read_text(encoding='utf-8') + '\n' + style, encoding='utf-8')
helper = root / 'tools/update_page_content.py'
helper.write_text(helper.read_text(encoding='utf-8').replace('<small>고소작업 전문 업체</small>더 높은 곳은', '더 높은 곳은'), encoding='utf-8')
print('Applied service band, 4 tonne labels, large-equipment card and larger safety message.')
