"""Keep all eight main-page work photos in one continuous gallery."""
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parents[1]
page = ROOT / 'index.html'
text = page.read_text(encoding='utf-8')
split = '</div><h3 class="extra-field-heading">추가 작업 사진</h3><div class="field-grid">'
assert split in text
text = text.replace(split, '', 1)
field = re.search(r'<section id="field".*?</section>', text, re.S)[0]
assert field.count('class="field-grid"') == 1
assert field.count('<figure>') == 8
assert 'extra-field-heading' not in field
page.write_text(text, encoding='utf-8')
print('Removed extra heading; verified 8 photos in one main-page gallery.')
