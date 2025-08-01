const translations = {
    en: {
        "page-title": "Order Service - Eduvia",
        "meta-desc": "Order a service from Eduvia's Skills Market.",
        "meta-keywords": "order service, Eduvia, skills market",
        "og-title": "Order Service - Eduvia",
        "og-desc": "Order a service from Eduvia's Skills Market.",
        "hero-title": "Order a Service",
        "hero-desc": "Place your order for a service from Eduvia's Skills Market",
        "card-provider": "Provider:",
        "card-skill": "Skill:",
        "card-price": "Price:",
        "card-coins": "Coins",
        "card-delivery": "Delivery:",
        "card-day": "Day",
        "card-days": "Days",
        "card-description": "Description:",
        "form-details-label": "Order Details:",
        "form-submit": "Place Order",
        "btn-back-services": "Back to Services",
        "btn-view-skills": "View Skills",
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
        "page-title": "طلب خدمة - إدوفيا",
        "meta-desc": "اطلب خدمة من سوق المهارات بإدوفيا.",
        "meta-keywords": "طلب خدمة, إدوفيا, سوق المهارات",
        "og-title": "طلب خدمة - إدوفيا",
        "og-desc": "اطلب خدمة من سوق المهارات بإدوفيا.",
        "hero-title": "طلب خدمة",
        "hero-desc": "قم بطلب خدمتك من سوق المهارات بإدوفيا",
        "card-provider": "المزود:",
        "card-skill": "المهارة:",
        "card-price": "السعر:",
        "card-coins": "نقاط",
        "card-delivery": "التسليم:",
        "card-day": "يوم",
        "card-days": "أيام",
        "card-description": "الوصف:",
        "form-details-label": "تفاصيل الطلب:",
        "form-submit": "تقديم الطلب",
        "btn-back-services": "العودة إلى الخدمات",
        "btn-view-skills": "عرض المهارات",
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