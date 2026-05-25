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
        "nav-dashboard": "Dashboard",
        "nav-profile": "Profile",
        "nav-messages": "Messages",
        "nav-logout": "Logout",
        "nav-coins": "Coins:",
        "nav-login": "Login",
        "hero-title": "Your Profile",
        "hero-subtitle": "View and manage your personal details on Eduvia.",
        "profile-title": "User Profile",
        "no-picture": "No profile picture uploaded.",
        "label-username": "Username",
        "label-fullname": "Full Name",
        "label-role": "Role",
        "label-dob": "Date of Birth",
        "label-file": "Choose File",
        "btn-chat": "Chat",
        "btn-edit": "Edit Profile",
        "btn-home": "Back to Home",
        "btn-send": "Send Message",
        "message-form-title": "Send a Message to ",
        "quick-access-title": "Quick Access",
        "qa-mycourses-title": "My Courses",
        "qa-mycourses-desc": "View and continue your enrolled courses.",
        "qa-checkout-title": "Checkout",
        "qa-checkout-desc": "Enroll in new courses and manage payments.",
        "qa-wallet-title": "Instructor Wallet",
        "qa-wallet-desc": "Track your earnings and transaction history.",
        "qa-access-title": "Access Info",
        "qa-access-desc": "Learn about content access and enrollment requirements.",
        "qa-btn-open": "Open",
        "qa-btn-shop": "Shop",
        "qa-btn-view": "View",
        "qa-btn-learn": "Learn",
        "footer-text": "© 2025 Eduvia and creativitycode. All rights reserved."
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
        "nav-dashboard": "لوحة التحكم",
        "nav-profile": "الملف الشخصي",
        "nav-messages": "الرسائل",
        "nav-logout": "تسجيل الخروج",
        "nav-coins": "النقاط:",
        "nav-login": "تسجيل الدخول",
        "hero-title": "ملفك الشخصي",
        "hero-subtitle": "عرض وإدارة تفاصيلك الشخصية على إدوفيا.",
        "profile-title": "الملف الشخصي",
        "no-picture": "لم يتم رفع صورة شخصية.",
        "label-username": "اسم المستخدم",
        "label-fullname": "الاسم الكامل",
        "label-role": "الدور",
        "label-dob": "تاريخ الميلاد",
        "label-file": "اختر ملف",
        "btn-chat": "دردشة",
        "btn-edit": "تعديل الملف الشخصي",
        "btn-home": "العودة إلى الرئيسية",
        "btn-send": "إرسال الرسالة",
        "message-form-title": "إرسال رسالة إلى ",
        "quick-access-title": "الوصول السريع",
        "qa-mycourses-title": "دوراتي",
        "qa-mycourses-desc": "عرض ومتابعة الدورات المسجّل بها.",
        "qa-checkout-title": "الدفع",
        "qa-checkout-desc": "التسجيل في دورات جديدة وإدارة المدفوعات.",
        "qa-wallet-title": "محفظة المدرب",
        "qa-wallet-desc": "تتبع أرباحك وسجل المعاملات.",
        "qa-access-title": "معلومات الوصول",
        "qa-access-desc": "تعرّف على شروط الوصول للمحتوى والتسجيل.",
        "qa-btn-open": "فتح",
        "qa-btn-shop": "تسوّق",
        "qa-btn-view": "عرض",
        "qa-btn-learn": "تعلّم",
        "footer-text": "© 2025 إدوفيا و كريتيفيتي كود. جميع الحقوق محفوظة."
    }
};

/* ---- Utility ---- */
function applyTranslations(lang) {
    document.querySelectorAll('[data-translate]').forEach(el => {
        const key = el.getAttribute('data-translate');
        const val = translations[lang][key];
        if (val !== undefined) el.textContent = val;
    });
    document.title = translations[lang]["title"] || document.title;
}

/* ---- Menu ---- */
function toggleMenu() {
    document.querySelector('.menu').classList.toggle('active');
}

/* ---- Dark Mode ---- */
function toggleDarkMode() {
    const body = document.body;
    const icon = document.querySelector('.dark-mode-toggle i');
    body.classList.toggle('dark-mode');
    const isDark = body.classList.contains('dark-mode');
    icon.className = isDark ? 'fas fa-sun' : 'fas fa-moon';
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
}

/* ---- Language ---- */
function toggleLanguage() {
    const root = document.getElementById('html-root');
    const current = root.getAttribute('lang');
    const next = current === 'en' ? 'ar' : 'en';
    root.setAttribute('lang', next);
    root.setAttribute('dir', next === 'ar' ? 'rtl' : 'ltr');
    applyTranslations(next);
    localStorage.setItem('language', next);
}

/* ---- Init ---- */
document.addEventListener('DOMContentLoaded', () => {
    // Theme
    const savedTheme = localStorage.getItem('theme');
    const themeIcon = document.querySelector('.dark-mode-toggle i');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        if (themeIcon) themeIcon.className = 'fas fa-sun';
    }

    // Language
    const savedLang = localStorage.getItem('language') || 'en';
    const root = document.getElementById('html-root');
    root.setAttribute('lang', savedLang);
    root.setAttribute('dir', savedLang === 'ar' ? 'rtl' : 'ltr');
    applyTranslations(savedLang);

    // Smooth entrance animation for info items
    const items = document.querySelectorAll('.info-item, .qa-card');
    items.forEach((el, i) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(16px)';
        el.style.transition = `opacity 0.5s ease ${i * 0.07}s, transform 0.5s ease ${i * 0.07}s`;
        requestAnimationFrame(() => {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        });
    });
});