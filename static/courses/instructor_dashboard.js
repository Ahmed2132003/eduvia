const translations = {
    en: {
        "page-title": "Instructor Dashboard - Eduvia",
        "meta-desc": "Manage your courses and videos on Eduvia's Instructor Dashboard. Create, edit, and organize your educational content.",
        "meta-keywords": "Eduvia, instructor dashboard, course management, online teaching, video management",
        "meta-desc-ar": "إدارة دوراتك وفيديوهاتك على لوحة تحكم المدربين في إدوفيا. أنشئ، حرر، ونظم محتواك التعليمي.",
        "meta-keywords-ar": "إدوفيا، لوحة تحكم المدربين، إدارة الدورات، التعليم عبر الإنترنت، إدارة الفيديو",
        "og-title": "Instructor Dashboard - Eduvia",
        "og-desc": "Manage your courses and videos on Eduvia's Instructor Dashboard.",
        "twitter-title": "Instructor Dashboard - Eduvia",
        "twitter-desc": "Manage your courses and videos on Eduvia's Instructor Dashboard.",
        "title": "Eduvia",
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
        "hero-title": "Instructor Dashboard",
        "hero-subtitle": "Manage your courses and videos with ease",
        "hero-btn": "Add New Course",
        "upgrade-btn": "Upgrade Your Plan",
        "welcome-text": "Welcome",
        "plan-text": "Subscription Plan",
        "courses-count": "Total Courses",
        "videos-count": "Total Videos",
        "free-plan-limit": "You have reached the maximum limit of one course in the free plan. Upgrade to the Instructor Plan for unlimited courses.",
        "courses-title": "Your Courses",
        "table-course-title": "Course Title",
        "table-videos": "Videos",
        "table-actions": "Actions",
        "no-videos": "No videos available",
        "no-courses": "You haven't created any courses yet.",
        "edit-btn": "Edit",
        "delete-btn": "Delete",
        "add-video-btn": "Add Video",
        "view-videos-btn": "View Videos",
        "video-limit": "You have reached the maximum limit of 10 videos in this course. Upgrade to add more.",
        "footer-text": "© 2025 Eduvia and creativitycode. All rights reserved."
    },
    ar: {
        "page-title": "لوحة تحكم المدرب - إدوفيا",
        "meta-desc": "إدارة دوراتك وفيديوهاتك على لوحة تحكم المدربين في إدوفيا. أنشئ، حرر، ونظم محتواك التعليمي.",
        "meta-keywords": "إدوفيا، لوحة تحكم المدربين، إدارة الدورات، التعليم عبر الإنترنت، إدارة الفيديو",
        "meta-desc-ar": "إدارة دوراتك وفيديوهاتك على لوحة تحكم المدربين في إدوفيا. أنشئ، حرر، ونظم محتواك التعليمي.",
        "meta-keywords-ar": "إدوفيا، لوحة تحكم المدربين، إدارة الدورات، التعليم عبر الإنترنت، إدارة الفيديو",
        "og-title": "لوحة تحكم المدرب - إدوفيا",
        "og-desc": "إدارة دوراتك وفيديوهاتك على لوحة تحكم المدربين في إدوفيا.",
        "twitter-title": "لوحة تحكم المدرب - إدوفيا",
        "twitter-desc": "إدارة دوراتك وفيديوهاتك على لوحة تحكم المدربين في إدوفيا.",
        "title": "إدوفيا",
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
        "hero-title": "لوحة تحكم المدرب",
        "hero-subtitle": "إدارة دوراتك وفيديوهاتك بسهولة",
        "hero-btn": "إضافة دورة جديدة",
        "upgrade-btn": "ترقية خطتك",
        "welcome-text": "مرحبًا",
        "plan-text": "خطة الاشتراك",
        "courses-count": "إجمالي الدورات",
        "videos-count": "إجمالي الفيديوهات",
        "free-plan-limit": "لقد وصلت إلى الحد الأقصى لإضافة دورة واحدة في الخطة المجانية. قم بالترقية إلى خطة المدرب لإضافة دورات غير محدودة.",
        "courses-title": "دوراتك",
        "table-course-title": "عنوان الدورة",
        "table-videos": "الفيديوهات",
        "table-actions": "الإجراءات",
        "no-videos": "لا توجد فيديوهات متاحة",
        "no-courses": "لم تقم بإنشاء أي دورات بعد.",
        "edit-btn": "تعديل",
        "delete-btn": "حذف",
        "add-video-btn": "إضافة فيديو",
        "view-videos-btn": "عرض الفيديوهات",
        "video-limit": "لقد وصلت إلى الحد الأقصى لإضافة 10 فيديوهات في هذه الدورة. قم بالترقية لإضافة المزيد.",
        "footer-text": "© 2025 إدوفيا و كريتيفيتي كود . جميع الحقوق محفوظة."
    }
};

function toggleMenu() {
    const menu = document.querySelector('.menu');
    menu.classList.toggle('active');
    console.log('Menu toggled:', menu.classList.contains('active'));
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
        element.textContent = translations[newLang][key];
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
        element.textContent = translations[savedLang][key];
    });

    document.title = translations[savedLang]["page-title"];
});