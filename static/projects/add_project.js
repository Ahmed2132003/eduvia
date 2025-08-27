const translations = {
    en: {
        "page-title": "Add New Project - Eduvia",
        "meta-desc": "Add a new open-source project on Eduvia. Create coding tasks, engage students, and contribute to the community.",
        "meta-keywords": "add project, Eduvia projects, open source, create project, instructor projects, coding collaboration",
        "og-title": "Add New Project - Eduvia",
        "og-desc": "Create a new open-source project on Eduvia to engage students and foster collaboration.",
        "hero-title": "Add New Project",
        "hero-desc": "Create an open-source project to engage students and foster collaboration.",
        "view-btn": "View All Projects",
        "form-title": "Create a New Project",
        "title-label": "Project Title",
        "title-invalid": "Please enter a project title.",
        "desc-label": "Description",
        "desc-invalid": "Please enter a description.",
        "url-label": "Repository URL",
        "url-invalid": "Please enter a valid URL.",
        "category-label": "Category",
        "status-label": "Status",
        "image-label": "Project Image URL",
        "image-hint": "Enter the URL of an image for your project (e.g., from PostImage, optional).",
        "image-invalid": "Please enter a valid image URL (e.g., ending with .jpg, .png, .gif).",
        "submit-btn": "Create Project",
        "cancel-btn": "Cancel",
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
        "page-title": "إضافة مشروع جديد - إدوفيا",
        "meta-desc": "أضف مشروعًا مفتوح المصدر جديدًا على إدوفيا. أنشئ مهام برمجة، اجذب الطلاب، وساهم في المجتمع.",
        "meta-keywords": "إضافة مشروع, مشاريع إدوفيا, المصدر المفتوح, إنشاء مشروع, مشاريع المدربين, تعاون البرمجة",
        "og-title": "إضافة مشروع جديد - إدوفيا",
        "og-desc": "أنشئ مشروعًا مفتوح المصدر جديدًا على إدوفيا لجذب الطلاب وتعزيز التعاون.",
        "hero-title": "إضافة مشروع جديد",
        "hero-desc": "أنشئ مشروعًا مفتوح المصدر لجذب الطلاب وتعزيز التعاون.",
        "view-btn": "عرض جميع المشاريع",
        "form-title": "إنشاء مشروع جديد",
        "title-label": "عنوان المشروع",
        "title-invalid": "يرجى إدخال عنوان المشروع.",
        "desc-label": "الوصف",
        "desc-invalid": "يرجى إدخال وصف.",
        "url-label": "رابط المستودع",
        "url-invalid": "يرجى إدخال رابط صالح.",
        "category-label": "الفئة",
        "status-label": "الحالة",
        "image-label": "رابط صورة المشروع",
        "image-hint": "أدخل رابط صورة لمشروعك (مثلًا من PostImage، اختياري).",
        "image-invalid": "يرجى إدخال رابط صورة صالح (ينتهي بـ .jpg، .png، .gif).",
        "submit-btn": "إنشاء المشروع",
        "cancel-btn": "إلغاء",
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
            } else if (element.getAttribute('property')?.startsWith('og:') || element.getAttribute('name')?.startsWith('twitter:')) {
                element.setAttribute('content', text);
            }
        } else {
            element.textContent = text;
        }
    });

    document.title = translations[newLang]["page-title"];
    localStorage.setItem('language', newLang);
}

(function () {
    'use strict';
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            const imageUrlInput = form.querySelector('#id_image_url');
            if (imageUrlInput && imageUrlInput.value) {
                const validExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp'];
                const isValidImage = validExtensions.some(ext => imageUrlInput.value.toLowerCase().endsWith(ext));
                if (!isValidImage) {
                    imageUrlInput.classList.add('is-invalid');
                    event.preventDefault();
                    event.stopPropagation();
                } else {
                    imageUrlInput.classList.remove('is-invalid');
                }
            }
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
})();

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
            } else if (element.getAttribute('property')?.startsWith('og:') || element.getAttribute('name')?.startsWith('twitter:')) {
                element.setAttribute('content', text);
            }
        } else {
            element.textContent = text;
        }
    });

    document.title = translations[savedLang]["page-title"];
});