const translations = {
    en: {
        "dashboard-title": "Mentor Dashboard - Eduvia",
        "dashboard-meta-desc": "Mentor dashboard in Eduvia's Mentorship System.",
        "dashboard-meta-keywords": "mentor dashboard, Eduvia, mentorship",
        "dashboard-og-title": "Mentor Dashboard - Eduvia",
        "dashboard-og-desc": "Mentor dashboard in Eduvia's Mentorship System.",
        "hero-title": "Mentor Dashboard",
        "hero-desc": "Manage your mentees, groups, and mentorship activities in Eduvia",
        "dashboard-heading": "Mentor Dashboard",
        "mentees-heading": "Your Mentees",
        "started": "Started: {{ mentorship.created_at|date:'F d, Y H:i' }}",
        "rate-mentor": "Rate Mentor",
        "no-mentees": "You have no mentees yet.",
        "admin-groups-heading": "Your Admin Groups",
        "description": "Description: {{ group.description|truncatewords:20 }}",
        "manage-requests": "Manage Requests",
        "edit-group": "Edit Group",
        "no-admin-groups": "You are not an admin of any groups.",
        "member-groups-heading": "Groups You Are In",
        "no-member-groups": "You are not a member of any groups.",
        "all-links-heading": "All Mentorship Links",
        "find-mentor": "Find Mentor",
        "request-mentorship": "Request Mentorship",
        "group-detail": "Group Detail",
        "create-group": "Create Group",
        "request-join-group": "Request Join Group",
        "manage-group-requests": "Manage Group Requests",
        "become-mentor": "Become Mentor",
        "mentor-dashboard": "Mentor Dashboard",
        "community-feed": "Community Feed",
        "post-comments": "Post Comments",
        "nav-home": "Home",
        "nav-courses": "Courses",
        "nav-chatbot": "Chatbot",
        "nav-competitions": "Competitions",
        "nav-performance": "Performance",
        "nav-skills-market": "Skills Market",
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
        "dashboard-title": "لوحة تحكم المرشد - إدوفيا",
        "dashboard-meta-desc": "لوحة تحكم المرشد في نظام الإرشاد بمنصة إدوفيا.",
        "dashboard-meta-keywords": "لوحة تحكم المرشد, إدوفيا, الإرشاد",
        "dashboard-og-title": "لوحة تحكم المرشد - إدوفيا",
        "dashboard-og-desc": "لوحة تحكم المرشد في نظام الإرشاد بمنصة إدوفيا.",
        "hero-title": "لوحة تحكم المرشد",
        "hero-desc": "إدارة المتدربين والمجموعات وأنشطة الإرشاد في إدوفيا",
        "dashboard-heading": "لوحة تحكم المرشد",
        "mentees-heading": "المتدربون الخاصون بك",
        "started": "بدأ في: {{ mentorship.created_at|date:'F d, Y H:i' }}",
        "rate-mentor": "تقييم المرشد",
        "no-mentees": "ليس لديك متدربون بعد.",
        "admin-groups-heading": "المجموعات التي تديرها",
        "description": "الوصف: {{ group.description|truncatewords:20 }}",
        "manage-requests": "إدارة الطلبات",
        "edit-group": "تعديل المجموعة",
        "no-admin-groups": "أنت لست مسؤولاً عن أي مجموعات.",
        "member-groups-heading": "المجموعات التي تنتمي إليها",
        "no-member-groups": "أنت لست عضوًا في أي مجموعات.",
        "all-links-heading": "جميع روابط الإرشاد",
        "find-mentor": "ابحث عن مرشد",
        "request-mentorship": "طلب إرشاد",
        "group-detail": "تفاصيل المجموعة",
        "create-group": "إنشاء مجموعة",
        "request-join-group": "طلب الانضمام إلى مجموعة",
        "manage-group-requests": "إدارة طلبات المجموعة",
        "become-mentor": "كن مرشدًا",
        "mentor-dashboard": "لوحة تحكم المرشد",
        "community-feed": "تغذية المجتمع",
        "post-comments": "تعليقات المنشور",
        "nav-home": "الرئيسية",
        "nav-courses": "الدورات",
        "nav-chatbot": "الدردشة الآلية",
        "nav-competitions": "المسابقات",
        "nav-performance": "الأداء",
        "nav-skills-market": "سوق المهارات",
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
        if (['started', 'description'].includes(key)) {
            if (key === 'started') {
                const date = element.textContent.match(/Started: (.*)/)?.[1] || '{{ mentorship.created_at|date:"F d, Y H:i" }}';
                text = translations[newLang][key].replace('{{ mentorship.created_at|date:"F d, Y H:i" }}', date);
            } else if (key === 'description') {
                const desc = element.textContent.match(/Description: (.*)/)?.[1] || '{{ group.description|truncatewords:20 }}';
                text = translations[newLang][key].replace('{{ group.description|truncatewords:20 }}', desc);
            }
            element.textContent = text;
        } else {
            element.textContent = text;
        }
    });

    document.title = translations[newLang]["dashboard-title"];
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
        if (['started', 'description'].includes(key)) {
            if (key === 'started') {
                const date = element.textContent.match(/Started: (.*)/)?.[1] || '{{ mentorship.created_at|date:"F d, Y H:i" }}';
                text = translations[savedLang][key].replace('{{ mentorship.created_at|date:"F d, Y H:i" }}', date);
            } else if (key === 'description') {
                const desc = element.textContent.match(/Description: (.*)/)?.[1] || '{{ group.description|truncatewords:20 }}';
                text = translations[savedLang][key].replace('{{ group.description|truncatewords:20 }}', desc);
            }
            element.textContent = text;
        } else {
            element.textContent = text;
        }
    });

    document.title = translations[savedLang]["dashboard-title"];
});