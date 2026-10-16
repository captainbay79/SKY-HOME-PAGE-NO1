"""Consolidate identical region names while preserving the approved full layout."""
from pathlib import Path
from collections import defaultdict
from html import escape
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
PHONE = '010-4740-0482'
BRAND = '키다리스카이차'

def load_groups():
    rows = json.loads((ROOT/'assets/regions.json').read_text(encoding='utf-8'))
    manifest = json.loads((ROOT/'assets/region-pages.json').read_text(encoding='utf-8'))
    pages = {p['code']:p for p in manifest}
    groups = defaultdict(list)
    for row in rows:
        groups[row[1]].append(row)
    return rows, manifest, pages, groups

def common_page(source, name, code, indexable):
    label = escape(name)
    title = f'{name} 스카이차 임대·배차 상담 | {BRAND}'
    description = f'{name} 스카이차 상담. 현장 주소와 작업 내용을 알려주시면 작업 높이와 설치 공간을 확인해 장비와 배차 가능 일정을 안내합니다. 전화 {PHONE}.'
    summary = f'{BRAND}는 {name} 현장의 스카이차 임대·배차 상담을 받습니다. 정확한 현장 주소와 작업 내용을 알려주세요. 작업 높이와 차량 설치 공간, 희망 일정을 확인한 뒤 장비와 배차 가능 여부를 안내합니다.'
    source = re.sub(r'<title>.*?</title>', '<title>'+escape(title)+'</title>', source, count=1, flags=re.S)
    for key, value in [('name="description"', description), ('property="og:title"', title), ('property="og:description"', description)]:
        source = re.sub(r'<meta '+key+r'[^>]*>', '<meta '+key+' content="'+escape(value,quote=True)+'">', source, count=1)
    source = re.sub(r'<meta name="robots"[^>]*>', '<meta name="robots" content="'+('index,follow,max-image-preview:large' if indexable else 'noindex,follow')+'">', source, count=1)
    source = re.sub(r'<meta property="og:image"[^>]*>', f'<meta property="og:image" content="../assets/region-thumbnails/{code}.jpg?v=square-approved1">', source, count=1)
    source = re.sub(r'<link rel="canonical"[^>]*>|<meta property="og:url"[^>]*>', '', source)
    source = source.replace('</head>', f'<link rel="canonical" href="{code}.html"></head>', 1)
    source = re.sub(r'<nav class="breadcrumb".*?</nav>', f'<nav class="breadcrumb" aria-label="현재 위치"><a href="../index.html">홈</a><span>/</span><a href="index.html">전국 지역</a><span>/</span><span aria-current="page">{label}</span></nav>', source, count=1, flags=re.S)
    source = re.sub(r'(<h1 class="hero-message"><small>).*?(</small>)', r'\g<1>'+label+r' 스카이차\2', source, count=1, flags=re.S)
    source = re.sub(r'<p class="summary">.*?</p>', '<p class="summary">'+escape(summary)+'</p>', source, count=1, flags=re.S)
    source = re.sub(r'<figure><a href="tel:01047400482".*?</figure>', f'<figure><a href="tel:01047400482" aria-label="{label} 장비 전화 상담 {PHONE}"><img class="regional-thumbnail" src="../assets/region-thumbnails/{code}.jpg?v=square-approved1" alt="{label} 우리동네 스카이차 {PHONE}" width="1200" height="1200" fetchpriority="high"></a></figure>', source, count=1, flags=re.S)
    # A shared name has no single parent or local subdivision directory.
    address = f'<section class="section light shared-address"><div class="wrap"><p class="eyebrow">SITE ADDRESS</p><h2>{label} 현장 주소 확인</h2><div class="answer-box">현장 주소와 건물명, 차량이 들어갈 입구를 함께 알려주세요. 작업 높이와 진입로, 차량과 지지대를 설치할 공간을 확인해 장비와 가능한 일정을 안내합니다.</div><a class="region-back" href="tel:01047400482">현장 주소로 전화 상담하기 ↗</a></div></section>'
    source, count = re.subn(r'<section class="section light"><div class="wrap"><p class="eyebrow">(?:AREA DIRECTORY|SITE ADDRESS)</p>.*?</section>|<section class="section light shared-address">.*?</section>', address, source, count=1, flags=re.S)
    assert count == 1
    faq = [
        (f'{name} 스카이차 상담은 어떻게 하나요?', f'도로명 주소와 건물명, 작업 내용, 희망 날짜·시간을 {PHONE}로 알려주세요. 정확한 현장 위치와 장비 조건은 통화하면서 확인합니다.'),
        (f'{name} 현장에 당일배차도 가능한가요?', '당일배차·빠른배차를 문의할 수 있습니다. 현장 주소, 차량 일정과 이동 거리, 설치 조건을 확인한 뒤 가능한 시간을 안내합니다. 주말·야간 일정도 전화로 확인해 주세요.'),
        (f'{name} 현장에는 어떤 장비가 필요한가요?', '1톤·2톤·3톤·5톤부터 대형·특수 장비까지 상담합니다. 작업 높이와 수평 거리, 탑승 인원·자재, 진입로와 설치 공간을 함께 확인합니다.'),
        ('임대 견적은 어떻게 확인하나요?', '장비 종류와 예상 작업 시간, 현장 조건을 확인한 뒤 견적을 안내합니다. 작업 인력·자재와 공사 수행 범위는 별도로 상담하며 VAT는 별도입니다.'),
        ('카드결제와 예약 변경도 가능한가요?', f'카드결제 예정이라면 예약 전에 미리 말씀해 주세요. 일정이나 작업 내용이 바뀌면 {PHONE}로 연락해 차량 일정과 현장 조건을 다시 확인합니다.'),
    ]
    faq_html = '<section class="section light"><div class="wrap regional-faq"><p class="eyebrow">QUESTIONS & ANSWERS</p><h2>'+label+' 스카이차 상담 FAQ</h2>'+''.join('<details><summary>'+escape(q)+'</summary><p>'+escape(a)+'</p></details>' for q,a in faq)+'</div></section>'
    source, count = re.subn(r'<section class="section light"><div class="wrap regional-faq">.*?</section>', faq_html, source, count=1, flags=re.S)
    assert count == 1
    source = re.sub(r'<section class="section light"><div class="wrap"><h2>같은 상위 지역의 안내 페이지</h2>.*?</section>', '', source, count=1, flags=re.S)
    source = re.sub(r'(<div class="steps"><article><span>01</span><h3>현장 주소</h3><p>).*?(</p>)', r'\g<1>도로명 주소와 건물명, 진입로 폭,<br>차량을 세울 공간을 확인해 주세요.\2', source, count=1, flags=re.S)
    source = re.sub(r'키다리스카이차 · [^<]* 스카이차 상담', BRAND+' · '+label+' 스카이차 상담', source)
    provider = {'@type':'Organization','name':BRAND,'telephone':'+82-10-4740-0482'}
    schema = {'@context':'https://schema.org','@graph':[
        {'@type':'WebPage','name':title,'description':description,'inLanguage':'ko-KR'},
        {'@type':'Service','name':f'{name} 스카이차 임대·배차 상담','serviceType':'스카이차·고소작업차 임대 상담','description':summary,'provider':provider},
        {'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':i+1,'name':n} for i,n in enumerate(['홈','전국 지역',name])]}
    ]}
    source = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda _: '<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('</','<\\/')+'</script>', source, count=1, flags=re.S)
    assert source.count('<summary>') == 5
    assert source.count('class="equipment-number"') == 4
    assert source.count('<figure>') == 9
    return source

