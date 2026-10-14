"""Apply the approved consultation band without changing local content or photos."""
from pathlib import Path
import ast
import re

ROOT = Path(__file__).resolve().parents[1]
LINK = '<a class="service-equipment-link" href="#equipment"><span>장비 먼저 살펴보기</span><span class="equipment-down-arrow" aria-hidden="true">↓</span></a>'

def apply():
    preview = ast.parse((ROOT / 'tools/preview_equipment_link.py').read_text(encoding='utf-8'))
    style = next(ast.literal_eval(node.value) for node in preview.body
                 if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'style' for t in node.targets))
    css_path = ROOT / 'styles.css'
    css = css_path.read_text(encoding='utf-8')
    marker = '/* Approved consultation band: soft background and equipment navigation */'
    if marker not in css:
        css_path.write_text(css + '\n' + marker + '\n' + style.removeprefix('<style>').removesuffix('</style>') + '\n', encoding='utf-8')
    pages = [ROOT / 'index.html', *sorted((ROOT / 'regions').glob('*.html'))]
    count = 0
    for page in pages:
        original = page.read_text(encoding='utf-8')
        if 'class="service-band"' not in original:
            continue
        updated = re.sub(r'<a class="hero-secondary hero-equipment-link"[^>]*>.*?</a>', '', original, flags=re.S)
        updated = re.sub(r'<a class="service-call"[^>]*>.*?</a>', LINK, updated, flags=re.S)
        updated = re.sub(r'(href="(?:\.\./)?styles\.css)(?:\?[^"<>]*)?"', r'\1?v=service-soft5"', updated)
        assert 'hero-equipment-link' not in updated
        assert 'class="service-call"' not in updated
        assert updated.count('class="service-equipment-link"') == 1
        assert re.findall(r'<img[^>]*>', original) == re.findall(r'<img[^>]*>', updated)
        assert original.count('<summary>') == updated.count('<summary>')
        if updated != original:
            page.write_text(updated, encoding='utf-8')
        count += 1
    assert count == 5352, count
    print(f'Applied approved band to {count} pages; photos and FAQ unchanged.', flush=True)

if __name__ == '__main__':
    apply()
