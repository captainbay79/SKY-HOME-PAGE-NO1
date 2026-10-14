from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
p = root/'index.html'
s = p.read_text(encoding='utf-8')
if 'class="region-directory-link"' not in s:
    s = s.replace('<div class="region-count">', '<a class="region-directory-link" href="regions/index.html">지역별 사진과 상담 안내 보기 ↗</a><div class="region-count">')
schema={'@context':'https://schema.org','@type':'Organization','name':'키다리스카이차','telephone':'+82-10-4740-0482','description':'전국 스카이차·고소작업차 임대 상담'}
if 'application/ld+json' not in s:
    s=s.replace('</head>', '<meta name="robots" content="index,follow,max-image-preview:large"><script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False)+'</script></head>')
p.write_text(s,encoding='utf-8')
print('Main page region links and organization data updated')
