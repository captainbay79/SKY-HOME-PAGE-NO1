"""Sample only: original orange label size with heavier, tall region lettering."""
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
# Use larger bold glyphs and a compact width, keeping the selected box intact.
f=font(120)
scratch=Image.new('RGBA',(1000,250))
d=ImageDraw.Draw(scratch)
box=d.textbbox((0,0),label,font=f,stroke_width=3)
d.text((5-box[0],5-box[1]),label,font=f,fill='white',stroke_width=3,stroke_fill='white')
glyphs=scratch.crop((0,0,box[2]-box[0]+10,box[3]-box[1]+10))
glyphs=glyphs.resize((448,110),Image.Resampling.LANCZOS)
layer=Image.new('RGBA',SIZE)
layer.alpha_composite(glyphs,(103,55))
outline=Image.new('RGBA',SIZE,(32,23,18,255))
outline.putalpha(layer.getchannel('A').filter(ImageFilter.MaxFilter(7)))
canvas=Image.alpha_composite(canvas,shadow(Image.alpha_composite(outline,layer)))
out=ROOT/'assets/thumbnail-samples/sejong-jeonui-original-box-bold.png'
canvas.convert('RGB').save(out)
print('Saved original-size orange box with heavier lettering; live pages unchanged')
