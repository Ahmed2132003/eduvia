const translations = {
    en: {
        "create-competition-title": "Create Competition | Eduvia",
        "create-competition-meta-desc": "Create educational competitions on the Eduvia platform and design engaging challenges for students to enhance their skills and earn XP and coins!",
        "create-competition-meta-keywords": "create competitions, educational competitions, Eduvia platform, interactive learning, learning challenges, XP, coins",
        "create-competition-og-title": "Create Competition | Eduvia",
        "create-competition-og-desc": "Create educational competitions on the Eduvia platform and design engaging challenges for students to enhance their skills and earn XP and coins!",
        "create-competition-meta-desc-en": "Create educational competitions on the Eduvia platform and design engaging challenges for students to enhance their skills and earn XP and coins!",
        "create-competition-meta-keywords-en": "create competitions, educational competitions, Eduvia platform, interactive learning, learning challenges, XP, coins",
        "hero-title": "Create a New Competition",
        "hero-desc": "Design exciting challenges for students to learn and earn rewards!",
        "content-title": "Create Competition",
        "create-button": "Create",
        "nav-home": "Home",
        "nav-courses": "Courses",
        "nav-chatbot": "Chatbot",
        "nav-competitions": "Competitions",
        "nav-performance": "Performance",
        "nav-about": "About Us",
        "nav-contact": "Contact Us",
        "nav-dashboard": "Dashboard",
        "nav-subscribe": "subscribe",
        "nav-profile": "Profile",
        "nav-logout": "Logout",
        "nav-coins": "Coins:",
        "nav-login": "Login",
        "footer-text": "© 2025 Eduvia and creativitycode. All rights reserved."
    },
    ar: {
        "create-competition-title": "إنشاء مسابقة | إدوفيا",
        "create-competition-meta-desc": "أنشئ مسابقات تعليمية على منصة Eduvia وصمم تحديات ممتعة للطلاب لتعزيز مهاراتهم واكتساب نقاط XP وكوينز!",
        "create-competition-meta-keywords": "إنشاء مسابقات, مسابقات تعليمية, منصة إدوفيا, تعليم تفاعلي, تحديات تعليمية, XP, كوينز",
        "create-competition-og-title": "إنشاء مسابقة | إدوفيا",
        "create-competition-og-desc": "أنشئ مسابقات تعليمية على منصة Eduvia وصمم تحديات ممتعة للطلاب لتعزيز مهاراتهم واكتساب نقاط XP وكوينز!",
        "create-competition-meta-desc-en": "أنشئ مسابقات تعليمية على منصة Eduvia وصمم تحديات ممتعة للطلاب لتعزيز مهاراتهم واكتساب نقاط XP وكوينز!",
        "create-competition-meta-keywords-en": "إنشاء مسابقات, مسابقات تعليمية, منصة إدوفيا, تعليم تفاعلي, تحديات تعليمية, XP, كوينز",
        "hero-title": "إنشاء مسابقة جديدة",
        "hero-desc": "صمم تحديات مثيرة للطلاب للتعلم وكسب المكافآت!",
        "content-title": "إنشاء مسابقة",
        "create-button": "إنشاء",
        "nav-home": "الرئيسية",
        "nav-courses": "الدورات",
        "nav-chatbot": "الدردشة الآلية",
        "nav-competitions": "المسابقات",
        "nav-performance": "الأداء",
        "nav-about": "معلومات عنا",
        "nav-contact": "تواصل معنا",
        "nav-dashboard": "لوحة التحكم",
        "nav-subscribe": "الاشتراك",
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
        const text = translations[newLang][key];
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

    document.title = translations[newLang]["create-competition-title"];
    
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
        } else {
            element.textContent = text;
        }
    });

    document.title = translations[savedLang]["create-competition-title"];
});