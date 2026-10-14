# 지역별 페이지와 검색 준비

지역 자료의 5,351개 항목별로 `regions/{지역코드}.html`과 `assets/region-thumbnails/{지역코드}.jpg`를 생성합니다. 전체 지역 탐색은 `regions/index.html`입니다. 메인의 지역 검색도 각 상세페이지로 연결됩니다.

## 적용 내용

- 페이지별 title, description, H1, OG 이미지와 언어 정보
- JavaScript 실행 없이 읽을 수 있는 본문과 상위·하위 지역 링크
- WebPage, Service, Organization, BreadcrumbList JSON-LD
- 지역명, 전화번호, 장비 문의 범위, 견적 조건을 설명하는 본문
- 실제 작업 사진의 대체 텍스트, 크기, 지연 로딩과 웹용 압축
- 사용자가 확인할 수 있는 상담 질문과 답변
- 모바일 메뉴, 고정 전화 상담 버튼, 썸네일 다운로드

FAQ는 읽기 쉬운 답변 콘텐츠로 제공합니다. Google 검색의 FAQ 리치 결과 표시를 약속하거나 이를 전제로 FAQPage 스키마를 넣지 않았습니다. 사업장 주소가 확인되지 않아 주소나 좌표가 필요한 LocalBusiness 정보와 가짜 지점은 추가하지 않았습니다. 촬영 지역이 확인되지 않은 사진을 지역별 시공 실적으로 쓰지 않습니다.

## 검색 색인 범위

하위 지역 목록이 있는 지역 탐색 페이지는 `index,follow`입니다. 지역 고유 현장 정보 없이 상담 템플릿만 있는 마지막 단위 페이지는 `noindex,follow`입니다. 페이지와 썸네일은 모두 존재하고 고객이 접근할 수 있지만, 내용이 비슷한 수천 개의 페이지를 검색엔진에 일괄 제출하지 않습니다.

마지막 단위 페이지의 검색 색인을 열기 전에는 확인된 지역별 작업 사례, 지역과 연결된 사진, 실제 진입·설치 조건 등 고객에게 유용한 고유 내용을 추가하고 생성기를 확장해야 합니다. 제공된 지역 JSON을 그대로 사용했으며 현행 행정구역·법정동 자료와 별도 대조하지 않았습니다.

## 재생성

저장소 루트에서 Pillow가 설치된 Python으로 실행합니다.

```powershell
python tools/build_regions.py
python tools/update_home.py
python tools/verify_regions.py
```

원본 폴더: `C:/Users/Over kim/Documents/홈페이지 제작용 이미지/광고기획 작업사진/`

원본은 수정하지 않습니다. 현장 갤러리의 선정 사진 12장은 `assets/regional-photo-catalog.json`에, 썸네일 배경 원본 471장은 `assets/thumbnail-photo-catalog.json`에 기록하며 SHA-256을 보관합니다. 페이지·썸네일·배경 사진 매핑은 `assets/region-pages.json`에 있습니다.

최종 승인한 시안을 바탕으로 지역명·우리동네 스카이차·전화번호를 표시합니다. 지역명은 기존 크기의 주황색 박스 안에서 한 줄로 표시하며, 조금 더 굵게 만든 흰색 글씨에 검정 테두리와 그림자를 넣었습니다. 우리동네·스카이차·전화번호에도 검정 테두리를 적용했고 전화 아이콘의 그림자도 유지합니다. 썸네일은 800×600의 4:3 JPG입니다. 각 페이지 상단의 썸네일을 누르면 전화 상담으로 연결됩니다. 목록과 메인 검색에도 같은 썸네일을 사용합니다.

썸네일을 제외한 홈페이지 작업사진에는 승인한 C 반복형 워터마크를 불투명도 15%로 적용했습니다. 상호 `키다리스카이차`를 대각선으로 반복 표시합니다. `assets/watermarked/`의 별도 파일을 페이지에서 사용하고 원본 및 썸네일 배경용 파일은 보존합니다. 대상·원본 매핑은 `assets/watermark-catalog.json`에 기록합니다. 재생성 시에도 같은 워터마크가 적용됩니다.

배경은 직접 제공된 원본 사진 471장을 순환 배치합니다. 같은 상위 지역에 속한 지역 목록에서는 원본 SHA-256이 서로 다른 사진을 사용합니다. 전체 페이지 수가 원본 수보다 많아 다른 지역 목록에서는 사진이 재사용됩니다. 장비를 새로 생성하거나 사진 속 개별 장비를 이동하지 않고, 사진 전체를 비례 확대·크롭하여 전화번호 띠 위 영역에 맞춥니다. 갤러리에는 글자를 얹지 않은 실제 현장 사진을 유지합니다.

## 공개 도메인을 정한 뒤

```powershell
python tools/build_regions.py --base-url https://확정한-도메인
python tools/verify_regions.py
```

확정한 HTTPS 도메인을 전달하면 지역 페이지의 canonical, og:url, 절대 이미지 URL, 구조화 데이터 URL과 색인 대상만 포함하는 sitemap.xml을 생성합니다. robots.txt에도 sitemap을 연결합니다. 메인페이지의 canonical과 OG URL은 동일한 실제 도메인으로 추가해야 합니다. 현재는 localhost 개발이므로 가짜 도메인을 넣지 않았습니다.

공개 후 사업자 정보와 지역 자료를 확인하고 Google Search Console 및 네이버 서치어드바이저에서 사이트를 등록·검증합니다. 이 로컬 작업에서는 검색엔진 제출이나 배포를 수행하지 않았습니다.

## 참고한 공식 자료

- [Google: 생성형 AI 검색 기능에 맞춘 웹사이트 최적화](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
- [Google: 생성형 AI 콘텐츠 지침](https://developers.google.com/search/docs/fundamentals/using-gen-ai-content)
- [Google: LocalBusiness 구조화 데이터](https://developers.google.com/search/docs/appearance/structured-data/local-business)

GEO와 AEO도 유용하고 사실에 근거한 콘텐츠, 읽을 수 있는 페이지 구조, 이미지와 검색 기본 요건을 중심으로 적용했습니다. 전용 AI 파일이나 문구를 넣는 것만으로 검색·AI 답변에 노출된다고 설명하지 않습니다.
