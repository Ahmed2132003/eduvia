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

const translations = {
    en: {
        "page-title": "Create Live Session - Eduvia",
        "meta-desc": "Create a live session on Eduvia to engage with learners. Schedule your online workshop, add details, and share your Google Meet link for interactive teaching.",
        "meta-keywords": "Eduvia, live session, online learning, schedule workshop, Google Meet, instructor dashboard, coding workshops, AI teaching",
        "og-title": "Create Live Session - Eduvia",
        "og-desc": "Schedule and create live sessions on Eduvia to teach coding, AI, and more to students worldwide.",
        "hero-title": "Create Your Live Workshop",
        "hero-desc": "Engage with learners worldwide by scheduling interactive live sessions on Eduvia.",
        "hero-btn": "Get Started",
        "form-title": "Create Live Session",
        "form-title-label": "Title",
        "form-desc-label": "Description",
        "form-meet-label": "Google Meet Link",
        "form-image-label": "Session Image URL",
        "form-start-label": "Start Time",
        "form-end-label": "End Time",
        "form-submit": "Create Session",
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
        "page-title": "إنشاء جلسة مباشرة - إدوفيا",
        "meta-desc": "أنشئ جلسة مباشرة على إدوفيا للتفاعل مع المتعلمين. قم بجدولة ورشة عملك عبر الإنترنت، أضف التفاصيل، وشارك رابط Google Meet الخاص بك للتعليم التفاعلي.",
        "meta-keywords": "إدوفيا, جلسة مباشرة, تعلم إلكتروني, جدولة ورشة عمل, Google Meet, لوحة تحكم المدرب, ورش برمجة, تدريس الذكاء الاصطناعي",
        "og-title": "إنشاء جلسة مباشرة - إدوفيا",
        "og-desc": "جدولة وإنشاء جلسات مباشرة على إدوفيا لتعليم البرمجة، الذكاء الاصطناعي، وأكثر للطلاب حول العالم.",
        "hero-title": "أنشئ ورشتك المباشرة",
        "hero-desc": "تفاعل مع المتعلمين حول العالم من خلال جدولة جلسات مباشرة تفاعلية على إدوفيا.",
        "hero-btn": "ابدأ الآن",
        "form-title": "إنشاء جلسة مباشرة",
        "form-title-label": "العنوان",
        "form-desc-label": "الوصف",
        "form-meet-label": "رابط Google Meet",
        "form-image-label": "رابط صورة الجلسة",
        "form-start-label": "وقت البدء",
        "form-end-label": "وقت الانتهاء",
        "form-submit": "إنشاء الجلسة",
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