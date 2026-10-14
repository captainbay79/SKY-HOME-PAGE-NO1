from pathlib import Path
root = Path(__file__).resolve().parents[1]
script = root / 'script.js'
text = script.read_text(encoding='utf-8')
start = text.index('const models =')
end = text.index('const search =')
(root / 'equipment.js').write_text(text[start:end], encoding='utf-8')
script.write_text(text[:start] + text[end:], encoding='utf-8')
page = root / 'index.html'
text = page.read_text(encoding='utf-8').replace('styles.css?v=equipment2', 'styles.css?v=regional-main3').replace('script.js?v=region-order1', 'script.js?v=regional-main3')
text = text.replace('</head>', '<script src="equipment.js?v=regional-main3" defer></script></head>', 1)
page.write_text(text, encoding='utf-8')
css = root / 'styles.css'
css.write_text(css.read_text(encoding='utf-8') + '\n.equipment-visual strong{display:flex;align-items:baseline;gap:4px;color:var(--orange);letter-spacing:-2px}.equipment-visual strong small{color:var(--ink);font-size:.55em;line-height:1;margin-left:0;letter-spacing:0}\n', encoding='utf-8')
css = root / 'region.css'
css.write_text(css.read_text(encoding='utf-8') + '\n.regional-main-hero:after{background:linear-gradient(110deg,#0c151e,#1f2a30);}.regional-main-hero .wrap{position:relative}.regional-main-hero .hero-message{font-size:clamp(36px,4vw,58px)}.regional-main-hero .hero-message small{font-size:20px;color:#ffb28e;line-height:1.5}.regional-main-hero .hero-message em{font-size:30px}.regional-main-hero .hero-introduction{font-size:18px!important}.regional-main-hero .summary{font-size:13px;line-height:1.8;margin:20px 0 0}.regional-main-hero .hero-tags{margin-top:24px;gap:8px;font-size:12px}.regional-main-hero .hero-tags>span{padding:9px}.regional-main-hero figure{margin:0}@media(max-width:760px){.regional-main-hero .hero-message{font-size:42px}.regional-main-hero .hero-message em{font-size:28px}}@media(max-width:480px){.regional-main-hero .hero-message{font-size:36px}.regional-main-hero .hero-message em{font-size:25px}}\n', encoding='utf-8')
