const translations = {
    en: {
        "page-title": "Instructor Dashboard - Eduvia",
        "meta-desc": "Manage your courses and videos on Eduvia's Instructor Dashboard. Create, edit, and organize your educational content with ease.",
        "meta-keywords": "Eduvia, instructor dashboard, online teaching, course management, educational platform",
        "meta-desc-ar": "إدارة دوراتك وفيديوهاتك على لوحة تحكم المدربين في إدوفيا. أنشئ، حرر، ونظم محتواك التعليمي بسهولة.",
        "meta-keywords-ar": "إدوفيا، لوحة تحكم المدربين، التعليم عبر الإنترنت، إدارة الدورات، منصة تعليمية",
        "og-title": "Instructor Dashboard - Eduvia",
        "og-desc": "Take control of your teaching with Eduvia's Instructor Dashboard. Manage courses and engage with students.",
        "twitter-title": "Instructor Dashboard - Eduvia",
        "twitter-desc": "Take control of your teaching with Eduvia's Instructor Dashboard. Manage courses and engage with students.",
        "hero-title": "Instructor Dashboard",
        "hero-desc": "Manage your courses and videos with ease. Create, edit, and engage with your students.",
        "overview-title": "Overview",
        "total-courses": "Total Courses: {{ total_courses }}",
        "total-videos": "Total Videos: {{ total_videos }}",
        "add-course-btn": "Add New Course",
        "courses-title": "Your Courses",
        "category-label": "Category: {{ course.get_category_display }}",
        "view-videos": "View Videos",
        "edit-course": "Edit",
        "no-courses": "No courses found. Create your first course!",
        "add-task": "Add Task",
        "add-alternative-quiz": "Add Alternative Quiz",
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
        "footer-text": "© 2025 Eduvia. All rights reserved."
    },
    ar: {
        "page-title": "لوحة تحكم المدرب - إدوفيا",
        "meta-desc": "إدارة دوراتك وفيديوهاتك على لوحة تحكم المدربين في إدوفيا. أنشئ، حرر، ونظم محتواك التعليمي بسهولة.",
        "meta-keywords": "إدوفيا، لوحة تحكم المدربين، التعليم عبر الإنترنت، إدارة الدورات، منصة تعليمية",
        "meta-desc-ar": "إدارة دوراتك وفيديوهاتك على لوحة تحكم المدربين في إدوفيا. أنشئ، حرر، ونظم محتواك التعليمي بسهولة.",
        "meta-keywords-ar": "إدوفيا، لوحة تحكم المدربين، التعليم عبر الإنترنت، إدارة الدورات، منصة تعليمية",
        "og-title": "لوحة تحكم المدرب - إدوفيا",
        "og-desc": "تحكم في تدريسك مع لوحة تحكم المدربين في إدوفيا. إدارة الدورات والتفاعل مع الطلاب.",
        "twitter-title": "لوحة تحكم المدرب - إدوفيا",
        "twitter-desc": "تحكم في تدريسك مع لوحة تحكم المدربين في إدوفيا. إدارة الدورات والتفاعل مع الطلاب.",
        "hero-title": "لوحة تحكم المدرب",
        "hero-desc": "إدارة دوراتك وفيديوهاتك بسهولة. أنشئ، حرر، وتفاعل مع طلابك.",
        "overview-title": "نظرة عامة",
        "total-courses": "إجمالي الدورات: {{ total_courses }}",
        "total-videos": "إجمالي الفيديوهات: {{ total_videos }}",
        "add-course-btn": "إضافة دورة جديدة",
        "courses-title": "دوراتك",
        "category-label": "الفئة: {{ course.get_category_display }}",
        "view-videos": "عرض الفيديوهات",
        "edit-course": "تعديل",
        "no-courses": "لم يتم العثور على دورات. أنشئ دورتك الأولى!",
        "add-task": "إضافة مهمة",
        "add-alternative-quiz": "إضافة اختبار بديل",
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
            element.setAttribute('content', text);
        } else if (key === 'total-courses') {
            const count = element.textContent.match(/Total Courses: (\d+)/)?.[1] || '{{ total_courses }}';
            text = translations[newLang][key].replace('{{ total_courses }}', count);
            element.textContent = text;
        } else if (key === 'total-videos') {
            const count = element.textContent.match(/Total Videos: (\d+)/)?.[1] || '{{ total_videos }}';
            text = translations[newLang][key].replace('{{ total_videos }}', count);
            element.textContent = text;
        } else if (key === 'category-label') {
            const category = element.textContent.match(/Category: (.+)/)?.[1] || '{{ course.get_category_display }}';
            text = translations[newLang][key].replace('{{ course.get_category_display }}', category);
            element.textContent = text;
        } else {
            element.textContent = text;
        }
    });

    document.title = translations[newLang]["page-title"];
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
            element.setAttribute('content', text);
        } else if (key === 'total-courses') {
            const count = element.textContent.match(/Total Courses: (\d+)/)?.[1] || '{{ total_courses }}';
            text = translations[savedLang][key].replace('{{ total_courses }}', count);
            element.textContent = text;
        } else if (key === 'total-videos') {
            const count = element.textContent.match(/Total Videos: (\d+)/)?.[1] || '{{ total_videos }}';
            text = translations[savedLang][key].replace('{{ total_videos }}', count);
            element.textContent = text;
        } else if (key === 'category-label') {
            const category = element.textContent.match(/Category: (.+)/)?.[1] || '{{ course.get_category_display }}';
            text = translations[savedLang][key].replace('{{ course.get_category_display }}', category);
            element.textContent = text;
        } else {
            element.textContent = text;
        }
    });

    document.title = translations[savedLang]["page-title"];
});