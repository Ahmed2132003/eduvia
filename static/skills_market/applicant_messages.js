const translations = {
    en: {
        "page-title": "My Messages - Eduvia",
        "meta-desc": "View your messages in Eduvia's Skills Market.",
        "meta-keywords": "my messages, Eduvia, skills market",
        "og-title": "My Messages - Eduvia",
        "og-desc": "View your messages in Eduvia's Skills Market.",
        "hero-title": "My Messages",
        "hero-desc": "View and manage your messages in Eduvia's Skills Market",
        "messages-title": "My Messages",
        "order-service": "Chat with",
        "order-service-title": "Order:",
        "order-opportunity": "Chat with",
        "order-opportunity-title": "Opportunity:",
        "order-status": "Status:",
        "order-created": "Created At:",
        "no-messages": "No messages yet.",
        "back-to-services": "Back to Services",
        "back-to-messages": "Back to Messages",
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
        "footer-text": "© 2025 Eduvia and creativitycode. All rights reserved."
    },
    ar: {
        "page-title": "رسائلي - إدوفيا",
        "meta-desc": "عرض رسائلك في سوق المهارات بإدوفيا.",
        "meta-keywords": "رسائلي, إدوفيا, سوق المهارات",
        "og-title": "رسائلي - إدوفيا",
        "og-desc": "عرض رسائلك في سوق المهارات بإدوفيا.",
        "hero-title": "رسائلي",
        "hero-desc": "عرض وإدارة رسائلك في سوق المهارات بإدوفيا",
        "messages-title": "رسائلي",
        "order-service": "دردشة مع",
        "order-service-title": "الطلب:",
        "order-opportunity": "دردشة مع",
        "order-opportunity-title": "الفرصة:",
        "order-status": "الحالة:",
        "order-created": "تاريخ الإنشاء:",
        "no-messages": "لا توجد رسائل بعد.",
        "back-to-services": "العودة إلى الخدمات",
        "back-to-messages": "العودة إلى الرسائل",
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
        "footer-text": "© 2025 إدوفيا و كريتيفيتي كود . جميع الحقوق محفوظة."
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