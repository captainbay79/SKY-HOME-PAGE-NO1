"""Approved photo-preserving 4:3 thumbnail design with text/phone shadows."""
from functools import lru_cache
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SIZE=(800,600)
REFERENCE=ROOT/'assets/thumbnail-samples/ulsan-jung-gu-orange-region.png'
FONT=r'C:\Windows\Fonts\malgunbd.ttf'
SHORT={'서울특별시':'서울','전남광주통합특별시':'전남광주','부산광역시':'부산','대구광역시':'대구','인천광역시':'인천','대전광역시':'대전','울산광역시':'울산','세종특별자치시':'세종','경기도':'경기','충청북도':'충북','충청남도':'충남','경상북도':'경북','경상남도':'경남','제주특별자치도':'제주','강원특별자치도':'강원','전북특별자치도':'전북'}

def resized(image):
    return image.resize(SIZE,Image.Resampling.LANCZOS)

def shadow(layer):
    alpha=layer.getchannel('A')
    shifted=Image.new('L',layer.size,0)
    shifted.paste(alpha,(5,7))
    effect=Image.new('RGBA',layer.size,(12,17,20,0))
    effect.putalpha(shifted.filter(ImageFilter.GaussianBlur(3)).point(lambda p:round(p*.86)))
    return Image.alpha_composite(effect,layer)

def outlined_shadow(layer,width=2):
    edge=Image.new('RGBA',layer.size,(0,0,0,255))
    edge.putalpha(layer.getchannel('A').filter(ImageFilter.MaxFilter(width*2+1)))
    return shadow(Image.alpha_composite(edge,layer))

@lru_cache(maxsize=1)
def template():
    ref=Image.open(REFERENCE).convert('RGB')
    arr=np.array(ref).astype(float)
    graphic=Image.new('RGBA',ref.size)
    # Orange header and original black map pin, with the old letters cleared.
    card=Image.new('RGB',ref.size,'#ff631f')
    # Recover only the dark pin, leaving a clean uniform orange label.
    pin=arr[125:280,50:165]
    pin_alpha=np.clip((100-pin[:,:,0])/70,0,1)
    pin_layer=Image.new('RGBA',(115,155),(12,17,20,255))
    pin_layer.putalpha(Image.fromarray((pin_alpha*255).astype(np.uint8)))
    card.paste(pin_layer,(50,125),pin_layer)
    mask=Image.new('L',ref.size,0)
    ImageDraw.Draw(mask).rounded_rectangle((33,70,1044,325),radius=40,fill=255)
    graphic.paste(card,(0,0),mask)
    # Approved bottom ribbon; preserve all geometry but redraw digits as a layer.
    ribbon=Image.new('RGB',ref.size,'#ff631f')
    icon_mask=Image.new('L',ref.size,0)
    ImageDraw.Draw(icon_mask).ellipse((40,900,190,1049),fill=255)
    phone_icon=ref.convert('RGBA')
    phone_icon.putalpha(icon_mask)
    mask=Image.new('L',ref.size,0)
    ImageDraw.Draw(mask).polygon([(0,882),(1332,882),(1354,894),(1448,1086),(0,1086)],fill=255)
    graphic.paste(ribbon,(0,0),mask)
    letters=Image.new('RGBA',ref.size)
    for box,color in [((35,380,725,563),'white'),((40,574,724,751),'orange'),((203,902,1352,1052),'white')]:
        x0,y0,x1,y1=box
        crop=arr[y0:y1,x0:x1]
        if color=='white':
            alpha=np.clip((np.min(crop,axis=2)-185)/60,0,1)
            rgb=(255,255,255)
        else:
            valid=(crop[:,:,0]>175)&(crop[:,:,1]<155)&(crop[:,:,2]<80)
            alpha=np.where(valid,np.clip((crop[:,:,0]-150)/95,0,1),0)
            rgb=(255,99,31)
        part=Image.new('RGBA',(x1-x0,y1-y0),rgb+(255,))
        part.putalpha(Image.fromarray((alpha*255).astype(np.uint8)))
        letters.alpha_composite(part,(x0,y0))
    # Exact selected lettering is retained for the approved Ulsan example.
    alpha=np.clip((255-arr[96:303,175:1016,0])/240,0,1)
    ul=Image.new('RGBA',ref.size)
    part=Image.new('RGBA',(841,207),'white')
    part.putalpha(Image.fromarray((alpha*255).astype(np.uint8)))
    ul.alpha_composite(part,(175,96))
    shade=Image.new('RGBA',SIZE)
    d=ImageDraw.Draw(shade)
    for x in range(800):
        d.line((x,0,x,487),fill=(10,15,19,round(210*max(0,1-x/640))))
    effects=Image.alpha_composite(outlined_shadow(resized(letters),2),shadow(resized(phone_icon)))
    return resized(graphic),effects,shadow(resized(ul)),shade

@lru_cache(maxsize=24)
def photograph(filename):
    with Image.open(ROOT/filename) as photo:
        # Resize/crop uniformly. No equipment is moved, reconstructed or removed.
        image=ImageOps.fit(photo.convert('RGBA'),(800,487),centering=(.5,.75))
        canvas=Image.new('RGBA',SIZE,'#171a1b')
        canvas.paste(image,(0,0))
        return canvas

@lru_cache(maxsize=128)
def font(size):
    return ImageFont.truetype(FONT,size)

def region_label(row):
    parts=row[3].split()
    if len(parts)<=2: return ' '.join([SHORT.get(parts[0],parts[0])]+parts[1:])
    return ' '.join(parts[-2:])

def region_text(label):
    # Final approved sample: one bold white region line in the original box,
    # with a clear dark outline and shadow. Avoid separate region badges.
    f=font(120)
    probe=ImageDraw.Draw(Image.new('RGBA',(1,1)))
    box=probe.textbbox((0,0),label,font=f)
    glyphs=Image.new('RGBA',(box[2]-box[0]+10,box[3]-box[1]+10))
    d=ImageDraw.Draw(glyphs)
    # Font is already bold: white dilation was closing the small gaps in ㄹ.
    # Preserve the original glyph counters, outline after resizing instead.
    d.text((5-box[0],5-box[1]),label,font=f,fill='white')
    width=min(448,round(glyphs.width*110/glyphs.height))
    glyphs=glyphs.resize((width,110),Image.Resampling.LANCZOS)
    layer=Image.new('RGBA',SIZE)
    layer.alpha_composite(glyphs,(103+(448-width)//2,55))
    layer.putalpha(layer.getchannel('A').filter(ImageFilter.MaxFilter(3)))
    return outlined_shadow(layer,2)

def make_thumbnail(row,photo,path):
    graphic,letters,ulsan,shade=template()
    canvas=Image.alpha_composite(photograph(photo['file']),shade)
    canvas=Image.alpha_composite(canvas,graphic)
    canvas=Image.alpha_composite(canvas,letters)
    canvas=Image.alpha_composite(canvas,region_text(region_label(row)))
    canvas.convert('RGB').save(path,quality=78,optimize=True)
