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
const search = document.querySelector('#region-search');
const status = document.querySelector('#region-status');
const results = document.querySelector('#region-results');
const selection = document.querySelector('#region-selection');
let regions = [];
let sharedRegionCodes = {};
const sharedRegionLabels = new Set();
const provinceOrder = ['1100000000', '4100000000', '2800000000', '5100000000', '3000000000', '3611000000', '4300000000', '4400000000', '5200000000', '1200000000', '2700000000', '4700000000', '2600000000', '3100000000', '4800000000', '5000000000'];
const provinceRank = new Map(provinceOrder.map((code, index) => [code, index]));
const shortNames = { '서울특별시':'서울', '부산광역시':'부산', '대구광역시':'대구', '인천광역시':'인천', '대전광역시':'대전', '울산광역시':'울산', '세종특별자치시':'세종', '경기도':'경기', '강원특별자치도':'강원', '충청북도':'충북', '충청남도':'충남', '전북특별자치도':'전북', '전남광주통합특별시':'전남광주', '경상북도':'경북', '경상남도':'경남', '제주특별자치도':'제주' };
function renderRegions() {
  if (!regions.length) return;
  const words = search.value.trim().split(/\s+/).filter(Boolean);
  const candidates = words.length ? regions.filter(r => words.every(word => (r[3] + ' ' + Object.entries(shortNames).filter(([full]) => r[3].includes(full)).map(([,short]) => short).join(' ')).includes(word))) : regions.filter(r => !r[2]).sort((a, b) => (provinceRank.get(a[0]) ?? 99) - (provinceRank.get(b[0]) ?? 99));
  const seen = new Set();
  const matches = candidates.filter(row => { const code = sharedRegionCodes[row[0]] || row[0]; if (seen.has(code)) return false; seen.add(code); return true; });
  results.replaceChildren();
  results.classList.toggle('searching', !!words.length);
  status.textContent = words.length ? (matches.length ? `${matches.length.toLocaleString('ko-KR')}개 지역을 찾았습니다.${matches.length > 30 ? ' 상위 30개 표시 · 지역명을 더 입력해 주세요.' : ''}` : '일치하는 지역이 없습니다. 시·군·구 또는 법정동 이름으로 검색해 주세요.') : '시·도를 선택하거나 지역 이름을 검색하세요.';
  for (const row of matches.slice(0, 30)) {
    const link = document.createElement('a');
    const targetCode = sharedRegionCodes[row[0]] || row[0];
    link.href = `regions/${targetCode}.html`;
    const image = document.createElement('img');
    image.src = `assets/region-thumbnails/${targetCode}.jpg?v=square-approved1`;
    image.alt = '';
    image.width = 1200;
    image.height = 1200;
    image.loading = 'lazy';
    const label = document.createElement('span');
    label.textContent = (sharedRegionLabels.has(row[1]) ? row[1] : (words.length ? row[3] : (shortNames[row[1]] || row[1]))) + ' ↗';
    link.append(image, label);
    results.append(link);
  }
}
search.addEventListener('input', () => { selection.hidden = true; renderRegions(); });
Promise.all(['assets/regions.json','assets/region-name-groups.json'].map(url => fetch(url).then(response => {
  if (!response.ok) throw new Error('Region data unavailable');
  return response.json();
}))).then(([data, shared]) => { regions = data; sharedRegionCodes = shared.by_code; shared.groups.forEach(g => sharedRegionLabels.add(g.name)); renderRegions(); }).catch(() => {
  status.textContent = '지역 자료를 불러오지 못했습니다. 010-4740-0482로 현장 주소를 알려주세요.';
});
