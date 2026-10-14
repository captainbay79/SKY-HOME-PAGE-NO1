"""Build local region pages, photographic thumbnails and optional production SEO URLs.

Run from the repository root. Originals are read-only. Pillow is required.
"""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
from html import escape
from collections import defaultdict
from urllib.parse import urlsplit
import argparse
import hashlib
import json
from thumbnail_design import make_thumbnail
from thumbnail_photos import prepare as prepare_thumbnail_photos, assign as assign_thumbnail_photos
from site_watermarks import apply_site_watermarks
from faq_content import regional_faq
from region_order import province_sort_key
from regional_main_design import apply_main_design
from business_footer import apply_business_footer

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(r'C:\Users\Over kim\Documents\홈페이지 제작용 이미지\광고기획 작업사진')
FONT = Path(r'C:\Windows\Fonts\malgunbd.ttf')
PHONE = '010-4740-0482'
BRAND = '키다리스카이차'

def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def prepare_photos():
    # Visually reviewed photos; descriptions only state what is visible.
    selected = [
        ('advertising-work-1686680868703.jpg', '주택 외벽 앞에 펼친 스카이차 붐대'),
        ('advertising-work-20221026-111929.jpg', '수목 옆 도로에 배치된 스카이차'),
        ('advertising-work-20230110-144152.jpg', '구조물 아래에 배치된 스카이차'),
        ('advertising-work-20230806-081952.jpg', '건물 외벽과 작업대 배치'),
        ('advertising-work-20231228-081419.jpg', '실내 공간에 배치된 스카이차'),
        ('advertising-work-20260314-080750.jpg', '상가 앞 도로변 고소작업 현장'),
        ('advertising-work-20260328-083024.jpg', '조명이 켜진 실내의 작업대'),
        ('advertising-work-20260405-101914.jpg', '건물 옆 장비와 지지대 설치'),
        ('advertising-work-20260605-102629.jpg', '유리 외벽 앞에 펼친 스카이차'),
        ('advertising-work-20260630-085036.jpg', '건물 앞 공간에 배치된 스카이차'),
        ('advertising-work-20260707-145716.jpg', '수목과 건물 사이의 장비 배치'),
        ('advertising-work-20261006-095838.jpg', '벽돌 건물 앞에 펼친 스카이차'),
    ]
    catalog = []
    destination = ROOT / 'assets' / 'regional-photos'
    destination.mkdir(exist_ok=True)
    for i,(filename,alt) in enumerate(selected):
        original = SOURCE / filename
        if not original.exists():
            raise FileNotFoundError(original)
        path = destination / f'field-{i+1:02d}.jpg'
        with Image.open(original) as raw:
            im = ImageOps.exif_transpose(raw).convert('RGB')
            im.thumbnail((1600,1200))
            im.save(path, quality=82, optimize=True)
        catalog.append({'file':path.relative_to(ROOT).as_posix(), 'original_filename':filename,
                        'source':'user_provided_folder', 'title':alt, 'region':None,
                        'equipment_class':None, 'sha256':hashlib.sha256(original.read_bytes()).hexdigest(),
                        'processing':'EXIF orientation, web resize, JPEG compression; original untouched'})
    dump(ROOT / 'assets' / 'regional-photo-catalog.json', catalog)
    return catalog

def header(prefix):
    return f'''<a class="skip" href="#main">본문 바로가기</a>
<div class="utility"><div class="wrap"><span>전국 스카이차 · 고소작업차 임대 상담</span><span>현장에 맞는 장비, 전화로 확인하세요 ↗</span></div></div>
<header><div class="wrap header-inner"><a class="brand" href="{prefix}index.html" aria-label="키다리스카이차 홈"><span class="brand-icon" aria-hidden="true">K<span>↗</span></span><span>키다리<span class="brand-orange">스카이차</span><small>KIDARI SKY EQUIPMENT</small></span></a><button class="menu-toggle" aria-controls="navigation" aria-expanded="false" aria-label="메뉴 열기">☰</button><nav id="navigation" aria-label="주요 메뉴"><a href="{prefix}index.html#equipment">장비 안내</a><a href="{prefix}index.html#services">작업 분야</a><a href="{prefix}index.html#field">현장 사진</a><a href="{prefix}regions/index.html">전국 지역</a></nav><a class="header-call" href="tel:01047400482">전화 상담 <strong>{PHONE} ↗</strong></a></div></header>'''

