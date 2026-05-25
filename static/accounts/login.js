/* ═══════════════════════════════════════════════════════════════════
   login.js — Obsidian Academy Auth
   ═══════════════════════════════════════════════════════════════════ */

const translations = {
  en: {
    "title":           "Login - Eduvia",
    "heading":         "Welcome back",
    "subheading":      "Sign in to continue your learning journey",
    "label-username":  "Username",
    "label-password":  "Password",
    "button-login":    "Sign In",
    "footer-text":     "Don't have an account?",
    "footer-link":     "Create one"
  },
  ar: {
    "title":           "تسجيل الدخول - إدوفيا",
    "heading":         "مرحباً بعودتك",
    "subheading":      "سجّل دخولك لمواصلة رحلتك التعليمية",
    "label-username":  "اسم المستخدم",
    "label-password":  "كلمة المرور",
    "button-login":    "تسجيل الدخول",
    "footer-text":     "ليس لديك حساب؟",
    "footer-link":     "أنشئ حساباً"
  }
};

let currentLang = localStorage.getItem('language') || 'en';

/* ── Theme ────────────────────────────────────────────────────────── */
function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  const icon = document.getElementById('theme-icon');
  if (icon) icon.className = theme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';
  localStorage.setItem('theme', theme);
}

function toggleDarkMode() {
  const current = document.documentElement.getAttribute('data-theme') || 'dark';
  applyTheme(current === 'dark' ? 'light' : 'dark');
}

/* ── Language ─────────────────────────────────────────────────────── */
function applyLang(lang) {
  currentLang = lang;
  const root = document.getElementById('html-root');
  root.setAttribute('lang', lang);
  root.setAttribute('dir', lang === 'ar' ? 'rtl' : 'ltr');

  document.querySelectorAll('[data-translate]').forEach(el => {
    const key = el.getAttribute('data-translate');
    if (translations[lang] && translations[lang][key]) {
      el.textContent = translations[lang][key];
    }
  });

  // Update placeholders
  const usernameInput = document.getElementById('username');
  const passwordInput = document.getElementById('password');
  if (usernameInput) usernameInput.placeholder = lang === 'ar' ? 'أدخل اسم المستخدم' : 'Enter your username';
  if (passwordInput) passwordInput.placeholder = lang === 'ar' ? 'أدخل كلمة المرور' : 'Enter your password';

  document.title = translations[lang]['title'];
  localStorage.setItem('language', lang);
}

function toggleLanguage() {
  applyLang(currentLang === 'en' ? 'ar' : 'en');
}

/* ── Password toggle ──────────────────────────────────────────────── */
function togglePassword() {
  const inp = document.getElementById('password');
  const icon = document.getElementById('pw-eye');
  if (!inp || !icon) return;
  if (inp.type === 'password') {
    inp.type = 'text';
    icon.className = 'fas fa-eye-slash';
  } else {
    inp.type = 'password';
    icon.className = 'fas fa-eye';
  }
}

/* ── Submit loading state ─────────────────────────────────────────── */
function handleSubmit(form) {
  const btn = form.querySelector('.auth-btn');
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span>';
  }
  return true;
}

/* ── DOMContentLoaded ─────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  // Theme
  const savedTheme = localStorage.getItem('theme') || 'dark';
  applyTheme(savedTheme);

  // Lang
  const savedLang = localStorage.getItem('language') || 'en';
  applyLang(savedLang);

  // Auto-focus
  const usernameInput = document.getElementById('username');
  if (usernameInput) setTimeout(() => usernameInput.focus(), 300);

  // Mark errors on inputs that have server-side errors
  document.querySelectorAll('.field-error').forEach(errEl => {
    const fieldGroup = errEl.closest('.field-group');
    if (fieldGroup) {
      const inp = fieldGroup.querySelector('.auth-input');
      if (inp) inp.classList.add('is-error');
    }
  });

  // Clear error on input
  document.querySelectorAll('.auth-input').forEach(inp => {
    inp.addEventListener('input', () => inp.classList.remove('is-error'));
  });
});