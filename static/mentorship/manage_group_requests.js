const translations = {
    en: {
        "manage-requests-title": "Manage Group Requests - Eduvia",
        "manage-requests-meta-desc": "Manage requests to join {{ group.name }} in Eduvia's Mentorship System.",
        "manage-requests-meta-keywords": "manage group requests, {{ group.name }}, Eduvia, mentorship",
        "manage-requests-og-title": "Manage Group Requests - Eduvia",
        "manage-requests-og-desc": "Manage requests to join {{ group.name }} in Eduvia's Mentorship System.",
        "hero-title": "Manage Requests for {{ group.name }}",
        "hero-desc": "Review and approve requests to join your group",
        "requests-heading": "Group Join Requests",
        "requested-at-label": "Requested At:",
        "accept": "Accept",
        "reject": "Reject",
        "no-requests": "No pending requests at the moment.",
        "back-to-group": "Back to Group",
        "back-to-dashboard": "Back to Dashboard",
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
        "manage-requests-title": "إدارة طلبات المجموعة - إدوفيا",
        "manage-requests-meta-desc": "إدارة طلبات الانضمام إلى {{ group.name }} في نظام الإرشاد بمنصة إدوفيا.",
        "manage-requests-meta-keywords": "إدارة طلبات المجموعة, {{ group.name }}, إدوفيا, الإرشاد",
        "manage-requests-og-title": "إدارة طلبات المجموعة - إدوفيا",
        "manage-requests-og-desc": "إدارة طلبات الانضمام إلى {{ group.name }} في نظام الإرشاد بمنصة إدوفيا.",
        "hero-title": "إدارة الطلبات لـ {{ group.name }}",
        "hero-desc": "راجع ووافق على طلبات الانضمام إلى مجموعتك",
        "requests-heading": "طلبات الانضمام إلى المجموعة",
        "requested-at-label": "تم الطلب في:",
        "accept": "قبول",
        "reject": "رفض",
        "no-requests": "لا يوجد طلبات معلقة في الوقت الحالي.",
        "back-to-group": "العودة إلى المجموعة",
        "back-to-dashboard": "العودة إلى لوحة التحكم",
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

    document.title = translations[newLang]["manage-requests-title"];
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

    document.title = translations[savedLang]["manage-requests-title"];
});