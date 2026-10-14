from pathlib import Path
from PIL import Image, ImageFilter, ImageChops
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'assets/thumbnail-samples'
reference=Image.open(folder/'ulsan-jung-gu-orange-region.png').convert('RGB')
base=Image.open(folder/'ulsan-jung-gu-original-white-region.png').convert('RGBA')
arr=np.array(reference).astype(float)
text_mask=Image.new('L',base.size,0)

# Recover the exact letter shapes from the selected design; omit the map pin
# and phone ribbon so both remain unchanged.
region=arr[96:303,175:1016]
coverage=np.clip((255-region[:,:,0])/240,0,1)
text_mask.paste(Image.fromarray((coverage*255).astype(np.uint8)),(175,96))
for box,color in [((35,380,725,563),'white'),((40,574,724,751),'orange')]:
    x0,y0,x1,y1=box
    crop=arr[y0:y1,x0:x1]
    if color=='white':
        alpha=np.clip((np.min(crop,axis=2)-185)/60,0,1)
    else:
        valid=(crop[:,:,0]>175)&(crop[:,:,1]<155)&(crop[:,:,2]<80)
        alpha=np.where(valid,np.clip((crop[:,:,0]-150)/95,0,1),0)
    text_mask.paste(Image.fromarray((alpha*255).astype(np.uint8)),(x0,y0))

def render(effect,name):
    layer=Image.new('RGBA',base.size,(12,17,20,255))
    layer.putalpha(effect)
    result=Image.alpha_composite(base,layer)
    # Restore exact original letter fills above the effect.
    result.paste(base,(0,0),text_mask)
    result.convert('RGB').save(folder/name)
    return result.convert('RGB')

shifted=Image.new('L',base.size,0)
shifted.paste(text_mask,(9,12))
shadow=shifted.filter(ImageFilter.GaussianBlur(5)).point(lambda p:round(p*.86))
a=render(shadow,'ulsan-jung-gu-shadow.png')
expanded=text_mask.filter(ImageFilter.MaxFilter(17))
outline=ImageChops.subtract(expanded,text_mask).point(lambda p:round(p*.95))
b=render(outline,'ulsan-jung-gu-outline.png')
preview=Image.new('RGB',(1448,543),'white')
preview.paste(a.resize((724,543),Image.Resampling.LANCZOS),(0,0))
preview.paste(b.resize((724,543),Image.Resampling.LANCZOS),(724,0))
preview.save(ROOT/'.preview/text-effect-comparison.jpg',quality=92)
print('Saved shadow and outline variants; photo, icon and phone unchanged')
