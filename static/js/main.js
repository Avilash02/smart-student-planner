/* Smart Student Planner – main.js */

// ─── Mobile sidebar toggle ───────────────────────────────────
const hamburger = document.getElementById('hamburger');
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('sidebarOverlay');

if (hamburger && sidebar && overlay) {
  hamburger.addEventListener('click', () => {
    sidebar.classList.toggle('open');
    overlay.classList.toggle('open');
  });
  overlay.addEventListener('click', () => {
    sidebar.classList.remove('open');
    overlay.classList.remove('open');
  });
}

// ─── Auto-dismiss flash messages after 4 s ───────────────────
document.querySelectorAll('.alert').forEach(el => {
  setTimeout(() => {
    el.style.transition = 'opacity .4s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 400);
  }, 4000);
});

// ─── Set date inputs' default to today if empty ──────────────
document.querySelectorAll('input[type="date"]').forEach(input => {
  if (!input.value) {
    const now = new Date();
    const yyyy = now.getFullYear();
    const mm = String(now.getMonth() + 1).padStart(2, '0');
    const dd = String(now.getDate()).padStart(2, '0');
    input.value = `${yyyy}-${mm}-${dd}`;
  }
});

// ─── Set time input default to next round hour ───────────────
document.querySelectorAll('input[type="time"]').forEach(input => {
  if (!input.value) {
    const now = new Date();
    now.setMinutes(0, 0, 0);
    now.setHours(now.getHours() + 1);
    const hh = String(now.getHours()).padStart(2, '0');
    const mm = String(now.getMinutes()).padStart(2, '0');
    input.value = `${hh}:${mm}`;
  }
});

// ─── Highlight active nav link (fallback for JS-loaded pages) ─
// Already handled server-side, but kept for SPA-style future use.

// ─── Progress bar animation on load ─────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.progress-bar-fill').forEach(bar => {
    const rawTarget = bar.getAttribute('data-pct') || bar.style.width || '';
    const cleanTarget = rawTarget.replace(/\s+/g, '');
    if (!cleanTarget || cleanTarget === '0%' || cleanTarget === '0') return;
    bar.style.width = '0%';
    requestAnimationFrame(() => {
      setTimeout(() => { bar.style.width = cleanTarget; }, 100);
    });
  });

  // ─── Auth Option Toggles (Login & Register) ────────────────
  const btnContinueEmail = document.getElementById('btnContinueEmail');
  const loginEmailSec = document.getElementById('emailAuthSection');
  const loginAuthOpts = document.getElementById('authOptions');
  const btnBackLogin = document.getElementById('btnBackToOptions');

  if (btnContinueEmail && loginEmailSec && loginAuthOpts) {
    btnContinueEmail.addEventListener('click', () => {
      loginAuthOpts.classList.add('hidden');
      loginEmailSec.classList.remove('hidden');
      const uInput = document.getElementById('id_username');
      if (uInput) uInput.focus();
    });
  }

  if (btnBackLogin && loginAuthOpts && loginEmailSec) {
    btnBackLogin.addEventListener('click', () => {
      loginEmailSec.classList.add('hidden');
      loginAuthOpts.classList.remove('hidden');
    });
  }

  const btnRegisterEmail = document.getElementById('btnRegisterEmail');
  const regEmailSec = document.getElementById('registerEmailSection');
  const regAuthOpts = document.getElementById('registerOptions');
  const btnBackReg = document.getElementById('btnBackToRegisterOptions');

  if (btnRegisterEmail && regEmailSec && regAuthOpts) {
    btnRegisterEmail.addEventListener('click', () => {
      regAuthOpts.classList.add('hidden');
      regEmailSec.classList.remove('hidden');
      const firstField = regEmailSec.querySelector('input:not([type=hidden])');
      if (firstField) firstField.focus();
    });
  }

  if (btnBackReg && regAuthOpts && regEmailSec) {
    btnBackReg.addEventListener('click', () => {
      regEmailSec.classList.add('hidden');
      regAuthOpts.classList.remove('hidden');
    });
  }

  // Auto-expand form if errors are present on page load
  const hasAuthErrors = document.querySelector('.auth-card .alert-error, .auth-card .field-error');
  if (hasAuthErrors) {
    if (loginEmailSec && loginAuthOpts) {
      loginAuthOpts.classList.add('hidden');
      loginEmailSec.classList.remove('hidden');
    }
    if (regEmailSec && regAuthOpts) {
      regAuthOpts.classList.add('hidden');
      regEmailSec.classList.remove('hidden');
    }
  }
});
