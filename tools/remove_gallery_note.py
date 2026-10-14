"""Remove the owner-selected gallery note from live pages and gallery templates."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
note = '<p class="equipment-note">직접 제공해 주신 실제 현장 사진입니다. 촬영 지역이 확인되지 않아 특정 지역의 작업 사례로 표시하지 않습니다.</p>'
pages = [ROOT/'index.html'] + list((ROOT/'regions').glob('*.html'))
changed = 0
for page in pages:
    text = page.read_text(encoding='utf-8')
    if note in text:
        text = text.replace(note, '')
        page.write_text(text, encoding='utf-8')
        changed += 1
    assert note not in text
for filename in ['regional_gallery.py','preview_regional_refinements.py']:
    template = ROOT/'tools'/filename
    template.write_text(template.read_text(encoding='utf-8').replace(note,''), encoding='utf-8')
print(f'Removed gallery note from {changed} pages; verified all {len(pages)} pages and updated templates.', flush=True)
