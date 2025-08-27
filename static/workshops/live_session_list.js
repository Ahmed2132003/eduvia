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
        "page-title": "Live Coding & AI Workshops - Eduvia",
        "meta-desc": "Join live coding, AI, and programming workshops on Eduvia. Explore interactive online classes, upload recordings, and enhance your learning experience.",
        "meta-keywords": "Eduvia, coding workshops, AI learning, online programming classes, live sessions, instructor-led training, cybersecurity courses, mathematics tutorials",
        "your-sessions": "Your Live Sessions",
        "instructor-label": "Instructor:",
        "time-label": "Time:",
        "meet-label": "Meet Link:",
        "start-live": "Start Live",
        "session-active": "Session is active!",
        "upload-recording": "Upload Recording",
        "watch-recording": "Watch Recording",
        "no-sessions": "You have no live sessions.",
        "active-sessions": "Active Live Sessions",
        "join-live": "Join Live",
        "no-active": "No active sessions at the moment.",
        "upcoming-sessions": "Upcoming Live Sessions",
        "starts-label": "Starts:",
        "no-upcoming": "No upcoming sessions scheduled.",
        "nav-home-btn": "Home",
        "nav-create-btn": "Create Session",
        "nav-back-btn": "Back",
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
        "footer-text": "© 2025 Eduvia and creativitycode. All rights reserved."
    },
    ar: {
        "page-title": "الجلسات المباشرة للبرمجة والذكاء الاصطناعي - إدوفيا",
        "meta-desc": "انضم إلى جلسات البرمجة والذكاء الاصطناعي المباشرة في إدوفيا. استكشف الفصول التفاعلية عبر الإنترنت، ارفع التسجيلات، وطور تجربتك التعليمية.",
        "meta-keywords": "إدوفيا, ورش برمجة, تعلم الذكاء الاصطناعي, فصول برمجة عبر الإنترنت, جلسات مباشرة, تدريب بقيادة مدرب, دورات أمن معلومات, دروس رياضيات",
        "your-sessions": "جلساتك المباشرة",
        "instructor-label": "المدرب:",
        "time-label": "الوقت:",
        "meet-label": "رابط الميت:",
        "start-live": "بدء مباشر",
        "session-active": "الجلسة نشطة!",
        "upload-recording": "رفع التسجيل",
        "watch-recording": "مشاهدة التسجيل",
        "no-sessions": "ليس لديك جلسات مباشرة.",
        "active-sessions": "الجلسات المباشرة النشطة",
        "join-live": "انضم مباشرة",
        "no-active": "لا توجد جلسات نشطة حاليًا.",
        "upcoming-sessions": "الجلسات المباشرة القادمة",
        "starts-label": "تبدأ:",
        "no-upcoming": "لا توجد جلسات قادمة مجدولة.",
        "nav-home-btn": "الرئيسية",
        "nav-create-btn": "إنشاء جلسة",
        "nav-back-btn": "رجوع",
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
        "footer-text": "© 2025 إدوفيا و كريتيفيتي كود. جميع الحقوق محفوظة."
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
            }
        } else {
            element.textContent = text;
        }
    });

    document.title = translations[savedLang]["page-title"];
});