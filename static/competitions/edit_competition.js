const translations = {
    en: {
        "edit-competition-title": "Edit Competition | Eduvia",
        "edit-competition-meta-desc": "Edit educational competitions on the Eduvia platform to customize learning challenges and enhance the student learning experience!",
        "edit-competition-meta-keywords": "edit competitions, educational competitions, Eduvia platform, interactive learning, learning challenges, customize competitions",
        "edit-competition-og-title": "Edit Competition | Eduvia",
        "edit-competition-og-desc": "Edit educational competitions on the Eduvia platform to customize learning challenges and enhance the student learning experience!",
        "edit-competition-meta-desc-en": "Edit educational competitions on the Eduvia platform to customize learning challenges and enhance the student learning experience!",
        "edit-competition-meta-keywords-en": "edit competitions, educational competitions, Eduvia platform, interactive learning, learning challenges, customize competitions",
        "hero-title": "Edit {{ competition.title }}",
        "content-title": "Edit {{ competition.title }}",
        "save-button": "Save Changes",
        "back-link": "Back to Competition",
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
        "edit-competition-title": "تحرير المسابقة | إدوفيا",
        "edit-competition-meta-desc": "قم بتحرير المسابقات التعليمية على منصة Eduvia لتخصيص التحديات التعليمية وتعزيز تجربة التعلم للطلاب!",
        "edit-competition-meta-keywords": "تحرير المسابقات, مسابقات تعليمية, منصة إدوفيا, تعليم تفاعلي, تحديات تعليمية, تخصيص المسابقات",
        "edit-competition-og-title": "تحرير المسابقة | إدوفيا",
        "edit-competition-og-desc": "قم بتحرير المسابقات التعليمية على منصة Eduvia لتخصيص التحديات التعليمية وتعزيز تجربة التعلم للطلاب!",
        "edit-competition-meta-desc-en": "قم بتحرير المسابقات التعليمية على منصة Eduvia لتخصيص التحديات التعليمية وتعزيز تجربة التعلم للطلاب!",
        "edit-competition-meta-keywords-en": "تحرير المسابقات, مسابقات تعليمية, منصة إدوفيا, تعليم تفاعلي, تحديات تعليمية, تخصيص المسابقات",
        "hero-title": "تحرير {{ competition.title }}",
        "content-title": "تحرير {{ competition.title }}",
        "save-button": "حفظ التغييرات",
        "back-link": "العودة إلى المسابقة",
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
        } else if (['hero-title', 'content-title'].includes(key)) {
            const competitionTitle = element.textContent.match(/Edit (.*)/)?.[1] || '{{ competition.title }}';
            text = translations[newLang][key].replace('{{ competition.title }}', competitionTitle);
            element.textContent = text;
        } else {
            element.textContent = text;
        }
    });

    document.title = translations[newLang]["edit-competition-title"];
    
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
        } else if (['hero-title', 'content-title'].includes(key)) {
            const competitionTitle = element.textContent.match(/Edit (.*)/)?.[1] || '{{ competition.title }}';
            text = translations[savedLang][key].replace('{{ competition.title }}', competitionTitle);
            element.textContent = text;
        } else {
            element.textContent = text;
        }
    });

    document.title = translations[savedLang]["edit-competition-title"];
});