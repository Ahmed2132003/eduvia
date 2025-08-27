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
        "chatbot-chats-title": "Your Chats",
        "chatbot-new-chat": "New Chat",
        "chatbot-no-chats": "No chats yet.",
        "chatbot-message-limit": "Messages today: ",
        "chatbot-limit-reached-free": "You have reached the daily message limit (5 messages). Please subscribe to continue chatting.",
        "chatbot-limit-reached-basic": "You have reached the daily message limit (30 messages). Please upgrade to Pro to continue chatting.",
        "chatbot-limit-reached-pro": "You have reached the daily message limit (60 messages). Please upgrade to Premium to continue chatting.",
        "chatbot-subscribe": "Subscribe Now",
        "chatbot-error": "Error: ",
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
        "footer-text": "© 2025 Eduvia and creativitycode. All rights reserved."
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
        "chatbot-chats-title": "محادثاتك",
        "chatbot-new-chat": "محادثة جديدة",
        "chatbot-no-chats": "لا توجد محادثات بعد.",
        "chatbot-message-limit": "الرسائل اليوم: ",
        "chatbot-limit-reached-free": "لقد وصلت إلى الحد الأقصى للرسائل اليومية (5 رسائل). يرجى الاشتراك لمواصلة الدردشة.",
        "chatbot-limit-reached-basic": "لقد وصلت إلى الحد الأقصى للرسائل اليومية (30 رسالة). يرجى ترقية باقتك إلى Pro لمواصلة الدردشة.",
        "chatbot-limit-reached-pro": "لقد وصلت إلى الحد الأقصى للرسائل اليومية (60 رسالة). يرجى ترقية باقتك إلى Premium لمواصلة الدردشة.",
        "chatbot-subscribe": "اشترك الآن",
        "chatbot-error": "خطأ: ",
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
        "footer-text": "© 2025 إدوفيا و كريتيفيتي كود . جميع الحقوق محفوظة."
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

async function sendMessage() {
    const inputField = document.getElementById("user-input");
    const sendButton = document.getElementById("send-button");
    const messagesDiv = document.getElementById("chat-messages");
    const loadingDiv = document.getElementById("loading");
    const errorDiv = document.getElementById("error-message");
    const userMessage = inputField.value.trim();

    if (!userMessage) {
        errorDiv.textContent = translations[document.getElementById('html-root').getAttribute('lang')]["chatbot-error"] + "Message cannot be empty";
        return;
    }

    // Show user message
    const userMessageDiv = document.createElement("div");
    userMessageDiv.className = "message user-message";
    userMessageDiv.textContent = userMessage;
    messagesDiv.appendChild(userMessageDiv);

    // Disable button and show loading
    sendButton.disabled = true;
    loadingDiv.style.display = "block";
    errorDiv.textContent = "";

    try {
        const response = await fetch(window.location.href, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({ message: userMessage })
        });

        const data = await response.json();

        if (data.redirect) {
            window.location.href = data.redirect;
            return;
        }

        if (data.error) {
            errorDiv.textContent = translations[document.getElementById('html-root').getAttribute('lang')]["chatbot-error"] + data.error;
        } else {
            const botMessageDiv = document.createElement("div");
            botMessageDiv.className = "message bot-message";
            botMessageDiv.textContent = data.response;
            messagesDiv.appendChild(botMessageDiv);

            // Update chat list if new chat was created
            if (data.chat_id && !document.querySelector(`.sidebar ul li a[href="/chatbot/${data.chat_id}/"]`)) {
                const chatList = document.querySelector('.sidebar ul');
                const newChatItem = document.createElement('li');
                newChatItem.innerHTML = `<a href="/chatbot/${data.chat_id}/" class="active">${data.chat_title} (${new Date().toLocaleString()})</a>`;
                chatList.insertBefore(newChatItem, chatList.firstChild);
                document.querySelectorAll('.sidebar ul li a').forEach(link => {
                    if (link.getAttribute('href') !== `/chatbot/${data.chat_id}/`) {
                        link.classList.remove('active');
                    }
                });
            }

            inputField.value = "";
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
    } catch (error) {
        errorDiv.textContent = translations[document.getElementById('html-root').getAttribute('lang')]["chatbot-error"] + error.message;
        console.error('There was a problem with the fetch operation:', error);
    } finally {
        sendButton.disabled = false;
        loadingDiv.style.display = "none";
    }
}

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

    document.title = translations[newLang]["chatbot-title"];
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

    document.getElementById("user-input").addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            sendMessage();
        }
    });

    // Clear current chat ID on New Chat click
    document.querySelector('.new-chat-btn').addEventListener('click', () => {
        localStorage.removeItem('currentChatId');
    });
});