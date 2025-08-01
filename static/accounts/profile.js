const translations = {
    en: {
        "title": "User Profile - Eduvia",
        "logo": "Eduvia",
        "nav-home": "Home",
        "nav-courses": "Courses",
        "nav-chatbot": "Chatbot",
        "nav-competitions": "Competitions",
        "nav-performance": "Performance",
        "nav-about": "About Us",
        "nav-contact": "Contact Us",
        "nav-profile": "Profile",
        "nav-messages": "Messages",
        "nav-logout": "Logout",
        "nav-coins": "Coins:",
        "nav-login": "Login",
        "hero-title": "Your Profile",
        "hero-subtitle": "View and manage your personal details on Eduvia.",
        "profile-title": "User Profile",
        "no-picture": "No profile picture uploaded.",
        "label-username": "Username:",
        "label-fullname": "Full Name:",
        "label-role": "Role:",
        "label-dob": "Date of Birth:",
        "label-file": "Choose File",
        "btn-chat": "Chat",
        "btn-edit": "Edit Profile",
        "btn-home": "Back to Home",
        "btn-send": "Send Message",
        "message-form-title": "Send a Message to ",
        "footer-text": "© 2025 Eduvia. All rights reserved."
    },
    ar: {
        "title": "الملف الشخصي - إدوفيا",
        "logo": "إدوفيا",
        "nav-home": "الرئيسية",
        "nav-courses": "الدورات",
        "nav-chatbot": "الدردشة الآلية",
        "nav-competitions": "المسابقات",
        "nav-performance": "الأداء",
        "nav-about": "معلومات عنا",
        "nav-contact": "تواصل معنا",
        "nav-profile": "الملف الشخصي",
        "nav-messages": "الرسائل",
        "nav-logout": "تسجيل الخروج",
        "nav-coins": "النقاط:",
        "nav-login": "تسجيل الدخول",
        "hero-title": "ملفك الشخصي",
        "hero-subtitle": "عرض وإدارة تفاصيلك الشخصية على إدوفيا.",
        "profile-title": "الملف الشخصي",
        "no-picture": "لم يتم رفع صورة شخصية.",
        "label-username": "اسم المستخدم:",
        "label-fullname": "الاسم الكامل:",
        "label-role": "الدور:",
        "label-dob": "تاريخ الميلاد:",
        "label-file": "اختر ملف",
        "btn-chat": "دردشة",
        "btn-edit": "تعديل الملف الشخصي",
        "btn-home": "العودة إلى الرئيسية",
        "btn-send": "إرسال الرسالة",
        "message-form-title": "إرسال رسالة إلى ",
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