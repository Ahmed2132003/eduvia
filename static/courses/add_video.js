const translations = {
    en: {
        "add-video-title": "Add Video - Eduvia",
        "add-video-meta-desc-en": "Add a new video to your course on Eduvia's Instructor Dashboard. Enhance your course with engaging video content.",
        "add-video-meta-keywords-en": "Eduvia, add video, instructor dashboard, online teaching, video management",
        "add-video-meta-desc-ar": "أضف فيديو جديد إلى دورتك على لوحة تحكم المدربين في Eduvia. عزز دورتك بمحتوى فيديو جذاب.",
        "add-video-meta-keywords-ar": "Eduvia، إضافة فيديو، لوحة تحكم المدربين، التعليم عبر الإنترنت، إدارة الفيديو",
        "add-video-og-title": "Add Video - Eduvia",
        "add-video-og-desc": "Create and add new video content to your course on Eduvia's Instructor Dashboard.",
        "add-video-twitter-title": "Add Video - Eduvia",
        "add-video-twitter-desc": "Create and add new video content to your course on Eduvia's Instructor Dashboard.",
        "hero-title": "Add Video",
        "hero-desc": "Add a new video to your course: {{ course.title }} to engage your students.",
        "form-title": "Add Video to {{ course.title }}",
        "form-label-title": "Video Title",
        "form-label-description": "Description",
        "form-label-video-url": "Video URL (Optional)",
        "form-label-video-file": "Upload Video (Optional)",
        "form-label-order": "Order",
        "form-label-unlocked": "Unlocked",
        "form-submit": "Add Video",
        "form-cancel": "Cancel",
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
        "add-video-title": "إضافة فيديو - إدوفيا",
        "add-video-meta-desc-en": "أضف فيديو جديد إلى دورتك على لوحة تحكم المدربين في Eduvia. عزز دورتك بمحتوى فيديو جذاب.",
        "add-video-meta-keywords-en": "Eduvia، إضافة فيديو، لوحة تحكم المدربين، التعليم عبر الإنترنت، إدارة الفيديو",
        "add-video-meta-desc-ar": "أضف فيديو جديد إلى دورتك على لوحة تحكم المدربين في Eduvia. عزز دورتك بمحتوى فيديو جذاب.",
        "add-video-meta-keywords-ar": "Eduvia، إضافة فيديو، لوحة تحكم المدربين، التعليم عبر الإنترنت، إدارة الفيديو",
        "add-video-og-title": "إضافة فيديو - إدوفيا",
        "add-video-og-desc": "أنشئ وأضف محتوى فيديو جديد إلى دورتك على لوحة تحكم المدربين في Eduvia.",
        "add-video-twitter-title": "إضافة فيديو - إدوفيا",
        "add-video-twitter-desc": "أنشئ وأضف محتوى فيديو جديد إلى دورتك على لوحة تحكم المدربين في Eduvia.",
        "hero-title": "إضافة فيديو",
        "hero-desc": "أضف فيديو جديد إلى دورتك: {{ course.title }} لإشراك طلابك.",
        "form-title": "إضافة فيديو إلى {{ course.title }}",
        "form-label-title": "عنوان الفيديو",
        "form-label-description": "الوصف",
        "form-label-video-url": "رابط الفيديو (اختياري)",
        "form-label-video-file": "رفع فيديو (اختياري)",
        "form-label-order": "الترتيب",
        "form-label-unlocked": "مفتوح",
        "form-submit": "إضافة الفيديو",
        "form-cancel": "إلغاء",
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
        } else if (['hero-desc', 'form-title'].includes(key)) {
            const courseTitle = element.textContent.match(/Add Video to (.*)/)?.[1] || '{{ course.title }}';
            text = translations[newLang][key].replace('{{ course.title }}', courseTitle);
            element.textContent = text;
        } else {
            element.textContent = text;
        }
    });

    document.title = translations[newLang]["add-video-title"];
    
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
            } else if (element.getAttribute('property')?.startsWith('og:') || element.getAttribute('name')?.startsWith('twitter:')) {
                element.setAttribute('content', text);
            }
        } else if (['hero-desc', 'form-title'].includes(key)) {
            const courseTitle = element.textContent.match(/Add Video to (.*)/)?.[1] || '{{ course.title }}';
            text = translations[savedLang][key].replace('{{ course.title }}', courseTitle);
            element.textContent = text;
        } else {
            element.textContent = text;
        }
    });

    document.title = translations[savedLang]["add-video-title"];

    const videoFileInput = document.getElementById('id_video_file');
    const videoPreview = document.querySelector('.video-preview');

    videoFileInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            const url = URL.createObjectURL(file);
            videoPreview.src = url;
            videoPreview.style.display = 'block';
        } else {
            videoPreview.src = '';
            videoPreview.style.display = 'none';
        }
    });
});