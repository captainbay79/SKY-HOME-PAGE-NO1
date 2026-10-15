"""Share the main-page content while retaining local navigation, FAQ and thumbnails."""
import re
from html import escape
from pathlib import Path
from regional_gallery import gallery_section
from hero_elements import HERO_TAGS, HERO_ACTIONS

ROOT = Path(__file__).resolve().parents[1]

def section(source, identifier):
    match = re.search(r'<section id="' + identifier + r'".*?</section>', source, re.S)
    assert match, identifier
    return match[0]

def adapt_assets(text):
    return text.replace('src="assets/', 'src="../assets/').replace('href="regions/', 'href="')

def apply_main_design(html, row):
    main = (ROOT / 'index.html').read_text(encoding='utf-8')
    full = escape(row[3])
    old_hero = re.search(r'<section class="regional-hero">.*?</section>', html, re.S)
    assert old_hero
    thumbnail = re.search(r'<figure>.*?</figure>', old_hero[0], re.S)[0]
    summary = re.search(r'<p class="summary">.*?</p>', old_hero[0], re.S)[0]
    heading = re.search(r'<h1 class="hero-message">.*?</h1>', main, re.S)[0]
    heading = heading.replace('>더 높은 곳은', f'><small>{full} 스카이차</small>더 높은 곳은', 1)
    introduction = re.search(r'<p class="hero-description hero-introduction">.*?</p>', main, re.S)[0]
    actions = HERO_ACTIONS
    tags = HERO_TAGS
    hero = f'<section class="regional-hero hero regional-main-hero"><div class="wrap"><div>{heading}{introduction}{summary}{actions}{tags}</div>{thumbnail}</div></section>'
    html = html[:old_hero.start()] + hero + html[old_hero.end():]
    band = re.search(r'<section class="service-band".*?</section>', main, re.S)[0]
    common = band + section(main, 'equipment') + section(main, 'services')
    html, count = re.subn(r'<section class="section light"><div class="wrap"><p class="eyebrow">QUICK ANSWER</p>.*?</section>', common, html, count=1, flags=re.S)
    assert count == 1
    html, count = re.subn(r'<section class="section light"><div class="wrap"><div class="section-heading"><div><p class="eyebrow">REAL FIELD PHOTOGRAPHS</p>.*?</section>', gallery_section(row[0]), html, count=1, flags=re.S)
    assert count == 1
    booking = re.search(r'<section class="section light"><div class="wrap"><div class="section-heading"><div><p class="eyebrow">05 / HOW TO BOOK</p>.*?</section>', main, re.S)[0]
    booking = re.sub(r'<div class="faq">.*?</div></div></section>', '</div></section>', booking, flags=re.S)
    booking = booking.replace('작업 지역과 진입로 폭,', full + '의 상세 주소와 진입로 폭,')
    html = html.replace('<section class="section light"><div class="wrap regional-faq">', booking + '<section class="section light"><div class="wrap regional-faq">', 1)
    html = re.sub(r'<section id="contact".*?</section>', section(main, 'contact').replace('키다리스카이차 · 전국 스카이차 임대 상담', f'키다리스카이차 · {full} 스카이차 상담'), html, count=1, flags=re.S)
    dialog = re.search(r'<dialog id="equipment-dialog">.*?</dialog>', main, re.S)[0]
    html = html.replace('</body>', dialog + '</body>', 1)
    html = html.replace('href="../styles.css"', 'href="../styles.css?v=regional-main3"')
    html = html.replace('href="../region.css"', 'href="../region.css?v=regional-main3"')
    html = html.replace('<script src="../region.js" defer></script>', '<script src="../region.js" defer></script><script src="../equipment.js?v=regional-main3" defer></script>')
    html = html.replace('?v=regional-main3', '?v=regional-refinement4')
    return html.replace('styles.css?v=regional-refinement4', 'styles.css?v=hero-proof6')

def update_existing():
    import json
    rows = json.loads((ROOT / 'assets/regions.json').read_text(encoding='utf-8'))
    for i, row in enumerate(rows):
        page = ROOT / 'regions' / f'{row[0]}.html'
        original = page.read_text(encoding='utf-8')
        thumbnail_before = re.search(r'<img class="regional-thumbnail"[^>]+>', original)[0]
        updated = apply_main_design(original, row)
        assert thumbnail_before == re.search(r'<img class="regional-thumbnail"[^>]+>', updated)[0]
        assert updated.count('<dialog id="equipment-dialog">') == 1
        assert len(re.findall(r'<figure>', section(updated, 'field'))) == 8
        assert updated.count('<summary>') == 5
        page.write_text(updated, encoding='utf-8')
        if (i+1) % 1000 == 0: print(f'{i+1}/{len(rows)} updated and verified', flush=True)
    print(f'Updated {len(rows)} pages; retained every thumbnail, regional FAQ and directory.', flush=True)

if __name__ == '__main__':
    update_existing()
