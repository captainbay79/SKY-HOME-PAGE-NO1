"""Business details supplied by the site owner."""
BUSINESS_INFO = '''<dl class="wrap business-info" aria-label="사업자 정보"><div><dt>상호</dt><dd>스카이차</dd></div><div><dt>사업자등록번호</dt><dd>417-16-27305</dd></div><div><dt>이메일</dt><dd><a href="mailto:skyhi0482@gmail.com">skyhi0482@gmail.com</a></dd></div><div><dt>고객센터</dt><dd><a href="tel:01047400482">010-4740-0482</a></dd></div></dl>'''

def apply_business_footer(html):
    html = html.replace('카드결제 사전 요청 · VAT 별도', '카드결제시 사전요청, VAT별도')
    if 'class="wrap business-info"' not in html:
        html = html.replace('<div class="wrap footer-bottom">', BUSINESS_INFO + '<div class="wrap footer-bottom">', 1)
    return html

if __name__ == '__main__':
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    pages = [root/'index.html'] + list((root/'regions').glob('*.html'))
    for i,page in enumerate(pages):
        text=apply_business_footer(page.read_text(encoding='utf-8'))
        assert text.count('class="wrap business-info"')==1
        assert 'href="mailto:skyhi0482@gmail.com"' in text
        assert '카드결제 사전 요청 · VAT 별도' not in text
        text=text.replace('?v=regional-refinement4','?v=business-footer6')
        page.write_text(text,encoding='utf-8')
        if (i+1)%1000==0: print(f'{i+1}/{len(pages)} footers updated',flush=True)
    styles=root/'styles.css'
    styles.write_text(styles.read_text(encoding='utf-8')+'''
footer .business-info{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px 36px;padding-top:28px;margin-top:28px;border-top:1px solid #ffffff26;font-size:14px;line-height:1.7}
footer .business-info>div{display:flex;align-items:baseline;gap:12px;min-width:0}footer .business-info dt{color:#a9afaf;font-size:12px;flex-shrink:0}footer .business-info dd{margin:0;color:#fff;font-size:14px;font-weight:600}footer .business-info a{font-size:14px!important;overflow-wrap:anywhere}footer .business-info a:hover{color:var(--orange)}
@media(max-width:760px){footer .business-info{grid-template-columns:1fr;gap:12px}footer .business-info dt{min-width:96px}}
''',encoding='utf-8')
    print(f'Updated and verified business details on {len(pages)} pages.',flush=True)
