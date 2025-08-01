const translations = {
    en: {
        "title": "Edit Profile - Eduvia",
        "logo": "Eduvia",
        "nav-home": "Home",
        "nav-courses": "Courses",
        "nav-recommendations": "Recommendations",
        "nav-chatbot": "Chatbot",
        "nav-about": "About Us",
        "nav-contact": "Contact Us",
        "nav-profile": "Profile",
        "nav-messages": "Messages",
        "nav-logout": "Logout",
        "nav-coins": "Coins:",
        "nav-login": "Login",
        "hero-title": "Edit Your Profile",
        "hero-subtitle": "Update your personal details to customize your Eduvia experience.",
        "edit-profile-title": "Edit Profile",
        "label-fullname": "Full Name:",
        "label-dob": "Date of Birth:",
        "label-profile-picture": "Profile Picture:",
        "btn-save": "Save Changes",
        "btn-cancel": "Cancel",
        "footer-text": "© 2025 Eduvia. All rights reserved."
    },
    ar: {
        "title": "تعديل الملف الشخصي - إدوفيا",
        "logo": "إدوفيا",
        "nav-home": "الرئيسية",
        "nav-courses": "الدورات",
        "nav-recommendations": "التوصيات",
        "nav-chatbot": "الدردشة الآلية",
        "nav-about": "معلومات عنا",
        "nav-contact": "تواصل معنا",
        "nav-profile": "الملف الشخصي",
        "nav-messages": "الرسائل",
        "nav-logout": "تسجيل الخروج",
        "nav-coins": "النقاط:",
        "nav-login": "تسجيل الدخول",
        "hero-title": "تعديل ملفك الشخصي",
        "hero-subtitle": "تحديث تفاصيلك الشخصية لتخصيص تجربتك على إدوفيا.",
        "edit-profile-title": "تعديل الملف الشخصي",
        "label-fullname": "الاسم الكامل:",
        "label-dob": "تاريخ الميلاد:",
        "label-profile-picture": "صورة الملف الشخصي:",
        "btn-save": "حفظ التغييرات",
        "btn-cancel": "إلغاء",
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
        if (element.tagName.toLowerCase() === 'label') {
            const forAttr = element.getAttribute('for');
            if (forAttr && translations[newLang][key]) {
                element.textContent = translations[newLang][key];
            }
        } else {
            element.textContent = translations[newLang][key];
        }
    });

    document.title = translations[newLang]["title"];
    
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
        if (element.tagName.toLowerCase() === 'label') {
            const forAttr = element.getAttribute('for');
            if (forAttr && translations[savedLang][key]) {
                element.textContent = translations[savedLang][key];
            }
        } else {
            element.textContent = translations[savedLang][key];
        }
    });

    document.title = translations[savedLang]["title"];
});