const toggle = document.querySelector('.menu-toggle');
const nav = document.querySelector('#navigation');
for (const link of nav.querySelectorAll('a')) {
  const target = link.hash.slice(1);
  if (target && document.getElementById(target)) link.setAttribute('href', `#${target}`);
}
function closeNavigation() {
  nav.classList.remove('open');
  toggle.setAttribute('aria-expanded', 'false');
  toggle.setAttribute('aria-label', '메뉴 열기');
}
toggle.addEventListener('click', () => {
  const open = toggle.getAttribute('aria-expanded') !== 'true';
  toggle.setAttribute('aria-expanded', String(open));
  toggle.setAttribute('aria-label', open ? '메뉴 닫기' : '메뉴 열기');
  nav.classList.toggle('open', open);
});
nav.querySelectorAll('a').forEach(a => a.addEventListener('click', closeNavigation));
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeNavigation(); });
