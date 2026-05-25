// verify_code.js — Obsidian Academy Design System

const translations = {
    en: {
        "title":                  "Verify Your Account - Eduvia",
        "heading":                "Verify Your Account",
        "subheading":             "Enter the verification code sent to your email.",
        "button-verify":          "Verify Code",
        "footer-text":            "Didn't receive a code?",
        "footer-link":            "Try again",
        "label-verification_code":"Enter Verification Code",
        "security-note":          "Your code is valid for 10 minutes. Do not share it with anyone.",
        "footer-copyright":       "© 2025 Eduvia. All rights reserved."
    },
    ar: {
        "title":                  "تحقق من حسابك - إدوفيا",
        "heading":                "تحقق من حسابك",
        "subheading":             "أدخل رمز التحقق المرسل إلى بريدك الإلكتروني.",
        "button-verify":          "تحقق من الرمز",
        "footer-text":            "لم تتلق رمزًا؟",
        "footer-link":            "حاول مرة أخرى",
        "label-verification_code":"أدخل رمز التحقق",
        "security-note":          "رمزك صالح لمدة 10 دقائق. لا تشاركه مع أحد.",
        "footer-copyright":       "© 2025 إدوفيا. جميع الحقوق محفوظة."
    }
};

function toggleDarkMode() {
    const current = document.documentElement.getAttribute('data-theme');
    const newTheme = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    const icon = document.querySelector('.dark-mode-toggle i');
    if (icon) icon.className = newTheme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';
    localStorage.setItem('theme', newTheme);
}

function toggleLanguage() {
    const root = document.getElementById('html-root');
    const currentLang = root.getAttribute('lang');
    const newLang = currentLang === 'en' ? 'ar' : 'en';
    root.setAttribute('lang', newLang);
    root.setAttribute('dir', newLang === 'ar' ? 'rtl' : 'ltr');
    document.querySelectorAll('[data-translate]').forEach(el => {
        const key = el.getAttribute('data-translate');
        if (translations[newLang] && translations[newLang][key]) el.textContent = translations[newLang][key];
    });
    document.title = translations[newLang]["title"];
    const input = document.getElementById('verification_code');
    if (input) input.placeholder = newLang === 'ar' ? '· · · · · ·' : '· · · · · ·';
    localStorage.setItem('language', newLang);
}

document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    const themeIcon = document.querySelector('.dark-mode-toggle i');
    if (themeIcon) themeIcon.className = savedTheme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';

    const savedLang = localStorage.getItem('language') || 'en';
    const root = document.getElementById('html-root');
    root.setAttribute('lang', savedLang);
    root.setAttribute('dir', savedLang === 'ar' ? 'rtl' : 'ltr');
    document.querySelectorAll('[data-translate]').forEach(el => {
        const key = el.getAttribute('data-translate');
        if (translations[savedLang] && translations[savedLang][key]) el.textContent = translations[savedLang][key];
    });
    document.title = translations[savedLang]["title"];

    // Submit loading state
    const form = document.getElementById('verify-form');
    if (form) {
        form.addEventListener('submit', function() {
            const btn = document.getElementById('verify-btn');
            if (btn) {
                btn.innerHTML = '<span style="width:16px;height:16px;border:2px solid transparent;border-top-color:#fff;border-radius:50%;animation:btnSpin .7s linear infinite;display:inline-block;"></span>';
                btn.disabled = true;
            }
        });
    }
});