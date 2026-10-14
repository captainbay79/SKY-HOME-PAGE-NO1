from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageFont
import json
from thumbnail_design import template, photograph, region_label, font, outlined_shadow, SIZE

ROOT=Path(__file__).resolve().parents[1]
rows={r[0]:r for r in json.loads((ROOT/'assets/regions.json').read_text(encoding='utf-8'))}
manifest=json.loads((ROOT/'assets/region-pages.json').read_text(encoding='utf-8'))
entry=next(r for r in manifest if r['code']=='3111000000')
graphic,letters,unused,shade=template()
canvas=Image.alpha_composite(photograph(entry['thumbnail_photo']),shade)
canvas=Image.alpha_composite(canvas,graphic)
canvas=Image.alpha_composite(canvas,letters)
label=region_label(rows[entry['code']])
f=font(120)
box=ImageDraw.Draw(Image.new('RGBA',(1,1))).textbbox((0,0),label,font=f)
glyphs=Image.new('RGBA',(box[2]-box[0]+10,box[3]-box[1]+10))
ImageDraw.Draw(glyphs).text((5-box[0],5-box[1]),label,font=f,fill='white')
width=min(448,round(glyphs.width*110/glyphs.height))
glyphs=glyphs.resize((width,110),Image.Resampling.LANCZOS)
layer=Image.new('RGBA',SIZE)
layer.alpha_composite(glyphs,(103+(448-width)//2,55))
# One-pixel weight increase rather than the three-pixel white expansion that
# previously obscured the gaps in ㄹ. Dark outline remains distinct.
layer.putalpha(layer.getchannel('A').filter(ImageFilter.MaxFilter(3)))
canvas=Image.alpha_composite(canvas,outlined_shadow(layer,2))
canvas.convert('RGB').save(ROOT/'assets/thumbnail-samples/ulsan-bolder-black-outline.png')

source=Path(r'C:\Users\Over kim\Documents\홈페이지 제작용 이미지\광고기획 작업사진\advertising-work-1686680868703.jpg')
with Image.open(source) as raw:
    photo=ImageOps.exif_transpose(raw).convert('RGBA')
    photo.thumbnail((1600,1200),Image.Resampling.LANCZOS)
text='키다리스카이차'
f=ImageFont.truetype(r'C:\Windows\Fonts\malgunbd.ttf',45)
box=ImageDraw.Draw(Image.new('RGBA',(1,1))).textbbox((0,0),text,font=f,stroke_width=2)
stamp=Image.new('RGBA',(box[2]+20,box[3]-box[1]+20))
ImageDraw.Draw(stamp).text((10,10-box[1]),text,font=f,fill=(255,255,255,38),stroke_width=2,stroke_fill=(0,0,0,19))
stamp=stamp.rotate(20,resample=Image.Resampling.BICUBIC,expand=True)
overlay=Image.new('RGBA',photo.size)
for y in range(90,photo.height,330):
    for x in range(70,photo.width,560): overlay.alpha_composite(stamp,(x,y))
Image.alpha_composite(photo,overlay).convert('RGB').save(ROOT/'assets/watermark-samples/C-repeated-15-percent.jpg',quality=91)
print('Saved heavier thumbnail and 15% repeating watermark approval samples; live images unchanged')
