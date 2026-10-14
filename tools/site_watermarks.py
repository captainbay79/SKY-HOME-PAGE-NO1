"""Apply approved C repeat watermarks to displayed site photos, preserving originals."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import json

ROOT=Path(__file__).resolve().parents[1]

def watermark(source,destination):
    with Image.open(source) as raw:
        photo=ImageOps.exif_transpose(raw).convert('RGBA')
    scale=photo.width/1600
    f=ImageFont.truetype(r'C:\Windows\Fonts\malgunbd.ttf',max(15,round(45*scale)))
    stroke=max(1,round(2*scale))
    text='키다리스카이차'
    box=ImageDraw.Draw(Image.new('RGBA',(1,1))).textbbox((0,0),text,font=f,stroke_width=stroke)
    pad=max(5,round(10*scale))
    stamp=Image.new('RGBA',(box[2]-box[0]+pad*2,box[3]-box[1]+pad*2))
    ImageDraw.Draw(stamp).text((pad-box[0],pad-box[1]),text,font=f,
                             fill=(255,255,255,38),stroke_width=stroke,stroke_fill=(0,0,0,19))
    stamp=stamp.rotate(20,resample=Image.Resampling.BICUBIC,expand=True)
    layer=Image.new('RGBA',photo.size)
    for y in range(round(90*scale),photo.height,max(1,round(330*scale))):
        for x in range(round(70*scale),photo.width,max(1,round(560*scale))):
            layer.alpha_composite(stamp,(x,y))
    destination.parent.mkdir(parents=True,exist_ok=True)
    Image.alpha_composite(photo,layer).convert('RGB').save(destination,quality=90,optimize=True)

def apply_site_watermarks():
    catalog=[]
    for directory, target_directory in [('work','work'),('regional-photos','regional-photos'),('thumbnail-photos','gallery')]:
        for source in sorted((ROOT/'assets'/directory).glob('*.jpg')):
            destination=ROOT/'assets/watermarked'/target_directory/source.name
            watermark(source,destination)
            catalog.append({'source':source.relative_to(ROOT).as_posix(),
                            'file':destination.relative_to(ROOT).as_posix(),
                            'style':'C-repeated','opacity':.15,'text':'키다리스카이차',
                            'thumbnail_excluded':True})
    # Reference only separate marked copies in all live pages.
    files=[ROOT/'index.html']+list((ROOT/'regions').glob('*.html'))
    for p in files:
        s=p.read_text(encoding='utf-8')
        for directory in ['work','regional-photos']:
            s=s.replace(f'assets/{directory}/',f'assets/watermarked/{directory}/')
        p.write_text(s,encoding='utf-8')
    (ROOT/'assets/watermark-catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Applied C watermark at 15% to {len(catalog)} site photos; originals and thumbnails preserved',flush=True)

if __name__=='__main__': apply_site_watermarks()
