from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
source = Path(r'C:\Users\Over kim\Documents\홈페이지 제작용 이미지\광고기획 작업사진\advertising-work-1686680868703.jpg')
font_path = r'C:\Windows\Fonts\malgunbd.ttf'
with Image.open(source) as raw:
    original = ImageOps.exif_transpose(raw).convert('RGB')
    w,h = original.size
    # Crop only; never reconstruct or move any photographic content.
    crop_width = round(w*.82)
    crop_height = round(crop_width*.75)
    top = round((h-crop_height)*.7)
    photo = original.crop((0,top,crop_width,top+crop_height)).resize((1200,900),Image.Resampling.LANCZOS).convert('RGBA')

shade=Image.new('RGBA',photo.size)
shade_draw=ImageDraw.Draw(shade)
for x in range(1200):
    alpha=round(205*max(0,1-x/1100))
    shade_draw.line((x,0,x,755),fill=(9,15,19,alpha))
photo=Image.alpha_composite(photo,shade)
draw=ImageDraw.Draw(photo)

def fitted(text,max_width,start_size):
    size=start_size
    while True:
        font=ImageFont.truetype(font_path,size)
        if draw.textbbox((0,0),text,font=font)[2]<=max_width: return font
        size-=1

def label(x,y,text,width,size,color):
    draw.text((x,y),text,font=fitted(text,width,size),fill=color,stroke_width=3,stroke_fill='#11191f',anchor='lt')

# Region gets a bright yellow treatment distinct from the white middle headline.
draw.ellipse((42,66,93,117),fill='#ffe34d')
draw.polygon([(43,100),(92,100),(68,143)],fill='#ffe34d')
draw.ellipse((56,80,79,103),fill='#171a1b')
label(120,45,'울산 중구',1020,176,'#ffe34d')
label(44,290,'우리동네',715,159,'white')
label(44,485,'스카이차',715,169,'#ff631f')

# Retain the original bottom phone ribbon position, orange and white styling.
draw.polygon([(0,755),(1118,755),(1200,900),(0,900)],fill='#ff631f')
draw.ellipse((28,776,132,880),fill='white')
draw.arc((55,797,114,854),75,260,fill='#ff631f',width=15)
draw.line((59,802,71,817),fill='#ff631f',width=17)
draw.line((94,846,110,836),fill='#ff631f',width=17)
draw.text((158,787),'010-4740-0482',font=fitted('010-4740-0482',960,111),fill='white',anchor='lt')
out=ROOT/'assets/thumbnail-samples/ulsan-jung-gu-original-yellow.png'
photo.convert('RGB').save(out)
print(out)
