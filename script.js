const menu = document.querySelector('.menu-toggle');
const navigation = document.querySelector('#navigation');
function closeMenu() { menu.setAttribute('aria-expanded', 'false'); menu.setAttribute('aria-label', '메뉴 열기'); navigation.classList.remove('open'); }
menu.addEventListener('click', () => {
  const open = menu.getAttribute('aria-expanded') !== 'true';
  menu.setAttribute('aria-expanded', String(open));
  menu.setAttribute('aria-label', open ? '메뉴 닫기' : '메뉴 열기');
  navigation.classList.toggle('open', open);
});
navigation.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMenu));
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeMenu(); });
const models = {
  '1': ['1톤 스카이차 · 최대 18m', 'ATOM 200NL', '좁은 진입로와 소형 간판 작업을 위한 장비입니다. 진입로 폭과 지지대 설치 공간을 확인해 주세요.'],
  '2': ['2톤 스카이차 · 최대 23m', '한신 HS250', '도심 간판과 외벽 등 다양한 고소작업을 상담합니다. 현장 주소와 작업 지점까지의 거리를 알려주세요.'],
  '3': ['3톤 스카이차 · 최대 32m', '호룡 SKY320S', '중층 건물의 외벽과 설비 작업을 위한 장비입니다. 차량 배치 공간과 작업 높이를 함께 확인합니다.'],
  '5': ['5톤 스카이차 · 최대 45m', '호룡 SKY450SQ', '높은 외벽과 대형 구조물 작업을 위한 장비입니다. 진입로와 회전 공간, 지지대 설치 공간을 사전에 확인합니다.']
};
const dialog = document.querySelector('#equipment-dialog');
dialog.setAttribute('aria-labelledby', 'detail-title');
document.querySelectorAll('[data-equipment]').forEach(button => button.addEventListener('click', () => {
  const [title, model, description] = models[button.dataset.equipment];
  document.querySelector('#detail-title').textContent = title;
  document.querySelector('#detail-model').textContent = `대표 모델: ${model}`;
  document.querySelector('#detail-description').textContent = description;
  dialog.showModal();
}));
document.querySelector('.dialog-close').addEventListener('click', () => dialog.close());
dialog.addEventListener('click', e => {
  const r = dialog.getBoundingClientRect();
  if (e.target === dialog && (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom)) dialog.close();
});
const search = document.querySelector('#region-search');
const status = document.querySelector('#region-status');
const results = document.querySelector('#region-results');
const selection = document.querySelector('#region-selection');
let regions = [];
const shortNames = { '서울특별시':'서울', '부산광역시':'부산', '대구광역시':'대구', '인천광역시':'인천', '대전광역시':'대전', '울산광역시':'울산', '세종특별자치시':'세종', '경기도':'경기', '강원특별자치도':'강원', '충청북도':'충북', '충청남도':'충남', '전북특별자치도':'전북', '전남광주통합특별시':'전남광주', '경상북도':'경북', '경상남도':'경남', '제주특별자치도':'제주' };
function renderRegions() {
  if (!regions.length) return;
  const words = search.value.trim().split(/\s+/).filter(Boolean);
  const matches = words.length ? regions.filter(r => words.every(word => (r[3] + ' ' + Object.entries(shortNames).filter(([full]) => r[3].includes(full)).map(([,short]) => short).join(' ')).includes(word))) : regions.filter(r => !r[2]);
  results.replaceChildren();
  results.classList.toggle('searching', !!words.length);
  status.textContent = words.length ? (matches.length ? `${matches.length.toLocaleString('ko-KR')}개 지역을 찾았습니다.${matches.length > 30 ? ' 상위 30개 표시 · 지역명을 더 입력해 주세요.' : ''}` : '일치하는 지역이 없습니다. 시·군·구 또는 법정동 이름으로 검색해 주세요.') : '시·도를 선택하거나 지역 이름을 검색하세요.';
  for (const row of matches.slice(0, 30)) {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = words.length ? row[3] + ' ↗' : (shortNames[row[1]] || row[1]) + ' ↗';
    button.addEventListener('click', () => {
      document.querySelector('#selected-region').textContent = row[3];
      selection.hidden = false;
      if (!words.length) { search.value = row[1]; renderRegions(); }
    });
    results.append(button);
  }
}
search.addEventListener('input', () => { selection.hidden = true; renderRegions(); });
fetch('assets/regions.json').then(response => {
  if (!response.ok) throw new Error('Region data unavailable');
  return response.json();
}).then(data => { regions = data; renderRegions(); }).catch(() => {
  status.textContent = '지역 자료를 불러오지 못했습니다. 010-4740-0482로 현장 주소를 알려주세요.';
});
