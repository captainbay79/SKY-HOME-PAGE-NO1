"""Make an isolated service-band proposal for user review."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
page = (root / 'index.html').read_text(encoding='utf-8')
band = '''<section class="service-band" aria-label="장비 상담 안내"><div class="wrap">
<p class="service-kicker">현장에 맞는 상담부터 배차까지</p>
<h2>주소만 알려주세요.<br>장비와 일정을 함께 확인합니다.</h2>
<div class="service-benefits">
<article><span class="service-symbol" aria-hidden="true">↗</span><div><h3>빠른 배차 상담</h3><p>작업 위치와 차량 일정을 확인해<br>가능한 배차 시간을 안내합니다.</p></div></article>
<article><span class="service-symbol" aria-hidden="true">✓</span><div><h3>현장에 맞는 장비</h3><p>높이·거리·진입로를 함께 살펴<br>작업에 맞는 장비를 상담합니다.</p></div></article>
<article><span class="service-symbol" aria-hidden="true">☎</span><div><h3>간편한 예약 안내</h3><p>현장 주소와 희망 날짜로<br>견적과 예약 절차를 확인하세요.</p></div></article>
</div><a class="service-call" href="tel:01047400482"><span>장비 예약 친절 상담</span><strong>010-4740-0482 ↗</strong></a>
</div></section>'''
style = '''<style>
.service-band{background:#ff6417;color:#14191b;padding:40px 0 28px}
.service-kicker{font-size:13px;font-weight:900;letter-spacing:.06em;margin:0 0 12px}
.service-band h2{font-size:clamp(26px,3.3vw,40px);line-height:1.3;letter-spacing:-.05em;margin:0 0 25px}
.service-benefits{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
.service-benefits article{display:flex;gap:12px;border-top:1px solid #161a1b55;padding-top:20px}
.service-symbol{display:flex;align-items:center;justify-content:center;flex-shrink:0;width:38px;height:38px;background:#171a1b;color:#ff6417;border-radius:50%;font-size:25px;font-weight:900}
.service-benefits h3{font-size:19px;margin:0 0 8px;font-weight:900;letter-spacing:-.04em}
.service-benefits p{font-size:14px;line-height:1.6;margin:0;color:#222}
.service-call{display:flex;justify-content:space-between;align-items:center;border-top:1px solid #161a1b55;margin-top:25px;padding-top:19px;font-weight:800;font-size:15px}
.service-call strong{font-size:23px}
@media(max-width:760px){.service-benefits{grid-template-columns:1fr;gap:14px}.service-benefits article{padding-top:14px}.service-benefits p br{display:none}.service-band{padding:28px 0 22px}.service-band h2{font-size:29px}.service-benefits h3{font-size:20px}.service-call{flex-wrap:wrap;gap:10px}.service-call strong{font-size:22px}}
</style>'''
page = page.replace('<head>', '<head><base href="../">', 1)
page = page.replace('</head>', style + '</head>', 1)
page = re.sub(r'<section class="hero">.*?</section>', '', page, count=1, flags=re.S)
page, count = re.subn(r'<div class="spec-band">.*?</div></div>\s*(?=<section id="equipment")', band, page, count=1, flags=re.S)
assert count == 1
page = re.sub(r'<div class="utility">.*?</div></div>', '', page, count=1, flags=re.S)
out = root / '.preview/service-band-concept.html'
out.write_text(page, encoding='utf-8')
print('Created isolated proposal:', out)
