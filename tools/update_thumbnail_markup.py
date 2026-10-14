"""Keep generator markup aligned with the approved 800x600 thumbnail design."""
from pathlib import Path

p=Path(__file__).resolve().parent/'build_regions.py'
s=p.read_text(encoding='utf-8')
s=s.replace('content="640"','content="800"').replace('content="360"','content="600"')
s=s.replace('width="640" height="360"','width="800" height="600"')
s=s.replace('region-thumbnails/{row[0]}.jpg" alt=', 'region-thumbnails/{row[0]}.jpg?v=shadow1" alt=')
s=s.replace('region-thumbnails/{r[0]}.jpg" alt=', 'region-thumbnails/{r[0]}.jpg?v=shadow1" alt=')
old='''<figure><img src="../{photo['file']}" alt="{escape(photo['title'])}" width="1600" height="1200" fetchpriority="high"><figcaption>'''
new='''<figure><a href="tel:01047400482" aria-label="{escape(full)} 장비 전화 상담 {PHONE}"><img class="regional-thumbnail" src="../assets/region-thumbnails/{code}.jpg?v=shadow1" alt="{escape(full)} 우리동네 스카이차 {PHONE}" width="800" height="600" fetchpriority="high"></a><figcaption>'''
if old not in s and new not in s:
    raise SystemExit('Unexpected hero markup; no files changed')
s=s.replace(old,new)
p.write_text(s,encoding='utf-8')
print('Updated generator: hero thumbnails, 4:3 dimensions and image cache version')
