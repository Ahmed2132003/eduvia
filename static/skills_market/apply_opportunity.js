const translations = {
    en: {
        "page-title": "Apply for Opportunity - Eduvia",
        "meta-desc": "Apply for opportunities in Eduvia's Skills Market.",
        "meta-keywords": "apply opportunity, Eduvia, skills market",
        "og-title": "Apply for Opportunity - Eduvia",
        "og-desc": "Apply for opportunities in Eduvia's Skills Market.",
        "hero-title": "Apply for {{ opportunity.title }}",
        "hero-desc": "Submit your application for this opportunity in Eduvia's Skills Market",
        "form-title": "Apply for {{ opportunity.title }}",
        "submit-btn": "Submit Application",
        "back-to-opportunities": "Back to Opportunities",
        "back-to-services": "Back to Services",
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
        "page-title": "التسجيل لفرصة - إدوفيا",
        "meta-desc": "تقديم طلب للفرص في سوق المهارات بإدوفيا.",
        "meta-keywords": "التسجيل لفرصة, إدوفيا, سوق المهارات",
        "og-title": "التسجيل لفرصة - إدوفيا",
        "og-desc": "تقديم طلب للفرص في سوق المهارات بإدوفيا.",
        "hero-title": "التسجيل لـ {{ opportunity.title }}",
        "hero-desc": "تقديم طلبك لهذه الفرصة في سوق المهارات بإدوفيا",
        "form-title": "التسجيل لـ {{ opportunity.title }}",
        "submit-btn": "تقديم الطلب",
        "back-to-opportunities": "العودة إلى الفرص",
        "back-to-services": "العودة إلى الخدمات",
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
    const opportunityTitle = document.querySelector('.hero h1').textContent.replace(translations[currentLang]["hero-title"].split('{{ opportunity.title }}')[0], '').trim() || 'Opportunity';
    
    htmlRoot.setAttribute('lang', newLang);
    htmlRoot.setAttribute('dir', newLang === 'ar' ? 'rtl' : 'ltr');
    
    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        let text = translations[newLang][key];
        if (text.includes('{{ opportunity.title }}')) {
            text = text.replace('{{ opportunity.title }}', opportunityTitle);
        }
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

    document.title = translations[newLang]["page-title"].replace('{{ opportunity.title }}', opportunityTitle);
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
    const opportunityTitle = document.querySelector('.hero h1').textContent.replace(translations[savedLang]["hero-title"].split('{{ opportunity.title }}')[0], '').trim() || 'Opportunity';
    
    htmlRoot.setAttribute('lang', savedLang);
    htmlRoot.setAttribute('dir', savedLang === 'ar' ? 'rtl' : 'ltr');

    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        let text = translations[savedLang][key];
        if (text.includes('{{ opportunity.title }}')) {
            text = text.replace('{{ opportunity.title }}', opportunityTitle);
        }
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

    document.title = translations[savedLang]["page-title"].replace('{{ opportunity.title }}', opportunityTitle);
});