from pathlib import Path
import json
from PIL import Image, ImageOps, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
photos=json.loads((ROOT/'assets/thumbnail-photo-catalog.json').read_text(encoding='utf-8'))
out=ROOT/'.preview/photo-caption-review'
out.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf',18)
for start in range(0,len(photos),48):
    sheet=Image.new('RGB',(1440,1068),'white')
    draw=ImageDraw.Draw(sheet)
    for offset,photo in enumerate(photos[start:start+48]):
        x=(offset%8)*180;y=(offset//8)*178
        with Image.open(ROOT/photo['file']) as raw:
            thumb=ImageOps.contain(raw.convert('RGB'),(174,148))
        sheet.paste(thumb,(x+(180-thumb.width)//2,y))
        draw.text((x+8,y+151),str(start+offset),fill='black',font=font)
    sheet.save(out/f'sheet-{start//48:02d}.jpg',quality=90)
print(f'Created {(len(photos)+47)//48} numbered review sheets for {len(photos)} source photographs.')
