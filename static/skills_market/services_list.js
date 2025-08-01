const translations = {
    en: {
        "page-title": "Services List - Eduvia",
        "meta-desc": "Browse services offered by skilled students on Eduvia's Skills Market.",
        "meta-keywords": "services, student services, Eduvia, skills market, freelance",
        "og-title": "Services List - Eduvia",
        "og-desc": "Browse services offered by skilled students on Eduvia's Skills Market.",
        "hero-title": "Skills Market",
        "hero-desc": "Explore and offer micro-services in Eduvia's Skills Market, connecting students with opportunities",
        "card-provider": "Provider:",
        "card-skill": "Skill:",
        "card-price": "Price:",
        "card-coins": "Coins",
        "card-delivery": "Delivery:",
        "card-day": "Day",
        "card-order": "Order Now",
        "cards-empty": "No services available.",
        "btn-skills": "View Skills",
        "btn-add-service": "Add Service",
        "btn-add-opportunity": "Add Opportunity",
        "btn-opportunities": "View Opportunities",
        "nav-home": "Home",
        "nav-courses": "Courses",
        "nav-chatbot": "Chatbot",
        "nav-competitions": "Competitions",
        "nav-performance": "Performance",
        "nav-about": "About Us",
        "nav-contact": "Contact Us",
        "nav-dashboard": "Dashboard",
        "nav-profile": "Profile",
        "nav-logout": "Logout",
        "nav-coins": "Coins:",
        "nav-login": "Login",
        "footer-text": "© 2025 Eduvia. All rights reserved.",
        "search-placeholder": "Search for services...",
        "search-button": "Search"
    },
    ar: {
        "page-title": "قائمة الخدمات - إدوفيا",
        "meta-desc": "تصفح الخدمات التي يقدمها الطلاب المهرة في سوق المهارات بإدوفيا.",
        "meta-keywords": "خدمات, خدمات الطلاب, إدوفيا, سوق المهارات, عمل حر",
        "og-title": "قائمة الخدمات - إدوفيا",
        "og-desc": "تصفح الخدمات التي يقدمها الطلاب المهرة في سوق المهارات بإدوفيا.",
        "hero-title": "سوق المهارات",
        "hero-desc": "استكشف وعرض الخدمات المصغرة في سوق المهارات بإدوفيا، واربط الطلاب بالفرص",
        "card-provider": "المزود:",
        "card-skill": "المهارة:",
        "card-price": "السعر:",
        "card-coins": "نقاط",
        "card-delivery": "التسليم:",
        "card-day": "يوم",
        "card-order": "اطلب الآن",
        "cards-empty": "لا توجد خدمات متاحة.",
        "btn-skills": "عرض المهارات",
        "btn-add-service": "إضافة خدمة",
        "btn-add-opportunity": "إضافة فرصة",
        "btn-opportunities": "عرض الفرص",
        "nav-home": "الرئيسية",
        "nav-courses": "الدورات",
        "nav-chatbot": "الدردشة الآلية",
        "nav-competitions": "المسابقات",
        "nav-performance": "الأداء",
        "nav-about": "معلومات عنا",
        "nav-contact": "تواصل معنا",
        "nav-dashboard": "لوحة التحكم",
        "nav-profile": "الملف الشخصي",
        "nav-logout": "تسجيل الخروج",
        "nav-coins": "النقاط:",
        "nav-login": "تسجيل الدخول",
        "footer-text": "© 2025 إدوفيا. جميع الحقوق محفوظة.",
        "search-placeholder": "ابحث عن الخدمات...",
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