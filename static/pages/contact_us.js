// Translation object
const translations = {
    en: {
        "title": "Contact Us - Eduvia",
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
        "hero-title": "Contact Us",
        "hero-subtitle": "Our team is ready to answer your questions and support your learning journey",
        "content-title": "We are here to help you anytime",
        "content-desc1": "If you need any assistance, please feel free to contact us. Our support team is always available to answer all your queries.",
        "content-desc2": "You can reach us through the following channels or via social media.",
        "social-facebook": "Facebook",
        "social-instagram": "Instagram",
        "social-whatsapp": "WhatsApp",
        "social-linkedin": "LinkedIn",
        "social-github": "GitHub",
        "social-tiktok": "TikTok",
        "social-youtube": "YouTube",
        "footer-text": "© 2025 Eduvia and creativitycode. All rights reserved."
    },
    ar: {
        "title": "تواصل معنا - إدوفيا",
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
        "hero-title": "تواصل معنا",
        "hero-subtitle": "فريقنا جاهز للإجابة على أسئلتك ودعم رحلتك التعليمية",
        "content-title": "نحن هنا لمساعدتك في أي وقت",
        "content-desc1": "إذا كنت بحاجة إلى أي مساعدة، لا تتردد في التواصل معنا. فريق الدعم لدينا دائمًا متاح للإجابة على جميع استفساراتك.",
        "content-desc2": "يمكنك الوصول إلينا من خلال القنوات التالية أو عبر وسائل التواصل الاجتماعي.",
        "social-facebook": "فيسبوك",
        "social-instagram": "إنستغرام",
        "social-whatsapp": "واتساب",
        "social-linkedin": "لينكدإن",
        "social-github": "جيثب",
        "social-tiktok": "تيك توك",
        "social-youtube": "يوتيوب",
        "footer-text": "© 2025 إدوفيا و كريتيفيتي كود . جميع الحقوق محفوظة."
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
        element.textContent = translations[newLang][key];
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
        element.textContent = translations[savedLang][key];
    });

    document.title = translations[savedLang]["title"];
});
