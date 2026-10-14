from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
reference = Image.open(ROOT/'assets/thumbnail-samples/ulsan-jung-gu-orange-region.png').convert('RGB')
source = Path(r'C:\Users\Over kim\Documents\홈페이지 제작용 이미지\광고기획 작업사진\advertising-work-1686680868703.jpg')
with Image.open(source) as raw:
    original = ImageOps.exif_transpose(raw).convert('RGB')
    # Keep the entire photograph and its original equipment placement.
    canvas = original.resize(reference.size, Image.Resampling.LANCZOS).convert('RGBA')
w,h=canvas.size
shade=Image.new('RGBA',(w,h))
d=ImageDraw.Draw(shade)
for x in range(w):
    alpha=round(210*max(0,1-x/(w*.8)))
    d.line((x,0,x,881),fill=(10,15,19,alpha))
canvas=Image.alpha_composite(canvas,shade)

# Reuse the selected rounded orange panel, location icon, and exact lettering.
region=reference.copy()
pixels=np.array(region)
area=pixels[96:303,175:1016].astype(float)
coverage=np.clip((255-area[:,:,0])/240,0,1)
# Black lettering becomes white, with its original antialiased edges preserved.
area=area*(1-coverage[:,:,None])+255*coverage[:,:,None]
pixels[96:303,175:1016]=area.astype(np.uint8)
region=Image.fromarray(pixels).convert('RGBA')
mask=Image.new('L',(w,h),0)
ImageDraw.Draw(mask).rounded_rectangle((33,70,1044,325),radius=40,fill=255)
canvas.paste(region,(0,0),mask)

# Extract only lettering from the selected sample, not the AI-reconstructed photo.
arr=np.array(reference)
for box,color in [((35,380,725,563),'white'),((40,574,724,751),'orange')]:
    x0,y0,x1,y1=box
    crop=arr[y0:y1,x0:x1].astype(float)
    if color=='white':
        coverage=np.clip((np.min(crop,axis=2)-185)/60,0,1)
        rgb=(255,255,255)
    else:
        valid=(crop[:,:,0]>175)&(crop[:,:,1]<155)&(crop[:,:,2]<80)
        coverage=np.where(valid,np.clip((crop[:,:,0]-150)/95,0,1),0)
        rgb=(255,99,31)
    overlay=Image.new('RGBA',(x1-x0,y1-y0),rgb+(255,))
    overlay.putalpha(Image.fromarray((coverage*255).astype(np.uint8)))
    canvas.alpha_composite(overlay,(x0,y0))

# Keep the selected phone ribbon, number and white telephone icon as supplied.
phone_mask=Image.new('L',(w,h),0)
ImageDraw.Draw(phone_mask).polygon([(0,882),(1332,882),(1354,894),(w,h),(0,h)],fill=255)
canvas.paste(reference,(0,0),phone_mask)
out=ROOT/'assets/thumbnail-samples/ulsan-jung-gu-original-white-region.png'
canvas.convert('RGB').save(out)
print('Saved original-photo sample with white region lettering')
