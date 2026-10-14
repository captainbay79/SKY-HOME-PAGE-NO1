"""Package public website files for the approved new Cloudflare Worker only."""
from pathlib import Path
import json
import re
import shutil

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist'
ORIGIN='https://sky-home-page-no1.captainbay79.workers.dev'
OUT.mkdir(exist_ok=True)
files=['index.html','styles.css','script.js','equipment.js','region.css','region.js','robots.txt','_redirects','assets/regions.json','assets/favicon.svg']
files += [page.relative_to(ROOT).as_posix() for page in (ROOT/'regions').glob('*.html')]
files += [image.relative_to(ROOT).as_posix() for image in (ROOT/'assets/region-thumbnails').glob('*.jpg')]
files += [image.relative_to(ROOT).as_posix() for image in (ROOT/'assets/watermarked').rglob('*.jpg')]
# Prune obsolete build artifacts only inside this verified repository build directory.
expected=set(files)|{'sitemap.xml'}
for existing in OUT.rglob('*'):
    if existing.is_file() and existing.relative_to(OUT).as_posix() not in expected:
        existing.unlink()
sitemap=['/','/regions/index.html']
for relative in files:
    source=ROOT/relative
    destination=OUT/relative
    destination.parent.mkdir(parents=True,exist_ok=True)
    if source.suffix=='.html':
        text=source.read_text(encoding='utf-8')
        path='/'+relative if relative!='index.html' else '/'
        text=re.sub(r'<link rel="canonical"[^>]*>|<meta property="og:url"[^>]*>','',text)
        text=text.replace('</head>',f'<link rel="canonical" href="{ORIGIN}{path}"><meta property="og:url" content="{ORIGIN}{path}"></head>',1)
        text=re.sub(r'(<meta property="og:image" content=")(?:\.\./|/)?assets/',r'\1'+ORIGIN+'/assets/',text)
        if relative.startswith('regions/') and relative!='regions/index.html' and 'content="index,follow' in text:
            sitemap.append(path)
        destination.write_text(text,encoding='utf-8')
    elif relative=='robots.txt':
        text=source.read_text(encoding='utf-8')
        text=re.sub(r'Sitemap:.*\n?','',text)
        destination.write_text(text+f'\nSitemap: {ORIGIN}/sitemap.xml\n',encoding='utf-8')
    elif not destination.exists() or source.stat().st_mtime>destination.stat().st_mtime:
        shutil.copy2(source,destination)
from xml.sax.saxutils import escape
(OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{escape(ORIGIN+path)}</loc></url>' for path in sitemap)+'</urlset>',encoding='utf-8')
print(json.dumps({'public_files':len(files)+1,'regional_pages':len(list((OUT/'regions').glob('[0-9]*.html'))),'indexed_urls':len(sitemap),'target':'sky-home-page-no1','origin':ORIGIN},ensure_ascii=False),flush=True)
