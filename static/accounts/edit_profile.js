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
        "form-card-subtitle": "Update your personal information",
        "label-fullname": "Full Name",
        "label-dob": "Date of Birth",
        "label-profile-picture": "Profile Picture URL",
        "image-upload-instruction": "Upload your image to",
        "image-upload-instruction-2": "and paste the direct link here.",
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
        "form-card-subtitle": "تحديث معلوماتك الشخصية",
        "label-fullname": "الاسم الكامل",
        "label-dob": "تاريخ الميلاد",
        "label-profile-picture": "رابط صورة الملف الشخصي",
        "image-upload-instruction": "ارفع صورتك على",
        "image-upload-instruction-2": "والصق الرابط المباشر هنا.",
        "btn-save": "حفظ التغييرات",
        "btn-cancel": "إلغاء",
        "footer-text": "© 2025 إدوفيا. جميع الحقوق محفوظة."
    }
};

/* ---- Utility ---- */
function applyTranslations(lang) {
    document.querySelectorAll('[data-translate]').forEach(el => {
        const key = el.getAttribute('data-translate');
        const val = translations[lang][key];
        if (val !== undefined) {
            // For labels that wrap form fields, only set textContent if
            // the element doesn't have child elements we'd destroy
            if (el.tagName.toLowerCase() === 'label' && el.children.length > 0) {
                // Replace text node only (first child that is a text node)
                const icon = el.querySelector('i');
                el.textContent = val;
                if (icon) el.prepend(icon);
            } else {
                el.textContent = val;
            }
        }
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

/* ---- Save button loading state ---- */
function attachFormLoading() {
    const form = document.querySelector('.edit-profile-container form');
    if (!form) return;
    form.addEventListener('submit', () => {
        const btn = form.querySelector('button[type="submit"]');
        if (btn) {
            btn.classList.add('loading');
            btn.disabled = true;
        }
    });
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

    // Form loading state
    attachFormLoading();

    // Input focus glow — ensure the CSS already handles this,
    // but add a subtle "filled" class for non-empty inputs
    document.querySelectorAll('.edit-profile-container form input, .edit-profile-container form textarea').forEach(input => {
        const check = () => {
            if (input.value.trim()) input.classList.add('filled');
            else input.classList.remove('filled');
        };
        input.addEventListener('input', check);
        check(); // run on load
    });
});