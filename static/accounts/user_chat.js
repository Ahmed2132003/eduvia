// user_chat.js — Obsidian Academy Design System
// Logic preserved from original; theme/lang aligned with lesson_view pattern

const translations = {
    en: {
        "chat-title":    "Chat with {{ other_user.username }} - Eduvia",
        "chat-empty":    "No messages yet. Start the conversation!",
        "chat-send":     "Send",
        "chat-status":   "Online",
        "chat-badge":    "Eduvia",
        "chat-download": "Download File",
        "nav-home": "Home", "nav-courses": "Courses", "nav-chatbot": "Chatbot",
        "nav-competitions": "Competitions", "nav-performance": "Performance",
        "nav-about": "About Us", "nav-contact": "Contact Us",
        "nav-dashboard": "Dashboard", "nav-profile": "Profile",
        "nav-logout": "Logout", "nav-coins": "Coins:", "nav-login": "Login",
        "footer-text": "© 2025 Eduvia. All rights reserved."
    },
    ar: {
        "chat-title":    "الدردشة مع {{ other_user.username }} - إدوفيا",
        "chat-empty":    "لا توجد رسائل بعد. ابدأ المحادثة!",
        "chat-send":     "إرسال",
        "chat-status":   "متصل",
        "chat-badge":    "إدوفيا",
        "chat-download": "تحميل الملف",
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
    const username = document.querySelector('.chat-header-name')?.textContent || '';
    if (translations[newLang]["chat-title"])
        document.title = translations[newLang]["chat-title"].replace("{{ other_user.username }}", username);
    // Update textarea placeholder
    const textarea = document.querySelector('.chat-textarea');
    if (textarea) textarea.placeholder = newLang === 'ar' ? 'اكتب رسالتك...' : 'Type a message...';
    localStorage.setItem('language', newLang);
}

function showFilePreview(input) {
    const preview = document.getElementById('file-preview');
    const display = document.getElementById('file-name-display');
    if (input.files && input.files[0] && preview && display) {
        display.textContent = input.files[0].name;
        preview.style.display = 'flex';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Theme
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    const themeIcon = document.querySelector('.dark-mode-toggle i');
    if (themeIcon) themeIcon.className = savedTheme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';

    // Language
    const savedLang = localStorage.getItem('language') || 'en';
    const root = document.getElementById('html-root');
    root.setAttribute('lang', savedLang);
    root.setAttribute('dir', savedLang === 'ar' ? 'rtl' : 'ltr');
    document.querySelectorAll('[data-translate]').forEach(el => {
        const key = el.getAttribute('data-translate');
        if (translations[savedLang] && translations[savedLang][key]) el.textContent = translations[savedLang][key];
    });

    // Scroll to bottom
    const msgList = document.getElementById('message-list');
    if (msgList) msgList.scrollTop = msgList.scrollHeight;

    // Textarea: style + auto-resize + Enter to send
    const textarea = document.querySelector('textarea[name="content"]');
    if (textarea) {
        textarea.classList.add('chat-textarea');
        textarea.placeholder = savedLang === 'ar' ? 'اكتب رسالتك...' : 'Type a message...';
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 140) + 'px';
        });
        textarea.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                const form = document.getElementById('chat-form');
                if (form) form.submit();
            }
        });
    }

    // Close menu on outside click
    document.addEventListener('click', e => {
        const menu = document.getElementById('main-menu');
        const hamburger = document.querySelector('.hamburger');
        if (menu && hamburger && !menu.contains(e.target) && !hamburger.contains(e.target)) {
            menu.classList.remove('active');
        }
    });
});