// Translation object
const translations = {
    en: {
        "chatbot-title": "Chatbot - Eduvia",
        "chatbot-meta-desc": "Interact with Eduvia's chatbot. Ask questions about programming, mathematics, English, or our platform!",
        "chatbot-meta-keywords": "Eduvia, chatbot, online learning, programming, mathematics, English",
        "chatbot-og-title": "Chatbot - Eduvia",
        "chatbot-og-desc": "Interact with Eduvia's chatbot. Ask questions about programming, mathematics, English, or our platform!",
        "chatbot-twitter-title": "Chatbot - Eduvia",
        "chatbot-twitter-desc": "Interact with Eduvia's chatbot. Ask questions about programming, mathematics, English, or our platform!",
        "chatbot-hero-title": "Welcome to Eduvia's Chatbot",
        "chatbot-hero-desc": "Eduvia's Chatbot is here to help you with programming, mathematics, and English. Feel free to ask any questions related to these topics or our platform!",
        "chatbot-hero-btn": "Start Chatting",
        "chatbot-input-placeholder": "Type your message here...",
        "chatbot-send": "Send",
        "chatbot-loading": "Loading...",
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
        "search-placeholder": "Search for a course...",
        "search-btn": "Search",
        "footer-text": "© 2025 Eduvia. All rights reserved."
    },
    ar: {
        "chatbot-title": "روبوت الدردشة - إدوفيا",
        "chatbot-meta-desc": "تفاعل مع روبوت الدردشة الخاص بـ إدوفيا. اطرح أسئلتك حول البرمجة، الرياضيات، الإنجليزية، أو منصتنا!",
        "chatbot-meta-keywords": "إدوفيا، روبوت الدردشة، التعلم عبر الإنترنت، البرمجة، الرياضيات، الإنجليزية",
        "chatbot-og-title": "روبوت الدردشة - إدوفيا",
        "chatbot-og-desc": "تفاعل مع روبوت الدردشة الخاص بـ إدوفيا. اطرح أسئلتك حول البرمجة، الرياضيات، الإنجليزية، أو منصتنا!",
        "chatbot-twitter-title": "روبوت الدردشة - إدوفيا",
        "chatbot-twitter-desc": "تفاعل مع روبوت الدردشة الخاص بـ إدوفيا. اطرح أسئلتك حول البرمجة، الرياضيات، الإنجليزية، أو منصتنا!",
        "chatbot-hero-title": "مرحبًا بك في روبوت الدردشة الخاص بإدوفيا",
        "chatbot-hero-desc": "روبوت الدردشة الخاص بإدوفيا هنا لمساعدتك في البرمجة، الرياضيات، والإنجليزية. لا تتردد في طرح أي أسئلة تتعلق بهذه المواضيع أو منصتنا!",
        "chatbot-hero-btn": "ابدأ الدردشة",
        "chatbot-input-placeholder": "اكتب رسالتك هنا...",
        "chatbot-send": "إرسال",
        "chatbot-loading": "جارٍ التحميل...",
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
        "search-placeholder": "ابحث عن دورة...",
        "search-btn": "ابحث",
        "footer-text": "© 2025 إدوفيا. جميع الحقوق محفوظة."
    }
};

function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    return null;
}

function sendMessage() {
    const inputField = document.getElementById("user-input");
    const sendButton = document.getElementById("send-button");
    const messagesDiv = document.getElementById("chat-messages");
    const loadingDiv = document.getElementById("loading");
    const errorDiv = document.getElementById("error-message");
    const userMessage = inputField.value.trim();

    if (userMessage) {
        // Show user message
        const userMessageDiv = document.createElement("div");
        userMessageDiv.className = "user-message";
        userMessageDiv.innerHTML = `<div class="message">${userMessage}</div>`;
        messagesDiv.appendChild(userMessageDiv);

        // Disable button and show loading
        sendButton.disabled = true;
        loadingDiv.style.display = "block";
        errorDiv.textContent = "";

        fetch(window.location.href, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({ message: userMessage })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to connect to the server: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            const botMessageDiv = document.createElement("div");
            botMessageDiv.className = "bot-message";
            botMessageDiv.innerHTML = `<div class="message">${data.response}</div>`;
            messagesDiv.appendChild(botMessageDiv);

            inputField.value = "";
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        })
        .catch(error => {
            errorDiv.textContent = translations[document.getElementById('html-root').getAttribute('lang')]["chatbot-error"] + error.message;
            console.error('There was a problem with the fetch operation:', error);
        })
        .finally(() => {
            // Re-enable button and hide loading
            sendButton.disabled = false;
            loadingDiv.style.display = "none";
        });
    }
}

function toggleMenu() {
    const menu = document.querySelector('.menu');
    menu.classList.toggle('active');
}

// Dark Mode Toggle
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

// Language Toggle
function toggleLanguage() {
    const htmlRoot = document.getElementById('html-root');
    const currentLang = htmlRoot.getAttribute('lang');
    const newLang = currentLang === 'en' ? 'ar' : 'en';
    
    // Update lang and direction
    htmlRoot.setAttribute('lang', newLang);
    htmlRoot.setAttribute('dir', newLang === 'ar' ? 'rtl' : 'ltr');
    
    // Update all translatable elements
    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        const text = translations[newLang][key];
        if (element.tagName.toLowerCase() === 'meta') {
            if (element.getAttribute('name') === 'description' || element.getAttribute('name') === 'keywords') {
                element.setAttribute('content', text);
            } else if (element.getAttribute('property')?.startsWith('og:') || element.getAttribute('name')?.startsWith('twitter:')) {
                element.setAttribute('content', text);
            }
        } else if (element.tagName.toLowerCase() === 'input' && element.getAttribute('type') === 'text') {
            element.setAttribute('placeholder', text);
        } else {
            element.textContent = text;
        }
    });

    // Update the title
    document.title = translations[newLang]["chatbot-title"];
    
    localStorage.setItem('language', newLang);
}

// Apply saved theme and language on page load
document.addEventListener('DOMContentLoaded', () => {
    // Apply Dark Mode
    const savedTheme = localStorage.getItem('theme');
    const toggleIcon = document.querySelector('.dark-mode-toggle i');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        toggleIcon.classList.remove('fa-moon');
        toggleIcon.classList.add('fa-sun');
    }

    // Apply Language
    const savedLang = localStorage.getItem('language') || 'en';
    const htmlRoot = document.getElementById('html-root');
    htmlRoot.setAttribute('lang', savedLang);
    htmlRoot.setAttribute('dir', savedLang === 'ar' ? 'rtl' : 'ltr');

    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        const text = translations[savedLang][key];
        if (element.tagName.toLowerCase() === 'meta') {
            if (element.getAttribute('name') === 'description' || element.getAttribute('name') === 'keywords') {
                element.setAttribute('content', text);
            } else if (element.getAttribute('property')?.startsWith('og:') || element.getAttribute('name')?.startsWith('twitter:')) {
                element.setAttribute('content', text);
            }
        } else if (element.tagName.toLowerCase() === 'input' && element.getAttribute('type') === 'text') {
            element.setAttribute('placeholder', text);
        } else {
            element.textContent = text;
        }
    });

    document.title = translations[savedLang]["chatbot-title"];
});

// Enable sending message with Enter key
document.getElementById("user-input").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        sendMessage();
    }
});
