const translations = {
    en: {
        "title": "Add Task - Eduvia",
        "meta-description": "Add a new task to your course on Eduvia Platform. Easily create and manage tasks to enhance your learning experience.",
        "meta-keywords": "Eduvia, add task, course management, online learning, education platform",
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
        "hero-title": "Add New Task",
        "submit-btn": "Add Task",
        "back-link": "Back to Course",
        "footer-text": "© 2025 Eduvia and creativitycode. All rights reserved.",
        "form-label-title": "Task Title",
        "form-label-order": "Task Order",
        "form-label-question": "Question",
        "form-label-options": "Options (comma-separated)",
        "form-label-correct-answer": "Correct Answer",
        "add-question-btn": "+ Add Question",
        "remove-question-btn": "Remove",
    },
    ar: {
        "title": "إضافة مهمة - إدوفيا",
        "meta-description": "إضافة مهمة جديدة إلى دورتك على منصة إدوفيا. أنشئ وأدر المهام بسهولة لتعزيز تجربتك التعليمية.",
        "meta-keywords": "إدوفيا, إضافة مهمة, إدارة الدورات, التعلم عبر الإنترنت, منصة تعليمية",
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
        "hero-title": "إضافة مهمة جديدة",
        "submit-btn": "إضافة المهمة",
        "back-link": "العودة إلى الدورة",
        "footer-text": "© 2025 إدوفيا و كريتيفيتي كود . جميع الحقوق محفوظة.",
        "form-label-title": "عنوان المهمة",
        "form-label-order": "ترتيب المهمة",
        "form-label-question": "السؤال",
        "form-label-options": "الخيارات (مفصولة بفاصلة)",
        "form-label-correct-answer": "الإجابة الصحيحة",
        "add-question-btn": "+ إضافة سؤال",
        "remove-question-btn": "إزالة",
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
        element.textContent = translations[newLang][key];
    });

    document.querySelectorAll('meta[data-translate]').forEach(meta => {
        const key = meta.getAttribute('data-translate');
        meta.setAttribute('content', translations[newLang][key]);
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
        element.textContent = translations[savedLang][key];
    });

    document.querySelectorAll('meta[data-translate]').forEach(meta => {
        const key = meta.getAttribute('data-translate');
        meta.setAttribute('content', translations[savedLang][key]);
    });

    document.title = translations[savedLang]["title"];

    // Dynamic questions addition
    const addQuestionBtn = document.getElementById('add-question-btn');
    const questionsContainer = document.getElementById('questions-container');
    const questionsJson = document.getElementById('id_questions');  // Hidden field

    let questionCount = 0;

    addQuestionBtn.addEventListener('click', () => {
        questionCount++;
        const questionGroup = document.createElement('div');
        questionGroup.classList.add('question-group');
        questionGroup.innerHTML = `
            <label><i class="fas fa-question"></i> ${translations[savedLang]['form-label-question']} ${questionCount}</label>
            <input type="text" class="question-text" placeholder="${translations[savedLang]['form-label-question']}">
            <label><i class="fas fa-list"></i> ${translations[savedLang]['form-label-options']}</label>
            <input type="text" class="options" placeholder="${translations[savedLang]['form-label-options']}">
            <label><i class="fas fa-check"></i> ${translations[savedLang]['form-label-correct-answer']}</label>
            <input type="text" class="correct-answer" placeholder="${translations[savedLang]['form-label-correct-answer']}">
            <button type="button" class="remove-question-btn">${translations[savedLang]['remove-question-btn']}</button>
        `;
        questionsContainer.appendChild(questionGroup);

        // Remove button
        questionGroup.querySelector('.remove-question-btn').addEventListener('click', () => {
            questionGroup.remove();
        });
    });

    // On form submit, serialize to JSON
    document.getElementById('task-form').addEventListener('submit', (e) => {
        const questions = [];
        document.querySelectorAll('.question-group').forEach(group => {
            const question = group.querySelector('.question-text').value;
            const optionsStr = group.querySelector('.options').value;
            const correct = group.querySelector('.correct-answer').value;

            if (question && optionsStr && correct) {
                const options = optionsStr.split(',').map(opt => opt.trim());
                questions.push({ question, options, correct_answer: correct });
            }
        });

        questionsJson.value = JSON.stringify(questions);
    });
});