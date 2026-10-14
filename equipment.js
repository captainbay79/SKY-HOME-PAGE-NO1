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