def apply_shared_names():
    rows, manifest, pages, groups = load_groups()
    duplicates = {name:members for name,members in groups.items() if len(members)>1}
    mapping = {}
    plan = []
    for name,members in duplicates.items():
        # Preserve an existing indexed entry when the group has one.
        representative = next((r for r in members if pages[r[0]]['indexable']), members[0])
        canonical = representative[0]
        indexable = any(pages[r[0]]['indexable'] for r in members)
        codes = [r[0] for r in members]
        mapping.update({code:canonical for code in codes})
        plan.append({'name':name,'canonical':canonical,'codes':codes,'indexable':indexable})
    config = {'version':1,'enabled':True,'groups':plan,'by_code':mapping}
    (ROOT/'assets/region-name-groups.json').write_text(json.dumps(config,ensure_ascii=False,indent=2),encoding='utf-8')
    # Import after writing the configuration, so the existing renderer only
    # changes the label, retaining every approved graphic and photograph.
    from thumbnail_design import make_thumbnail
    galleries = json.loads((ROOT/'assets/region-gallery-assignments.json').read_text(encoding='utf-8'))
    for i,group in enumerate(plan):
        code = group['canonical']; name = group['name']
        source = (ROOT/f'regions/{code}.html').read_text(encoding='utf-8')
        text = common_page(source, name, code, group['indexable'])
        for member in groups[name]:
            full = member[3]
            if full != name:
                assert full not in text, (code,full)
        target = ROOT/f'assets/region-thumbnails/{code}.jpg'
        make_thumbnail(next(r for r in groups[name] if r[0]==code), {'file':pages[code]['thumbnail_photo']}, target)
        for alias in group['codes']:
            alias_text = text if alias==code else text.replace('content="index,follow,max-image-preview:large"', 'content="noindex,follow"')
            (ROOT/f'regions/{alias}.html').write_text(alias_text,encoding='utf-8')
            if alias != code:
                shutil.copyfile(target, ROOT/f'assets/region-thumbnails/{alias}.jpg')
            galleries[alias] = galleries[code]
            pages[alias]['indexable'] = group['indexable'] and alias == code
            pages[alias]['canonical_code'] = code
            pages[alias]['display_name'] = name
            pages[alias]['thumbnail_photo'] = pages[code]['thumbnail_photo']
        if (i+1)%100==0: print(f'{i+1}/{len(plan)} shared names built',flush=True)
    # All existing entry links lead to the same representative; old URLs still
    # display the shared content and identify the representative as canonical.
    pattern = re.compile(r'(?P<attr>href|src)="(?P<prefix>(?:\.\./)?(?:regions/|assets/region-thumbnails/)?)?(?P<code>\d{10})(?P<suffix>\.html|\.jpg)(?P<query>\?[^"#]*)?(?P<hash>#[^"]*)?"')
    alt_names = {escape(member[3])+' 장비 상담 안내 썸네일':escape(name)+' 장비 상담 안내 썸네일' for name,members in duplicates.items() for member in members}
    for page in [ROOT/'index.html', *sorted((ROOT/'regions').glob('*.html'))]:
        source = page.read_text(encoding='utf-8')
        def replace(m):
            code = m['code']
            if code not in mapping: return m[0]
            query = '?v=square-approved1' if m['suffix']=='.jpg' else (m['query'] or '')
            return f'{m["attr"]}="{m["prefix"] or ""}{mapping[code]}{m["suffix"]}{query}{m["hash"] or ""}"'
        updated = pattern.sub(replace, source)
        updated = re.sub(r'alt="([^"]*)"', lambda m:'alt="'+alt_names.get(m[1],m[1])+'"',updated)
        if page.name=='index.html':
            updated = re.sub(r'script\.js\?v=[^"<>]+', 'script.js?v=square-approved1', updated)
        if updated != source:
            page.write_text(updated,encoding='utf-8')
    (ROOT/'assets/region-pages.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'assets/region-gallery-assignments.json').write_text(json.dumps(galleries,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Applied {len(plan)} shared names to {len(mapping)} old URLs; other region content retained.',flush=True)

if __name__=='__main__':
    apply_shared_names()
