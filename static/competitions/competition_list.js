const translations = {
    en: {
        "competitions-title": "Educational Competitions | Eduvia",
        "competitions-meta-desc": "Join educational competitions on the Eduvia platform and earn XP and coins! Discover fun learning challenges designed to boost your skills.",
        "competitions-meta-keywords": "educational competitions, interactive learning, Eduvia platform, online learning, learning challenges, XP, coins",
        "competitions-og-title": "Educational Competitions | Eduvia",
        "competitions-og-desc": "Join educational competitions on the Eduvia platform and earn XP and coins!",
        "competitions-meta-desc-en": "Join educational competitions on the Eduvia platform and earn XP and coins! Discover fun learning challenges designed to boost your skills.",
        "competitions-meta-keywords-en": "educational competitions, interactive learning, Eduvia platform, online learning, learning challenges, XP, coins",
        "hero-title": "Educational Competitions",
        "hero-desc": "Join fun learning challenges and earn XP and coins!",
        "competitions-list-title": "List of Competitions",
        "create-competition-link": "Create New Competition",
        "date-label": "From:",
        "status-ongoing": "Ongoing",
        "status-not-started": "Not Started",
        "status-ended": "Ended",
        "no-competitions": "No competitions available.",
        "current-time-label": "Current time:",
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
        "footer-text": "© 2025 Eduvia. All rights reserved."
    },
    ar: {
        "competitions-title": "المسابقات التعليمية | إدوفيا",
        "competitions-meta-desc": "شارك في المسابقات التعليمية على منصة Eduvia واكسب نقاط XP وكوينز! اكتشف تحديات تعليمية ممتعة مصممة لتعزيز مهاراتك.",
        "competitions-meta-keywords": "مسابقات تعليمية, تعليم تفاعلي, منصة إدوفيا, تعلم عبر الإنترنت, تحديات تعليمية, XP, كوينز",
        "competitions-og-title": "المسابقات التعليمية | إدوفيا",
        "competitions-og-desc": "شارك في المسابقات التعليمية على منصة Eduvia واكسب نقاط XP وكوينز!",
        "competitions-meta-desc-en": "شارك في المسابقات التعليمية على منصة Eduvia واكسب نقاط XP وكوينز! اكتشف تحديات تعليمية ممتعة مصممة لتعزيز مهاراتك.",
        "competitions-meta-keywords-en": "مسابقات تعليمية, تعليم تفاعلي, منصة إدوفيا, تعلم عبر الإنترنت, تحديات تعليمية, XP, كوينز",
        "hero-title": "المسابقات التعليمية",
        "hero-desc": "انضم إلى تحديات تعليمية ممتعة واكسب XP وكوينز!",
        "competitions-list-title": "قائمة المسابقات",
        "create-competition-link": "إنشاء مسابقة جديدة",
        "date-label": "من:",
        "status-ongoing": "جارية",
        "status-not-started": "لم تبدأ",
        "status-ended": "انتهت",
        "no-competitions": "لا توجد مسابقات متاحة.",
        "current-time-label": "الوقت الحالي:",
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
        const text = translations[newLang][key];
        if (element.tagName.toLowerCase() === 'meta') {
            if (element.getAttribute('name') === 'description' || element.getAttribute('name') === 'keywords') {
                element.setAttribute('content', text);
            } else if (element.getAttribute('property')?.startsWith('og:')) {
                element.setAttribute('content', text);
            }
        } else if (element.tagName.toLowerCase() === 'p' && ['date-label', 'current-time-label'].includes(key)) {
            const labelText = text + " ";
            const dynamicContent = element.childNodes[element.childNodes.length - 1].textContent.trim();
            element.textContent = labelText + dynamicContent;
        } else if (element.tagName.toLowerCase() === 'span' && ['status-ongoing', 'status-not-started', 'status-ended'].includes(key)) {
            element.textContent = text;
        } else if (element.tagName.toLowerCase() === 'li' && key === 'no-competitions') {
            element.textContent = text;
        } else {
            element.textContent = text;
        }
    });

    document.title = translations[newLang]["competitions-title"];
    
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
        const text = translations[savedLang][key];
        if (element.tagName.toLowerCase() === 'meta') {
            if (element.getAttribute('name') === 'description' || element.getAttribute('name') === 'keywords') {
                element.setAttribute('content', text);
            } else if (element.getAttribute('property')?.startsWith('og:')) {
                element.setAttribute('content', text);
            }
        } else if (element.tagName.toLowerCase() === 'p' && ['date-label', 'current-time-label'].includes(key)) {
            const labelText = text + " ";
            const dynamicContent = element.childNodes[element.childNodes.length - 1].textContent.trim();
            element.textContent = labelText + dynamicContent;
        } else if (element.tagName.toLowerCase() === 'span' && ['status-ongoing', 'status-not-started', 'status-ended'].includes(key)) {
            element.textContent = text;
        } else if (element.tagName.toLowerCase() === 'li' && key === 'no-competitions') {
            element.textContent = text;
        } else {
            element.textContent = text;
        }
    });

    document.title = translations[savedLang]["competitions-title"];
});