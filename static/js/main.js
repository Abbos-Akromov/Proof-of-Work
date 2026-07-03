// ─── Theme toggle ────────────────────────────────────────────────────────────
const html = document.documentElement;
const themeBtn = document.getElementById('themeToggle');

const saved = localStorage.getItem('pow-theme') || 'dark';
html.setAttribute('data-theme', saved);

if (themeBtn) {
  themeBtn.addEventListener('click', () => {
    const current = html.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('pow-theme', next);
  });
}

// ─── Mobile nav ──────────────────────────────────────────────────────────────
const burger = document.getElementById('navBurger');
const navLinks = document.querySelector('.nav-links');

if (burger && navLinks) {
  burger.addEventListener('click', () => {
    navLinks.classList.toggle('open');
  });
  document.addEventListener('click', (e) => {
    if (!burger.contains(e.target) && !navLinks.contains(e.target)) {
      navLinks.classList.remove('open');
    }
  });
}

// ─── Auto-dismiss messages ───────────────────────────────────────────────────
document.querySelectorAll('.message').forEach(msg => {
  setTimeout(() => {
    msg.style.transition = 'opacity 0.4s';
    msg.style.opacity = '0';
    setTimeout(() => msg.remove(), 400);
  }, 4000);
});

// ─── Smooth scroll for anchor links ─────────────────────────────────────────
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});