def footer(prefix):
    return f'''<section id="contact" class="contact"><div class="wrap"><div><p class="eyebrow">LET’S GET TO WORK</p><h2>현장 주소부터,<br>함께 확인하겠습니다.</h2><p>장비 · 견적 · 일정 전화 상담</p></div><a href="tel:01047400482"><small>{BRAND}</small><strong>{PHONE}</strong><span>지금 전화하기 ↗</span></a></div></section>
<footer><div class="wrap"><div><a class="brand" href="{prefix}index.html">키다리<span class="brand-orange">스카이차</span></a><p>전국 스카이차 · 고소작업차 임대 상담</p></div><div><a href="tel:01047400482">{PHONE}</a><p>카드결제 사전 요청 · VAT 별도</p></div></div><div class="wrap footer-bottom"><span>© 2026 {BRAND}</span><a href="{prefix}regions/index.html">전국 지역 안내 ↗</a></div></footer><a class="mobile-call" href="tel:01047400482"><span>장비 예약 친절 상담</span><strong>{PHONE} ↗</strong></a>'''

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', default='', help='Confirmed production HTTPS origin; omit for localhost work')
    args = parser.parse_args()
    base = args.base_url.rstrip('/')
    if base:
        parsed = urlsplit(base)
        if parsed.scheme != 'https' or not parsed.netloc or parsed.hostname in ('localhost','127.0.0.1') or parsed.query or parsed.fragment or parsed.path:
            raise ValueError('Use the confirmed production HTTPS origin, without path or query')
    rows = json.loads((ROOT/'assets/regions.json').read_text(encoding='utf-8'))
    by_id = {r[0]:r for r in rows}
    if len(by_id) != len(rows): raise ValueError('Duplicate region IDs')
    children = defaultdict(list)
    for row in rows: children[row[2]].append(row)
    def ancestors(row):
        result=[row]
        while result[0][2]: result.insert(0,by_id[result[0][2]])
        return result
    provinces = sorted(children[None], key=province_sort_key)
    photos = prepare_photos()
    thumbnail_photos = prepare_thumbnail_photos()
    photo_assignments = assign_thumbnail_photos(children, thumbnail_photos)
    pages = ROOT/'regions'
    thumbs = ROOT/'assets/region-thumbnails'
    pages.mkdir(exist_ok=True); thumbs.mkdir(exist_ok=True)
    manifest=[]; sitemap=['/','/regions/index.html']
    def meta(title,description,path,image,indexable):
        urlmeta = f'<link rel="canonical" href="{base}{path}"><meta property="og:url" content="{base}{path}">' if base else ''
        imgurl = base+image if base else '..'+image
        return f'''<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title><meta name="description" content="{escape(description,quote=True)}"><meta name="robots" content="{'index,follow,max-image-preview:large' if indexable else 'noindex,follow'}"><meta name="theme-color" content="#171a1b"><meta property="og:type" content="website"><meta property="og:locale" content="ko_KR"><meta property="og:site_name" content="{BRAND}"><meta property="og:title" content="{escape(title,quote=True)}"><meta property="og:description" content="{escape(description,quote=True)}"><meta property="og:image" content="{imgurl}"><meta property="og:image:width" content="800"><meta property="og:image:height" content="600"><meta name="twitter:card" content="summary_large_image">{urlmeta}<link rel="icon" href="../assets/favicon.svg"><link rel="stylesheet" href="../styles.css"><link rel="stylesheet" href="../region.css"><script src="../region.js" defer></script>'''
    def link(row,thumbnail=False):
        img=f'<img src="../assets/region-thumbnails/{row[0]}.jpg?v=approved-final3" alt="{escape(row[3])} 장비 상담 안내 썸네일" width="800" height="600" loading="lazy">' if thumbnail else ''
        return f'<a href="{row[0]}.html">{img}{escape(row[1])}<span aria-hidden="true">↗</span></a>'
    for i,row in enumerate(rows):
        code,name,parent,full=row
        chain=ancestors(row)
        photo_index=int(hashlib.sha256(code.encode()).hexdigest()[:8],16)%len(photos)
        photo=photos[photo_index]
        thumbnail=thumbs/f'{code}.jpg'
        make_thumbnail(row,photo_assignments[code],thumbnail)
        own_children=children[code]
        indexable=bool(own_children)
        title=f'{full} 스카이차·고소작업차 임대 상담 | {BRAND}'
        description=f'{full} 현장의 스카이차·고소작업차 상담 안내. 현장 주소, 작업 높이, 진입로와 희망 일정으로 장비·견적을 확인하세요. 전화 {PHONE}.'
        breadcrumb=[('홈','../index.html'),('전국 지역','index.html')]+[(r[1],r[0]+'.html') for r in chain]
        crumbs=' <span aria-hidden="true">/</span> '.join(f'<a href="{href}">{escape(label)}</a>' if j<len(breadcrumb)-1 else f'<span aria-current="page">{escape(label)}</span>' for j,(label,href) in enumerate(breadcrumb))
        summary=f'{BRAND}는 {full} 현장의 스카이차·고소작업차 임대 상담을 받습니다. 작업 높이와 차량 설치 공간, 희망 일정을 확인한 뒤 적합한 장비와 배차 가능 여부를 안내합니다.'
        faq=regional_faq(row,own_children)
        provider={'@type':'Organization','name':BRAND,'telephone':'+82-10-4740-0482'}
        schema={'@context':'https://schema.org','@graph':[
            {'@type':'WebPage','name':title,'description':description,'inLanguage':'ko-KR','about':{'@type':'AdministrativeArea','name':full}},
            {'@type':'Service','name':f'{full} 스카이차 임대 상담','serviceType':'스카이차·고소작업차 임대 상담','description':summary,'provider':provider,'areaServed':{'@type':'AdministrativeArea','name':full}},
            {'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':j+1,'name':label,'item':base+('/' if href=='../index.html' else '/regions/'+href)} for j,(label,href) in enumerate(breadcrumb)]}
        ]}
        # Absolute structured-data URLs are only emitted for a confirmed production origin.
        if base:
            schema['@graph'][0]['url']=base+f'/regions/{code}.html'
            schema['@graph'][0]['primaryImageOfPage']={'@type':'ImageObject','contentUrl':base+f'/assets/region-thumbnails/{code}.jpg'}
            provider['url']=base+'/'
        else:
            for item in schema['@graph'][2]['itemListElement']: item.pop('item')
        nearby=children[parent] if parent else provinces
        neighborhood=[r for r in nearby if r[0]!=code]
        related=''.join(link(r) for r in neighborhood[:12])
        child_section=f'<section class="section light"><div class="wrap"><p class="eyebrow">AREA DIRECTORY</p><h2>{escape(name)} 세부 지역 안내</h2><p class="equipment-note">{len(own_children):,}개 하위 지역에서 작업 위치를 찾아보세요. 법정동 자료 기준으로 행정동 명칭과 다를 수 있습니다.</p><div class="regional-links">'+''.join(link(r, len(own_children)<=30) for r in own_children)+'</div></div></section>' if own_children else f'<section class="section light"><div class="wrap"><p class="eyebrow">SITE ADDRESS</p><h2>{escape(name)} 현장 주소 확인</h2><div class="answer-box">{escape(full)} 안에서도 같은 이름의 건물이나 서로 다른 진입로가 있을 수 있습니다. 도로명 주소와 건물명, 차량이 들어갈 입구를 함께 알려주세요.</div><a class="region-back" href="{parent}.html">{escape(by_id[parent][1])} 전체 지역 보기 ↗</a></div></section>'
        gallery=''.join(f'<figure><img src="../{p["file"]}" alt="{escape(p["title"])}" width="1600" height="1200" loading="lazy"><figcaption>{escape(p["title"])}</figcaption></figure>' for p in [photo,photos[(photo_index+3)%len(photos)],photos[(photo_index+7)%len(photos)]])
        html=f'''<!doctype html><html lang="ko"><head>{meta(title,description,f'/regions/{code}.html',f'/assets/region-thumbnails/{code}.jpg',indexable)}<script type="application/ld+json">{json.dumps(schema,ensure_ascii=False).replace('</','<\\/')}</script></head><body>{header('../')}<main id="main"><div class="wrap"><nav class="breadcrumb" aria-label="현재 위치">{crumbs}</nav></div>
<section class="regional-hero"><div class="wrap"><div><p class="eyebrow">REGIONAL EQUIPMENT / {code}</p><h1>{escape(full)}<span>스카이차 임대 상담</span></h1><p class="summary">{escape(summary)}</p><a class="button orange" href="tel:01047400482">{PHONE} 전화 상담 <span>↗</span></a><a class="region-back" href="../index.html#equipment">장비 제원 살펴보기 ↓</a><div class="hero-tags"><span>당일배차 · 빠른배차 가능</span><span>1톤부터 대형 장비까지</span><span>카드결제 가능</span></div></div><figure><a href="tel:01047400482" aria-label="{escape(full)} 장비 전화 상담 {PHONE}"><img class="regional-thumbnail" src="../assets/region-thumbnails/{code}.jpg?v=approved-final3" alt="{escape(full)} 우리동네 스카이차 {PHONE}" width="800" height="600" fetchpriority="high"></a></figure></div></section>
<section class="section light"><div class="wrap"><p class="eyebrow">QUICK ANSWER</p><h2>{escape(name)} 장비 상담,<br>먼저 확인할 내용</h2><dl class="regional-facts"><div><dt>상담 지역</dt><dd>{escape(full)}</dd></div><div><dt>문의 장비</dt><dd>1톤 · 2톤 · 3톤 · 5톤<br>대형·특수 장비 상담</dd></div><div><dt>예약·견적</dt><dd>현장과 일정 확인 후 안내</dd></div><div><dt>전화번호</dt><dd><a href="tel:01047400482">{PHONE}</a></dd></div></dl><div class="regional-checklist"><article><h3>01. 현장 주소</h3><p>{escape(full)} 내 상세 주소와 건물명, 진입로 폭, 차량과 지지대를 설치할 공간을 확인해 주세요.</p></article><article><h3>02. 작업 조건</h3><p>간판·외벽·유리·설비 등 작업 종류, 필요한 높이와 수평 거리, 탑승 인원과 자재 정보를 알려주세요.</p></article><article><h3>03. 날짜와 시간</h3><p>희망 날짜와 예상 작업 시간을 알려주세요. 주말·야간과 당일 일정은 차량 및 현장 여건을 확인합니다.</p></article></div><p class="equipment-note">작업 인력·자재·공사 수행 범위는 별도로 상담합니다. 카드결제는 예약 전에 말씀해 주세요. VAT 별도.</p></div></section>
<section class="section light"><div class="wrap"><div class="section-heading"><div><p class="eyebrow">REAL FIELD PHOTOGRAPHS</p><h2>장비 배치,<br>사진으로 참고하세요.</h2></div><p>직접 제공된 실제 현장 사진입니다.<br>특정 지역·장비 톤수의 실적으로 분류하지 않았습니다.</p></div><div class="regional-gallery">{gallery}</div></div></section>
{child_section}<section class="section light"><div class="wrap regional-faq"><p class="eyebrow">QUESTIONS & ANSWERS</p><h2>{escape(name)} 스카이차 상담 FAQ</h2>{''.join(f'<details><summary>{escape(q)}</summary><p>{escape(a)}</p></details>' for q,a in faq)}</div></section>
<section class="section light"><div class="wrap"><h2>같은 상위 지역의 안내 페이지</h2><div class="regional-links">{related}</div><a class="region-back" href="index.html">전국 지역 다시 찾기 ↗</a></div></section></main>{footer('../')}</body></html>'''
        (pages/f'{code}.html').write_text(apply_business_footer(apply_main_design(html,row)),encoding='utf-8')
        manifest.append({'code':code,'name':full,'page':f'regions/{code}.html','thumbnail':f'assets/region-thumbnails/{code}.jpg','photo':photo['file'],'thumbnail_photo':photo_assignments[code]['file'],'indexable':indexable})
        if indexable: sitemap.append(f'/regions/{code}.html')
        if (i+1)%1000==0: print(f'{i+1}/{len(rows)} pages and thumbnails',flush=True)
    cards=''.join(f'<a class="region-thumbnail" href="{r[0]}.html"><img src="../assets/region-thumbnails/{r[0]}.jpg?v=approved-final3" alt="{escape(r[1])} 스카이차 상담 안내" width="800" height="600" loading="lazy"><strong>{escape(r[1])}<span>↗</span></strong></a>' for r in provinces)
    directory=f'''<!doctype html><html lang="ko"><head>{meta('전국 지역별 스카이차 상담 안내 | '+BRAND,'시·도에서 시·군·구, 읍·면·동까지 작업 지역을 찾아 장비 상담 준비 내용을 확인하세요. '+PHONE,'/regions/index.html','/assets/region-thumbnails/'+provinces[0][0]+'.jpg',True)}</head><body>{header('../')}<main id="main"><section class="section light region-directory"><div class="wrap"><nav class="breadcrumb" aria-label="현재 위치"><a href="../index.html">홈</a><span>/</span><span aria-current="page">전국 지역</span></nav><p class="eyebrow">NATIONWIDE / REGION DIRECTORY</p><h1>전국 방방곡곡,<br>현장 지역부터 찾아보세요.</h1><p class="equipment-note">{len(rows):,}개 지역 안내 · 실제 배차 가능 여부는 주소와 일정 확인 후 상담합니다.</p><a class="region-back" href="../index.html#regions">지역 이름으로 검색하기 ↗</a><div class="region-thumbnails">{cards}</div><p class="equipment-note">썸네일의 작업 사진은 장비 배치 참고용입니다. 촬영 지역이 확인되지 않아 지역별 시공 사례로 사용하지 않습니다. 지역명은 저장소의 기존 법정동 자료 기준입니다.</p></div></section></main>{footer('../')}</body></html>'''
    (pages/'index.html').write_text(apply_business_footer(directory),encoding='utf-8')
    dump(ROOT/'assets/region-pages.json',manifest)
    robots='User-agent: *\nAllow: /\nDisallow: /.git/\nDisallow: /.preview/\nDisallow: /tools/\n'
    if base:
        from xml.sax.saxutils import escape as xml_escape
        sitemap_xml='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{xml_escape(base+p)}</loc></url>' for p in sitemap)+'</urlset>'
        (ROOT/'sitemap.xml').write_text(sitemap_xml,encoding='utf-8')
        robots+=f'Sitemap: {base}/sitemap.xml\n'
    (ROOT/'robots.txt').write_text(robots,encoding='utf-8')
    dump(ROOT/'assets/region-build.json',{'page_count':len(rows),'thumbnail_count':len(rows),'indexable_pages':sum(r['indexable'] for r in manifest),'base_url':base or None,'photo_count':len(photos),'thumbnail_photo_count':len(thumbnail_photos),'thumbnail_design':'approved-heavier-region-all-text-black-outline-shadow','thumbnail_size':[800,600]})
    apply_site_watermarks()
    print(f'Built {len(rows)} pages and JPG thumbnails; {sum(r["indexable"] for r in manifest)} regional directory pages indexable; production origin: {base or "not configured"}',flush=True)

if __name__ == '__main__': main()
