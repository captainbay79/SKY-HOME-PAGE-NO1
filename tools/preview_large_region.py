"""Approval-only larger region label with open letter counters and crisp outline."""
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
d=ImageDraw.Draw(canvas)
# Give the title most of the canvas width rather than shrinking long names.
d.rounded_rectangle((18,30,780,195),radius=24,fill='#ff631f')
# Retain the original pin, while the region panel and letter size grow.
canvas.alpha_composite(graphic.crop((27,67,88,153)),(27,67))
canvas=Image.alpha_composite(canvas,letters)
layer=Image.new('RGBA',SIZE)
d=ImageDraw.Draw(layer)
label=region_label(row).replace(' ','  ')
size=120
while size>24:
    f=font(size)
    box=d.textbbox((0,0),label,font=f)
    if box[2]-box[0]<=661 and box[3]-box[1]<=130: break
    size-=1
x=100+(663-(box[2]-box[0]))/2-box[0]
y=45+(132-(box[3]-box[1]))/2-box[1]
# Do not fatten the white letters: internal gaps stay open and readable.
d.text((x,y),label,font=f,fill='white')
outline=Image.new('RGBA',SIZE,(32,23,18,255))
outline.putalpha(layer.getchannel('A').filter(ImageFilter.MaxFilter(9)))
outlined=Image.alpha_composite(outline,layer)
canvas=Image.alpha_composite(canvas,shadow(outlined))
out=ROOT/'assets/thumbnail-samples/sejong-jeonui-large-crisp-outline.png'
canvas.convert('RGB').save(out)
print(f'Saved larger approval sample, region font {size}px; live pages unchanged')
