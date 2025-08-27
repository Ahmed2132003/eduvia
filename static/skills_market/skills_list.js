const translations = {
    en: {
        "page-title": "Skills List - Eduvia",
        "meta-desc": "Discover a wide range of skills offered by students on Eduvia's Skills Market.",
        "meta-keywords": "skills, student skills, Eduvia, skills market, freelance",
        "og-title": "Skills List - Eduvia",
        "og-desc": "Discover a wide range of skills offered by students on Eduvia's Skills Market.",
        "hero-title": "Explore Skills on Eduvia",
        "hero-desc": "Discover a variety of skills offered by our community",
        "card-provider": "Provider:",
        "card-level": "Level:",
        "card-description": "Description:",
        "card-services": "View Services",
        "cards-empty": "No skills available.",
        "btn-services": "View Services",
        "btn-add-skill": "Add Skill",
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
        "footer-text": "© 2025 Eduvia and creativitycode. All rights reserved.",
        "search-placeholder": "Search for skills...",
        "search-button": "Search"
    },
    ar: {
        "page-title": "قائمة المهارات - إدوفيا",
        "meta-desc": "اكتشف مجموعة واسعة من المهارات التي يقدمها الطلاب في سوق المهارات بإدوفيا.",
        "meta-keywords": "مهارات, مهارات الطلاب, إدوفيا, سوق المهارات, عمل حر",
        "og-title": "قائمة المهارات - إدوفيا",
        "og-desc": "اكتشف مجموعة واسعة من المهارات التي يقدمها الطلاب في سوق المهارات بإدوفيا.",
        "hero-title": "استكشف المهارات على إدوفيا",
        "hero-desc": "اكتشف مجموعة متنوعة من المهارات التي يقدمها مجتمعنا",
        "card-provider": "المزود:",
        "card-level": "المستوى:",
        "card-description": "الوصف:",
        "card-services": "عرض الخدمات",
        "cards-empty": "لا توجد مهارات متاحة.",
        "btn-services": "عرض الخدمات",
        "btn-add-skill": "إضافة مهارة",
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
        "footer-text": "© 2025 إدوفيا و كريتيفيتي كود . جميع الحقوق محفوظة.",
        "search-placeholder": "ابحث عن المهارات...",
        "search-button": "بحث"
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

    document.querySelectorAll('input[placeholder][data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        element.setAttribute('placeholder', translations[newLang][key]);
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

    document.querySelectorAll('input[placeholder][data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        element.setAttribute('placeholder', translations[savedLang][key]);
    });

    document.title = translations[savedLang]["page-title"];
});