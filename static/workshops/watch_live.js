const translations = {
    en: {
        "title": "Watch Live - {{ session.title }} - Eduvia",
        "meta-desc": "Watch the live session '{{ session.title }}' on Eduvia and engage with expert instructors in real-time.",
        "meta-keywords": "Eduvia, live session, workshop, watch live, online learning, education platform",
        "og-title": "Watch Live - {{ session.title }} - Eduvia",
        "og-desc": "Join the live session '{{ session.title }}' on Eduvia for an interactive learning experience.",
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
        "hero-title": "Watch Live: {{ session.title }}",
        "hero-subtitle": "Join the live session '{{ session.title }}' and engage with expert instructors in real-time.",
        "hero-btn": "Join Now",
        "container-title": "Watch Live: {{ session.title }}",
        "instructor-label": "Instructor:",
        "time-label": "Time:",
        "meet-link-label": "Meet Link:",
        "join-btn": "Join Live Session",
        "no-meet-link": "No Meet link available.",
        "footer-text": "© 2025 Eduvia. All rights reserved."
    },
    ar: {
        "title": "مشاهدة مباشرة - {{ session.title }} - إدوفيا",
        "meta-desc": "شاهد الجلسة المباشرة '{{ session.title }}' على إدوفيا وتفاعل مع المدربين الخبراء في الوقت الفعلي.",
        "meta-keywords": "إدوفيا, جلسة مباشرة, ورشة عمل, مشاهدة مباشرة, تعلم عبر الإنترنت, منصة تعليمية",
        "og-title": "مشاهدة مباشرة - {{ session.title }} - إدوفيا",
        "og-desc": "انضم إلى الجلسة المباشرة '{{ session.title }}' على إدوفيا لتجربة تعليمية تفاعلية.",
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
        "hero-title": "مشاهدة مباشرة: {{ session.title }}",
        "hero-subtitle": "انضم إلى الجلسة المباشرة '{{ session.title }}' وتفاعل مع المدربين الخبراء في الوقت الفعلي.",
        "hero-btn": "انضم الآن",
        "container-title": "مشاهدة مباشرة: {{ session.title }}",
        "instructor-label": "المدرب:",
        "time-label": "الوقت:",
        "meet-link-label": "رابط الاجتماع:",
        "join-btn": "انضم إلى الجلسة المباشرة",
        "no-meet-link": "لا يوجد رابط اجتماع متاح.",
        "footer-text": "© 2025 إدوفيا. جميع الحقوق محفوظة."
    }
};

function toggleMenu() {
    const menu = document.querySelector('.menu');
    menu.classList.toggle('active');
}

// Dark Mode Toggle
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

// Language Toggle
function toggleLanguage() {
    const htmlRoot = document.getElementById('html-root');
    const currentLang = htmlRoot.getAttribute('lang');
    const newLang = currentLang === 'en' ? 'ar' : 'en';
    
    // Update lang and direction
    htmlRoot.setAttribute('lang', newLang);
    htmlRoot.setAttribute('dir', newLang === 'ar' ? 'rtl' : 'ltr');
    
    // Update all translatable elements
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

    // Update the title
    document.title = translations[newLang]["title"];
    
    localStorage.setItem('language', newLang);
}

// Apply saved theme and language on page load
document.addEventListener('DOMContentLoaded', () => {
    // Apply Dark Mode
    const savedTheme = localStorage.getItem('theme');
    const toggleIcon = document.querySelector('.dark-mode-toggle i');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        toggleIcon.classList.remove('fa-moon');
        toggleIcon.classList.add('fa-sun');
    }

    // Apply Language
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

    document.title = translations[savedLang]["title"];
});