(function(){
  const root = document.documentElement;
  const themeToggle = document.getElementById('themeToggle');
  const mobileToggle = document.getElementById('mobileNavToggle');
  const mobileNav = document.getElementById('mobileNav');
  const year = document.getElementById('year');

  // Year in footer
  if (year) year.textContent = new Date().getFullYear().toString();

  // Theme persistence
  const getPref = () => localStorage.getItem('tf-theme') || 'dark';
  const setTheme = (t) => { document.documentElement.setAttribute('data-theme', t); localStorage.setItem('tf-theme', t); };
  setTheme(getPref());
  if (themeToggle) themeToggle.addEventListener('click', () => setTheme(getPref()==='dark' ? 'light' : 'dark'));

  // Mobile nav
  if (mobileToggle && mobileNav) {
    mobileToggle.addEventListener('click', () => {
      const open = mobileNav.style.display === 'block';
      mobileNav.style.display = open ? 'none' : 'block';
      mobileToggle.setAttribute('aria-expanded', String(!open));
    });
  }

  // Utility: simple debounce
  window.tfDebounce = function(fn, ms){
    let t; return (...args) => { clearTimeout(t); t = setTimeout(() => fn.apply(null, args), ms); };
  };
})();
