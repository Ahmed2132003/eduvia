const translations = {
    en: {
        "page-title": "Opportunity Applications - Eduvia",
        "meta-desc": "View and manage applications for opportunities in Eduvia's Skills Market.",
        "meta-keywords": "opportunity applications, Eduvia, skills market",
        "og-title": "Opportunity Applications - Eduvia",
        "og-desc": "View and manage applications for opportunities in Eduvia's Skills Market.",
        "hero-title": "Opportunity Applications",
        "hero-desc": "Manage applications submitted for your opportunities in Eduvia's Skills Market",
        "applications-title": "Applications",
        "app-name": "Name:",
        "app-phone": "Phone:",
        "app-cv": "CV:",
        "app-status": "Status:",
        "app-accept": "Accept",
        "no-applications": "No applications available.",
        "btn-back-opportunities": "Back to Opportunities",
        "btn-back-services": "Back to Services",
        "nav-home": "Home",
        "nav-courses": "Courses",
        "nav-chatbot": "Chatbot",
        "nav-competitions": "Competitions",
        "nav-performance": "Performance",
        "nav-skills-market": "Skills Market",
        "nav-about": "About Us",
        "nav-contact": "Contact Us",
        "nav-dashboard": "Dashboard",
        "nav-profile": "Profile",
        "nav-logout": "Logout",
        "nav-coins": "Coins:",
        "nav-login": "Login",
        "footer-text": "© 2025 Eduvia. All rights reserved."
    },
    ar: {
        "page-title": "طلبات الفرص - إدوفيا",
        "meta-desc": "عرض وإدارة الطلبات المقدمة للفرص في سوق المهارات بإدوفيا.",
        "meta-keywords": "طلبات الفرص, إدوفيا, سوق المهارات",
        "og-title": "طلبات الفرص - إدوفيا",
        "og-desc": "عرض وإدارة الطلبات المقدمة للفرص في سوق المهارات بإدوفيا.",
        "hero-title": "طلبات الفرص",
        "hero-desc": "إدارة الطلبات المقدمة لفرصك في سوق المهارات بإدوفيا",
        "applications-title": "الطلبات",
        "app-name": "الاسم:",
        "app-phone": "الهاتف:",
        "app-cv": "السيرة الذاتية:",
        "app-status": "الحالة:",
        "app-accept": "قبول",
        "no-applications": "لا توجد طلبات متاحة.",
        "btn-back-opportunities": "العودة إلى الفرص",
        "btn-back-services": "العودة إلى الخدمات",
        "nav-home": "الرئيسية",
        "nav-courses": "الدورات",
        "nav-chatbot": "الدردشة الآلية",
        "nav-competitions": "المسابقات",
        "nav-performance": "الأداء",
        "nav-skills-market": "سوق المهارات",
        "nav-about": "معلومات عنا",
        "nav-contact": "تواصل معنا",
        "nav-dashboard": "لوحة التحكم",
        "nav-profile": "الملف الشخصي",
        "nav-logout": "تسجيل الخروج",
        "nav-coins": "النقاط:",
        "nav-login": "تسجيل الدخول",
        "footer-text": "© 2025 إدوفيا. جميع الحقوق محفوظة."
    }
};

function toggleMenu() {
    const menu = document.querySelector('.menu');
    menu.classList.toggle('active');
}

function toggleDarkMode() {
    const body = document.body;
    const toggleIcon = document.querySelector('.dark-mode-toggle i');
    body.classList.toggle('dark-mode');
    if (body.classList.contains('dark-mode')) {
        toggleIcon.classList.remove('fa-moon');
        toggleIcon.classList.add('fa-sun');
        localStorage.setItem('theme', 'dark');
    } else {
        toggleIcon.classList.remove('fa-sun');
        toggleIcon.classList.add('fa-moon');
        localStorage.setItem('theme', 'light');
    }
}

function toggleLanguage() {
    const htmlRoot = document.getElementById('html-root');
    const currentLang = htmlRoot.getAttribute('lang');
    const newLang = currentLang === 'en' ? 'ar' : 'en';
    htmlRoot.setAttribute('lang', newLang);
    htmlRoot.setAttribute('dir', newLang === 'ar' ? 'rtl' : 'ltr');
    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        let text = translations[newLang][key];
        if (element.tagName.toLowerCase() === 'meta') {
            if (element.getAttribute('name') === 'description' || element.getAttribute('name') === 'keywords') {
                element.setAttribute('content', text);
            } else if (element.getAttribute('property')?.startsWith('og:')) {
                element.setAttribute('content', text);
            }
        } else {
            element.textContent = text;
        }
    });
    document.title = translations[newLang]["page-title"];
    localStorage.setItem('language', newLang);
}

document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme');
    const toggleIcon = document.querySelector('.dark-mode-toggle i');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        toggleIcon.classList.remove('fa-moon');
        toggleIcon.classList.add('fa-sun');
    }

    const savedLang = localStorage.getItem('language') || 'en';
    const htmlRoot = document.getElementById('html-root');
    htmlRoot.setAttribute('lang', savedLang);
    htmlRoot.setAttribute('dir', savedLang === 'ar' ? 'rtl' : 'ltr');
    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        let text = translations[savedLang][key];
        if (element.tagName.toLowerCase() === 'meta') {
            if (element.getAttribute('name') === 'description' || element.getAttribute('name') === 'keywords') {
                element.setAttribute('content', text);
            } else if (element.getAttribute('property')?.startsWith('og:')) {
                element.setAttribute('content', text);
            }
        } else {
            element.textContent = text;
        }
    });
    document.title = translations[savedLang]["page-title"];
});