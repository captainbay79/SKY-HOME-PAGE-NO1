"""Captions based on visual inspection of all 471 numbered source photographs."""
from pathlib import Path
import json
import re
from regional_gallery import gallery_section, data

ROOT=Path(__file__).resolve().parents[1]
photos=json.loads((ROOT/'assets/thumbnail-photo-catalog.json').read_text(encoding='utf-8'))
titles={i:'건물 외벽 앞 스카이차 배치' for i in range(len(photos))}
def label(title, numbers):
    for part in numbers.split():
        if '-' in part:
            start,end=map(int,part.split('-'))
            indices=range(start,end+1)
        else: indices=[int(part)]
        for i in indices: titles[i]=title

label('주택 사이 골목의 스카이차 배치','2 24 67-69 82-83 91-94 100-101 157 176 195 215 227 307 323 335-338 346-347 359 398-399 401-403 407-412 420 425 438-439 448 450 458-459 469-470')
label('상가 앞 도로변 스카이차 배치','11-12 18 20-21 30 33 48-50 53-60 84-88 95-99 110-114 116 120-122 124-125 131 140 142-146 148 150 152 159 161-162 164-167 173 175 183 188-189 199 204-206 214 216 222 226 241-245 254 259-260 273 276 279-286 297-299 311-313 316-320 327-329 342-343 348-352 355 360 364-369 371-375 379 386-389 394-396 404-406 413-414 418-419 421-424 431-437 441 447 451-455 460-464')
label('아파트 앞 진입로의 스카이차 배치','51-52 104-105 107 109 123 174 201 212-213 225 321-322 324-326 349 397')
label('수목 주변 도로의 스카이차 배치','6-10 170 187 339-340 377-378 456-457')
label('건물 앞 넓은 공간의 스카이차 배치','3 19 23 63-64 106 127-129 134-136 160 184-186 198 202-203 217 228 271-272 275 308 341 344-345 354 376 390 393 400 415-416 426 430 442-446 466')
label('공사 현장 구조물 앞 스카이차 배치','1 5 14 25 46 65-66 89 130 132-133 153 158 163 196 207-211 270 361-362 392 427-428 433 434')
label('건물 사이 위로 펼친 붐대와 작업대','4 180-182 281')
label('교량 아래 스카이차와 작업대 배치','31-32 35-37 73-75 102-103 224 255-257 309-310 449')
label('교량 아래 조명을 켠 야간 작업대 배치','38-44 71-72 76-81')
label('실내 천장 아래 스카이차 배치','13 16 34 108 119 171-172 357-358 382-385 429')
label('터널 내부 스카이차와 작업대 배치','137-139')
label('도로 위 지붕 구조물 아래 작업대 배치','70 235 239-240 246-253 258 277 391')
label('야간 도로변 구조물 아래 스카이차 배치','154-156')
label('도로 교차로 위로 펼친 작업대','61-62 111 197')
label('조명이 켜진 상가 외벽 앞 야간 장비 배치','118 177-179 190-191 228-234 261-269 287-291 300-305 330-334 354 363 417 440 465')
label('유리 외벽 앞 스카이차 작업대 배치','26-29 54-55 85-87 149 151 165 181-182 241-245 254 297-299 306 314-315 327 341 348 350 364 371 374 424 453 455')
label('공장·창고 건물 앞 스카이차 배치','117 160 183-185 198 202 236-238 356 390 426 466')
label('운동장 조명탑 옆 스카이차 배치','168-169 218-221 292-296 467-468')
label('벽돌 건물 앞 스카이차 배치','112 175 192-194 203 215 278 323 347 359 379-381 408 411-412 437-439 469-470')
label('건물 외벽의 간판 앞 작업대 배치','57 60 121 165 228-234 262 280 301-305 332-334 351-352 373 447')
label('건물 옆 통로에 펼친 스카이차 붐대','45 47 90 115 126 223 353 361-362 410 414')
# User-selected examples: the actual alley and illuminated storefront photographs.
plan=json.loads((ROOT/'assets/region-gallery-assignments.json').read_text(encoding='utf-8'))
index={photo['file']:i for i,photo in enumerate(photos)}
titles[index[plan['4400000000'][7]]]='주택 사이 좁은 골목의 스카이차 배치'
titles[index[plan['4400000000'][5]]]='조명이 켜진 상가 외벽 앞 야간 장비 배치'
captions={photo['file']:{'title':titles[i],'sha256':photo['sha256'],'review':'visual inspection of original photograph'} for i,photo in enumerate(photos)}
(ROOT/'assets/photo-captions.json').write_text(json.dumps(captions,ensure_ascii=False,indent=2),encoding='utf-8')
data.cache_clear()
for i,code in enumerate(plan):
    page=ROOT/'regions'/f'{code}.html'
    text=page.read_text(encoding='utf-8')
    text,count=re.subn(r'<section id="field".*?</section>',gallery_section(code),text,count=1,flags=re.S)
    assert count==1
    assert '작업 위치와 차량 설치 공간을 참고하세요.' not in text
    assert '장비 배치 참고 사진 0' not in text
    page.write_text(text,encoding='utf-8')
    if (i+1)%1000==0: print(f'{i+1}/{len(plan)} caption updates',flush=True)
print(f'Applied {len(captions)} visually reviewed titles to {len(plan)} regional galleries; repetitive text removed.',flush=True)
