/* ═══════════════════════════════════════════════════════════════════
   register.js — Obsidian Academy Auth
   ═══════════════════════════════════════════════════════════════════ */

const translations = {
  en: {
    "title":          "Register - Eduvia",
    "heading":        "Create your account",
    "subheading":     "Join Eduvia and start your learning journey today",
    "button-register":"Create Account",
    "footer-text":    "Already have an account?",
    "footer-link":    "Sign in",
    "label-username":  "Username",
    "label-email":     "Email address",
    "label-password1": "Password",
    "label-password2": "Confirm password",
    "label-role":      "Role"
  },
  ar: {
    "title":          "التسجيل - إدوفيا",
    "heading":        "أنشئ حسابك",
    "subheading":     "انضم إلى إدوفيا وابدأ رحلتك التعليمية اليوم",
    "button-register":"إنشاء حساب",
    "footer-text":    "لديك حساب بالفعل؟",
    "footer-link":    "تسجيل الدخول",
    "label-username":  "اسم المستخدم",
    "label-email":     "البريد الإلكتروني",
    "label-password1": "كلمة المرور",
    "label-password2": "تأكيد كلمة المرور",
    "label-role":      "الدور"
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

  // Translate Django-rendered labels
  document.querySelectorAll('form p label').forEach(label => {
    const forAttr = label.getAttribute('for');
    if (forAttr) {
      const key = 'label-' + forAttr.replace(/^id_/, '').toLowerCase();
      if (translations[lang][key]) {
        label.textContent = translations[lang][key];
      }
    }
  });

  document.title = translations[lang]['title'];
  localStorage.setItem('language', lang);
}

function toggleLanguage() {
  applyLang(currentLang === 'en' ? 'ar' : 'en');
}

/* ── Password toggles ─────────────────────────────────────────────── */
function togglePassword(inputId, iconId) {
  const inp = document.getElementById(inputId);
  const icon = document.getElementById(iconId);
  if (!inp || !icon) return;
  if (inp.type === 'password') {
    inp.type = 'text';
    icon.className = 'fas fa-eye-slash';
  } else {
    inp.type = 'password';
    icon.className = 'fas fa-eye';
  }
}

/* ── Password strength ────────────────────────────────────────────── */
function checkPasswordStrength(pw) {
  const bar = document.getElementById('pw-strength-bar');
  const lbl = document.getElementById('pw-strength-lbl');
  if (!bar || !lbl) return;
  let score = 0;
  if (pw.length >= 8) score++;
  if (/[A-Z]/.test(pw)) score++;
  if (/[0-9]/.test(pw)) score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;
  const levels = [
    { label: '', color: 'transparent', width: '0%' },
    { label: currentLang === 'ar' ? 'ضعيف' : 'Weak',   color: '#fb7185', width: '25%' },
    { label: currentLang === 'ar' ? 'مقبول' : 'Fair',   color: '#fbbf24', width: '50%' },
    { label: currentLang === 'ar' ? 'جيد'   : 'Good',   color: '#38bdf8', width: '75%' },
    { label: currentLang === 'ar' ? 'قوي'   : 'Strong', color: '#34d399', width: '100%' }
  ];
  const lvl = levels[score] || levels[0];
  bar.style.width = lvl.width;
  bar.style.background = lvl.color;
  lbl.textContent = lvl.label;
  lbl.style.color = lvl.color;
}

/* ── Submit loading ───────────────────────────────────────────────── */
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
  applyTheme(localStorage.getItem('theme') || 'dark');
  // Lang
  applyLang(localStorage.getItem('language') || 'en');

  // Style Django-generated inputs
  document.querySelectorAll('form input, form select').forEach(inp => {
    inp.classList.add('auth-input');
    // Wrap with input-wrap if not already wrapped
    if (!inp.closest('.input-wrap') && inp.type !== 'hidden' && inp.type !== 'checkbox') {
      const wrap = document.createElement('div');
      wrap.className = 'input-wrap';
      inp.parentNode.insertBefore(wrap, inp);
      wrap.appendChild(inp);
    }
  });

  // Style error lists from Django
  document.querySelectorAll('ul.errorlist, .errorlist').forEach(ul => {
    ul.querySelectorAll('li').forEach(li => {
      const err = document.createElement('div');
      err.className = 'field-error';
      err.textContent = li.textContent;
      ul.parentNode.insertBefore(err, ul);
    });
    ul.remove();
  });

  // Password strength watcher
  const pw1 = document.getElementById('id_password1');
  if (pw1) {
    pw1.addEventListener('input', () => checkPasswordStrength(pw1.value));
  }

  // Error inputs
  document.querySelectorAll('.field-error').forEach(errEl => {
    const group = errEl.closest('.field-group') || errEl.parentElement;
    if (group) {
      const inp = group.querySelector('.auth-input');
      if (inp) inp.classList.add('is-error');
    }
  });

  document.querySelectorAll('.auth-input').forEach(inp => {
    inp.addEventListener('input', () => inp.classList.remove('is-error'));
  });
});