"""Watermark approval samples only; never modifies original or site photographs."""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
source=Path(r'C:\Users\Over kim\Documents\홈페이지 제작용 이미지\광고기획 작업사진\advertising-work-1686680868703.jpg')
folder=ROOT/'assets/watermark-samples'
folder.mkdir(exist_ok=True)
with Image.open(source) as raw:
    original=ImageOps.exif_transpose(raw).convert('RGBA')
    original.thumbnail((1600,1200),Image.Resampling.LANCZOS)
w,h=original.size
font_path=r'C:\Windows\Fonts\malgunbd.ttf'
def font(size): return ImageFont.truetype(font_path,size)

layer=Image.new('RGBA',original.size)
d=ImageDraw.Draw(layer)
d.text((w-50,h-110),'키다리스카이차',font=font(48),fill=(255,255,255,70),stroke_width=1,stroke_fill=(0,0,0,36),anchor='ra')
d.text((w-50,h-54),'010-4740-0482',font=font(28),fill=(255,255,255,60),anchor='ra')
Image.alpha_composite(original,layer).convert('RGB').save(folder/'A-corner.jpg',quality=91)

def slanted_stamp(size,alpha):
    f=font(size)
    text='키다리스카이차'
    scratch=Image.new('RGBA',(1200,250))
    d=ImageDraw.Draw(scratch)
    box=d.textbbox((0,0),text,font=f,stroke_width=2)
    stamp=Image.new('RGBA',(box[2]+20,box[3]-box[1]+20))
    ImageDraw.Draw(stamp).text((10,10-box[1]),text,font=f,fill=(255,255,255,alpha),stroke_width=2,stroke_fill=(0,0,0,round(alpha*.5)))
    return stamp.rotate(20,resample=Image.Resampling.BICUBIC,expand=True)

layer=Image.new('RGBA',original.size)
stamp=slanted_stamp(104,35)
layer.alpha_composite(stamp,((w-stamp.width)//2,(h-stamp.height)//2))
Image.alpha_composite(original,layer).convert('RGB').save(folder/'B-center.jpg',quality=91)

layer=Image.new('RGBA',original.size)
stamp=slanted_stamp(45,24)
for y in range(90,h,330):
    for x in range(70,w,560):
        layer.alpha_composite(stamp,(x,y))
Image.alpha_composite(original,layer).convert('RGB').save(folder/'C-repeated.jpg',quality=91)
print('Created 3 watermark samples; original and live site photos unchanged')
