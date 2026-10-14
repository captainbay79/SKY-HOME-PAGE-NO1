"""Update existing directory and province navigation without rebuilding photos."""
import json
import re
from html import escape
from pathlib import Path
from region_order import PROVINCE_ORDER, province_sort_key

root = Path(__file__).resolve().parents[1]
rows = json.loads((root / 'assets/regions.json').read_text(encoding='utf-8'))
provinces = sorted((row for row in rows if not row[2]), key=province_sort_key)
assert [row[0] for row in provinces] == PROVINCE_ORDER
directory = root / 'regions/index.html'
text = directory.read_text(encoding='utf-8')
pattern = r'(<div class="region-thumbnails">)(.*?)(</div>)'
match = re.search(pattern, text, re.S)
assert match
cards = re.findall(r'<a class="region-thumbnail".*?</a>', match[2], re.S)
assert len(cards) == len(provinces)
cards_by_code = {re.search(r'href="(\d+)\.html"', card)[1]: card for card in cards}
replacement = match[1] + ''.join(cards_by_code[row[0]] for row in provinces) + match[3]
text = text[:match.start()] + replacement + text[match.end():]
directory.write_text(text, encoding='utf-8')
for row in provinces:
    page = root / 'regions' / f'{row[0]}.html'
    text = page.read_text(encoding='utf-8')
    links = ''.join(f'<a href="{other[0]}.html">{escape(other[1])}<span aria-hidden="true">↗</span></a>'
                    for other in [other for other in provinces if other[0] != row[0]][:12])
    text, count = re.subn(r'(<h2>같은 상위 지역의 안내 페이지</h2><div class="regional-links">).*?(</div>)',
                          lambda match: match[1] + links + match[2], text, flags=re.S)
    assert count == 1, page
    page.write_text(text, encoding='utf-8')
print('Updated nationwide directory and 16 province navigation lists: 서울 → 경기 → 인천 first.')
