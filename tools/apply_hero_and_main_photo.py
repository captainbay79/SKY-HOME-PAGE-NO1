"""Apply approved hero controls and the supplied main photo, with local recovery."""
from pathlib import Path
import hashlib
import json
import re
import runpy
import subprocess
from restore_before_shared_names import inspect, STATE

ROOT=Path(__file__).resolve().parents[1]
BACKUP=ROOT/'.recovery/hero-photo-before'

def apply():
    recovery=inspect()
    preview=runpy.run_path(str(ROOT/'.preview/make-hero-cta-subtle-preview.py'))
    tags,actions=preview['tags'],preview['cta']
    css=preview['style'].removeprefix('<style>').removesuffix('</style>')
    tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().strip('\0').split('\0'))
    before={}
    def write(relative, content):
        path=ROOT/relative
        data=content.encode('utf-8')
        old=path.read_bytes() if path.exists() else None
        if old==data: return
        if relative in recovery['files'] and old is not None:
            assert hashlib.sha256(old).hexdigest()==recovery['files'][relative]['applied_sha256'],relative
        saved=BACKUP/relative
        if old is not None and not saved.exists():
            saved.parent.mkdir(parents=True,exist_ok=True)
            saved.write_bytes(old)
        before[relative]={'existed':old is not None,'before_sha256':hashlib.sha256(old).hexdigest() if old is not None else None}
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)
        info=recovery['files'].setdefault(relative,{'new':relative not in tracked})
        info['applied_sha256']=hashlib.sha256(data).hexdigest()
        # Persist recovery after every write, so interruption remains recoverable.
        STATE.write_text(json.dumps(recovery,ensure_ascii=False,indent=2),encoding='utf-8')
    module='"""Approved small phone CTA and two-row hero benefits."""\nHERO_TAGS='+repr(tags)+'\nHERO_ACTIONS='+repr(actions)+'\nHERO_CSS='+repr(css)+'\n'
    write('tools/hero_elements.py',module)
    stylesheet=(ROOT/'styles.css').read_text(encoding='utf-8')
    marker='/* Approved hero controls: small phone CTA and separate payment row */'
    if marker not in stylesheet:
        stylesheet+='\n'+marker+'\n'+css+'\n#main-field-05 img{aspect-ratio:4/3;object-fit:contain}\n'
    write('styles.css',stylesheet)
    count=0
    for path in [ROOT/'index.html',*sorted((ROOT/'regions').glob('*.html'))]:
        source=path.read_text(encoding='utf-8')
        if 'class="hero-actions"' not in source: continue
        if actions not in source:
            source,n=re.subn(r'<div class="hero-actions">.*?</div>',actions,source,count=1,flags=re.S)
            assert n==1,path
        if tags not in source:
            source,n=re.subn(r'<div class="hero-tags">.*?</div>',tags,source,count=1,flags=re.S)
            assert n==1,path
        source=re.sub(r'(href="(?:\.\./)?styles\.css)(?:\?[^"<>]*)?"',r'\1?v=hero-proof6"',source)
        if path==ROOT/'index.html':
            field=re.search(r'<section id="field".*?</section>',source,re.S)[0]
            figures=re.findall(r'<figure(?: [^>]*)?>.*?</figure>',field,re.S)
            assert len(figures)==8
            photo='<figure id="main-field-05"><div><img src="assets/watermarked/gallery/advertising-work-20260406-062158.jpg" alt="경기장 조명 구조물 옆으로 작업대를 펼친 스카이차" loading="lazy" width="1400" height="1050"><span>FIELD / 05</span></div><figcaption><h3>경기장 조명 구조물 앞 장비 배치</h3><p>조명 구조물 옆 작업대 위치와 장비 설치 공간 확인</p></figcaption></figure>'
            source=source.replace(field,field.replace(figures[4],photo,1),1)
        assert source.count('class="hero-tags hero-proof"')==1
        assert source.count('hero-consult-subtle')==1
        assert source.count('class="proof-payment"')==1
        write(path.relative_to(ROOT).as_posix(),source)
        count+=1
        if count%1000==0: print(f'{count}/5352 local hero blocks applied',flush=True)
    assert count==5352,count
    path=ROOT/'tools/regional_main_design.py'
    source=path.read_text(encoding='utf-8')
    source=source.replace('from regional_gallery import gallery_section','from regional_gallery import gallery_section\nfrom hero_elements import HERO_TAGS, HERO_ACTIONS')
    source=re.sub(r'    actions = re.search\(.*?\n', '    actions = HERO_ACTIONS\n',source,count=1)
    source=re.sub(r'    tags = re.search\(.*?\n','    tags = HERO_TAGS\n',source,count=1)
    source=source.replace('styles.css?v=service-soft5','styles.css?v=hero-proof6')
    write('tools/regional_main_design.py',source)
    path=ROOT/'tools/verify_regions.py'
    source=path.read_text(encoding='utf-8').replace('styles.css?v=service-soft5','styles.css?v=hero-proof6')
    source=source.replace("main_field.count('<figure>')", "len(re.findall(r'<figure(?: [^>]*)?>',main_field))")
    source=source.replace("    if 'class=\"service-band\"' in html:","    if 'class=\"service-band\"' in html:\n        if html.count('class=\"hero-tags hero-proof\"')!=1 or html.count('hero-consult-subtle')!=1:\n            errors.append(f'{p.name}: missing approved hero controls')")
    write('tools/verify_regions.py',source)
    own='tools/apply_hero_and_main_photo.py'
    recovery['files'][own]={'new':own not in tracked,'applied_sha256':hashlib.sha256((ROOT/own).read_bytes()).hexdigest()}
    STATE.write_text(json.dumps(recovery,ensure_ascii=False,indent=2),encoding='utf-8')
    (BACKUP/'changes.json').write_text(json.dumps(before,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Applied hero design to {count} local pages; main photo 05 replaced. Recovery preserved; no upload or deployment.',flush=True)

if __name__=='__main__': apply()
