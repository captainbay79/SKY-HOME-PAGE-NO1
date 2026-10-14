"""Approval preview only: restore a single region line and add a crisp outline."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import json
from thumbnail_design import template, photograph, region_label, font, shadow, SIZE

ROOT=Path(__file__).resolve().parents[1]
rows=json.loads((ROOT/'assets/regions.json').read_text(encoding='utf-8'))
row=next(r for r in rows if r[0]=='3611037000')
manifest=json.loads((ROOT/'assets/region-pages.json').read_text(encoding='utf-8'))
photo=next(r['thumbnail_photo'] for r in manifest if r['code']==row[0])
graphic,letters,unused,shade=template()
canvas=Image.alpha_composite(photograph(photo),shade)
canvas=Image.alpha_composite(canvas,graphic)
canvas=Image.alpha_composite(canvas,letters)
label=region_label(row)
layer=Image.new('RGBA',SIZE)
d=ImageDraw.Draw(layer)
size=96
while size>24:
    f=font(size)
    box=d.textbbox((0,0),label,font=f,stroke_width=3)
    if box[2]-box[0]<=448 and box[3]-box[1]<=106: break
    size-=1
x=97+(459-(box[2]-box[0]))/2-box[0]
y=52+(114-(box[3]-box[1]))/2-box[1]
d.text((x,y),label,font=f,fill='white',stroke_width=3,stroke_fill='white')
outline=Image.new('RGBA',SIZE,(36,25,19,255))
outline.putalpha(layer.getchannel('A').filter(ImageFilter.MaxFilter(7)))
outlined=Image.alpha_composite(outline,layer)
canvas=Image.alpha_composite(canvas,shadow(outlined))
out=ROOT/'assets/thumbnail-samples/sejong-jeonui-single-line-outline.png'
canvas.convert('RGB').save(out)
print('Saved sample only; live pages unchanged')
