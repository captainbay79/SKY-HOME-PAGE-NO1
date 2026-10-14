from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
import json

source = Path(r'C:\Users\Over kim\Documents\홈페이지 제작용 이미지\광고기획 작업사진')
files = sorted(source.glob('advertising-work-*.jpg'))
chosen = [files[round(i * (len(files)-1) / 59)] for i in range(60)]
out = Path('.preview')
out.mkdir(exist_ok=True)
(out / 'photo-selection.json').write_text(json.dumps([str(p) for p in chosen], ensure_ascii=False), encoding='utf-8')
for page in range(3):
    canvas = Image.new('RGB', (1200, 880), '#ecece8')
    draw = ImageDraw.Draw(canvas)
    for j,p in enumerate(chosen[page*20:(page+1)*20]):
        with Image.open(p) as raw:
            raw.draft('RGB',(600,600))
            im = ImageOps.exif_transpose(raw).convert('RGB')
            im.thumbnail((288,180))
            x=(j%4)*300+(300-im.width)//2
            y=(j//4)*176
            canvas.paste(im,(x,y))
            draw.rectangle(((j%4)*300,y+150,(j%4)*300+299,y+175), fill='#171a1b')
            draw.text(((j%4)*300+10,y+154),f'{page*20+j:02d} / {p.stem[-15:]}',fill='white')
    canvas.save(out/f'contact-{page}.jpg')
print(f'{len(files)} source photos; 60 sampled for review')
