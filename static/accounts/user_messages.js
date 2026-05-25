// user_messages.js — Obsidian Academy Design System

const translations = {
    en: {
        "messages-title":    "My Messages",
        "messages-subtitle": "All your conversations in one place.",
        "messages-direct":   "Direct Chats",
        "messages-service":  "Service Chats",
        "messages-no-direct":  "No direct chats yet.",
        "messages-no-service": "No service chats yet.",
        "messages-as-buyer":    "As Buyer",
        "messages-as-provider": "As Provider",
        "nav-home": "Home", "nav-courses": "Courses", "nav-chatbot": "Chatbot",
        "nav-competitions": "Competitions", "nav-performance": "Performance",
        "nav-about": "About Us", "nav-contact": "Contact Us",
        "nav-dashboard": "Dashboard", "nav-profile": "Profile",
        "nav-logout": "Logout", "nav-coins": "Coins:", "nav-login": "Login",
        "footer-text": "© 2025 Eduvia. All rights reserved."
    },
    ar: {
        "messages-title":    "رسائلي",
        "messages-subtitle": "كل محادثاتك في مكان واحد.",
        "messages-direct":   "محادثات مباشرة",
        "messages-service":  "محادثات الخدمات",
        "messages-no-direct":  "لا توجد محادثات مباشرة بعد.",
        "messages-no-service": "لا توجد محادثات خدمات بعد.",
        "messages-as-buyer":    "كمشتري",
        "messages-as-provider": "كمقدم خدمة",
        "nav-home": "الرئيسية", "nav-courses": "الدورات", "nav-chatbot": "الدردشة الآلية",
        "nav-competitions": "المسابقات", "nav-performance": "الأداء",
        "nav-about": "معلومات عنا", "nav-contact": "تواصل معنا",
        "nav-dashboard": "لوحة التحكم", "nav-profile": "الملف الشخصي",
        "nav-logout": "تسجيل الخروج", "nav-coins": "النقاط:", "nav-login": "تسجيل الدخول",
        "footer-text": "© 2025 إدوفيا. جميع الحقوق محفوظة."
    }
};

function toggleMenu() {
    const menu = document.getElementById('main-menu');
    if (menu) menu.classList.toggle('active');
}

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
    document.title = translations[newLang]["messages-title"] + ' - Eduvia';
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
    document.title = translations[savedLang]["messages-title"] + ' - Eduvia';

    document.addEventListener('click', e => {
        const menu = document.getElementById('main-menu');
        const hamburger = document.querySelector('.hamburger');
        if (menu && hamburger && !menu.contains(e.target) && !hamburger.contains(e.target)) {
            menu.classList.remove('active');
        }
    });
});