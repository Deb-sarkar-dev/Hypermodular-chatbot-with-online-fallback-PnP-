(function () {
    // Inject CSS
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'http://localhost:5000/static/chat-widget.css'; // Make sure this matches your Flask server path
    document.head.appendChild(link);

    // Backend URL
    const API_BASE = 'http://localhost:5000';

    // Build UI
    const widgetContainer = document.createElement('div');
    widgetContainer.id = 'rag-chat-widget';

    widgetContainer.innerHTML = `
        <div id="rag-chat-window">
            <div id="rag-chat-header">
                <div class="title">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                    Site Assistant
                </div>
                <button id="rag-close-btn">&times;</button>
            </div>
            <div id="rag-chat-messages">
                <div class="rag-message ai">Hi there! I'm the Site Assistant. How can I help you today?</div>
            </div>
            <div id="rag-chat-input-container">
                <input type="text" id="rag-chat-input" placeholder="Type your message..." />
                <button id="rag-send-btn">
                    <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path></svg>
                </button>
            </div>
        </div>
        <div id="rag-chat-bubble">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/></svg>
        </div>
    `;

    document.body.appendChild(widgetContainer);

    // Elements
    const bubble = document.getElementById('rag-chat-bubble');
    const chatWindow = document.getElementById('rag-chat-window');
    const closeBtn = document.getElementById('rag-close-btn');
    const inputField = document.getElementById('rag-chat-input');
    const sendBtn = document.getElementById('rag-send-btn');
    const messagesContainer = document.getElementById('rag-chat-messages');

    let currentURL = window.location.href;

    // Toggle Window
    bubble.addEventListener('click', () => {
        chatWindow.classList.add('open');
        bubble.style.display = 'none';
    });

    closeBtn.addEventListener('click', () => {
        chatWindow.classList.remove('open');
        setTimeout(() => { bubble.style.display = 'flex'; }, 300);
    });

    // Ingest Site Content on Load
    function ingestSiteContent() {
        const content = document.body.innerText;
        console.log("RAG Widget: Sending site content to backend for ingestion...");

        fetch(`${API_BASE}/ingest`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url: currentURL,
                content: content
            })
        })
            .then(res => res.json())
            .then(data => console.log("RAG Widget Ingestion:", data.message))
            .catch(err => console.error("RAG Widget Ingestion Error:", err));
    }

    // Call ingest initially
    setTimeout(ingestSiteContent, 1000);

    // Handle Sending Messages
    function addMessage(text, sender, queryContext = "") {
        const msgDiv = document.createElement('div');
        msgDiv.className = `rag-message ${sender}`;
        msgDiv.innerText = text;

        if (sender === 'ai') {
            const feedbackDiv = document.createElement('div');
            feedbackDiv.className = 'rag-feedback';

            const upBtn = document.createElement('button');
            upBtn.className = 'rag-feedback-btn';
            upBtn.innerHTML = '👍';

            const downBtn = document.createElement('button');
            downBtn.className = 'rag-feedback-btn';
            downBtn.innerHTML = '👎';

            const handleFeedback = (rating, btn) => {
                upBtn.disabled = true;
                downBtn.disabled = true;
                btn.classList.add('active');

                fetch(`${API_BASE}/feedback`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        url: currentURL,
                        query: queryContext,
                        response: text,
                        rating: rating
                    })
                }).then(res => res.json()).then(data => console.log("Feedback recorded:", data));
            };

            upBtn.onclick = () => handleFeedback('positive', upBtn);
            downBtn.onclick = () => handleFeedback('negative', downBtn);

            feedbackDiv.appendChild(upBtn);
            feedbackDiv.appendChild(downBtn);
            msgDiv.appendChild(feedbackDiv);
        }

        messagesContainer.appendChild(msgDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function showTyping() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'rag-typing';
        typingDiv.id = 'rag-typing-indicator';
        typingDiv.innerHTML = '<div class="rag-dot"></div><div class="rag-dot"></div><div class="rag-dot"></div>';
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function hideTyping() {
        const indicator = document.getElementById('rag-typing-indicator');
        if (indicator) indicator.remove();
    }

    function sendMessage() {
        const text = inputField.value.trim();
        if (!text) return;

        addMessage(text, 'user');
        inputField.value = '';
        showTyping();

        fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url: currentURL,
                message: text
            })
        })
            .then(res => res.json())
            .then(data => {
                hideTyping();
                addMessage(data.response, 'ai', text);
            })
            .catch(err => {
                hideTyping();
                addMessage("Sorry, I'm having trouble connecting to the server.", 'ai');
                console.error(err);
            });
    }

    sendBtn.addEventListener('click', sendMessage);
    inputField.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

})();
