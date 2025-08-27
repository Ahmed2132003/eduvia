const translations = {
    en: {
        "find-mentor-title": "Find a Mentor - Eduvia",
        "find-mentor-meta-desc": "Find mentors and mentorship groups on Eduvia's Mentorship System.",
        "find-mentor-meta-keywords": "find mentor, mentorship groups, Eduvia, mentorship",
        "find-mentor-og-title": "Find a Mentor - Eduvia",
        "find-mentor-og-desc": "Find mentors and mentorship groups on Eduvia's Mentorship System.",
        "hero-title": "Find a Mentor",
        "hero-desc": "Connect with mentors and join mentorship groups to enhance your learning journey",
        "mentors-heading": "Available Mentors",
        "mentor-email": "Email:",
        "request-mentorship": "Request Mentorship",
        "no-mentors": "No mentors available at the moment.",
        "public-groups-heading": "Public Groups",
        "private-groups-heading": "Private Groups",
        "group-description": "Description:",
        "group-admin": "Admin:",
        "join-group": "Join Group",
        "request-join": "Request to Join",
        "no-public-groups": "No public groups available at the moment.",
        "no-private-groups": "No private groups available at the moment.",
        "back-to-dashboard": "Back to Dashboard",
        "create-group": "Create Group",
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
        "find-mentor-title": "ابحث عن مرشد - إدوفيا",
        "find-mentor-meta-desc": "ابحث عن مرشدين ومجموعات إرشاد في نظام الإرشاد بمنصة إدوفيا.",
        "find-mentor-meta-keywords": "ابحث عن مرشد, مجموعات الإرشاد, إدوفيا, الإرشاد",
        "find-mentor-og-title": "ابحث عن مرشد - إدوفيا",
        "find-mentor-og-desc": "ابحث عن مرشدين ومجموعات إرشاد في نظام الإرشاد بمنصة إدوفيا.",
        "hero-title": "ابحث عن مرشد",
        "hero-desc": "تواصل مع المرشدين وانضم إلى مجموعات الإرشاد لتعزيز رحلتك التعليمية",
        "mentors-heading": "المرشدون المتاحون",
        "mentor-email": "البريد الإلكتروني:",
        "request-mentorship": "طلب الإرشاد",
        "no-mentors": "لا يوجد مرشدون متاحون في الوقت الحالي.",
        "public-groups-heading": "المجموعات العامة",
        "private-groups-heading": "المجموعات الخاصة",
        "group-description": "الوصف:",
        "group-admin": "المدير:",
        "join-group": "انضم إلى المجموعة",
        "request-join": "طلب الانضمام",
        "no-public-groups": "لا توجد مجموعات عامة متاحة في الوقت الحالي.",
        "no-private-groups": "لا توجد مجموعات خاصة متاحة في الوقت الحالي.",
        "back-to-dashboard": "العودة إلى لوحة التحكم",
        "create-group": "إنشاء مجموعة",
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

    document.title = translations[newLang]["find-mentor-title"];
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

    document.title = translations[savedLang]["find-mentor-title"];
});