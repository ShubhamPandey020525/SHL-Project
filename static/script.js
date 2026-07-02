
const API_BASE = '';

let messages = [];
let hasStarted = false;

const messagesDiv = document.getElementById('messages');
const chatContainer = document.getElementById('chatContainer');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const welcomeMessage = document.getElementById('welcomeMessage');

// Auto-resize textarea
function autoResize() {
    userInput.style.height = 'auto';
    userInput.style.height = Math.min(userInput.scrollHeight, 200) + 'px';
}

// Scroll to bottom
function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Update send button state
function updateSendButton() {
    const hasContent = userInput.value.trim().length > 0;
    sendBtn.disabled = !hasContent;
}

// Add typing indicator
function addTypingIndicator() {
    const indicatorDiv = document.createElement('div');
    indicatorDiv.className = 'message assistant';
    indicatorDiv.id = 'typing-indicator';
    indicatorDiv.innerHTML = `
        <div class="message-wrapper">
            <div class="message-avatar">SHL</div>
            <div class="message-content-wrapper">
                <div class="message-bubble">
                    <div class="typing-indicator">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>
                </div>
            </div>
        </div>
    `;
    messagesDiv.appendChild(indicatorDiv);
    scrollToBottom();
}

// Remove typing indicator
function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// Add message
function addMessage(content, role, recommendations = []) {
    if (hasStarted && welcomeMessage) {
        welcomeMessage.remove();
    }
    hasStarted = true;

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    let recHtml = '';
    if (recommendations && recommendations.length > 0) {
        recHtml = '<div class="recommendations">';
        recommendations.forEach(rec => {
            const badgeClass = rec.test_type === 'P' ? 'personality' : 'knowledge';
            const badgeText = rec.test_type === 'P' ? 'Personality' : 'Knowledge/Skill';
            recHtml += `
                <div class="recommendation-card">
                    <h4>${rec.name}</h4>
                    <a href="${rec.url}" target="_blank" rel="noopener noreferrer">${rec.url}</a>
                    <span class="badge ${badgeClass}">${badgeText}</span>
                </div>
            `;
        });
        recHtml += '</div>';
    }

    // Escape HTML and render newlines
    const safeContent = content
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\n/g, '<br>');
    
    messageDiv.innerHTML = `
        <div class="message-wrapper">
            <div class="message-avatar">${role === 'user' ? 'You' : 'SHL'}</div>
            <div class="message-content-wrapper">
                <div class="message-bubble">${safeContent}</div>
                ${recHtml}
            </div>
        </div>
    `;

    messagesDiv.appendChild(messageDiv);
    scrollToBottom();
}

// Send message
async function sendMessage(content) {
    if (!content) return;

    addMessage(content, 'user');
    messages.push({ role: 'user', content });
    userInput.value = '';
    autoResize();
    updateSendButton();
    sendBtn.disabled = true;

    addTypingIndicator();

    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ messages })
        });

        const data = await response.json();
        
        removeTypingIndicator();
        
        addMessage(data.reply, 'assistant', data.recommendations);
        messages.push({ role: 'assistant', content: data.reply });
    } catch (error) {
        removeTypingIndicator();
        addMessage('Sorry, there was an error. Please try again.', 'assistant');
    } finally {
        updateSendButton();
    }
}

// Event listeners
sendBtn.addEventListener('click', () => {
    sendMessage(userInput.value.trim());
});

userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage(userInput.value.trim());
    }
});

userInput.addEventListener('input', () => {
    autoResize();
    updateSendButton();
});

// Quick suggestions
document.querySelectorAll('.quick-suggestion-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const query = btn.getAttribute('data-query');
        sendMessage(query);
    });
});

// Initial setup
window.onload = () => {
    userInput.focus();
    updateSendButton();
};
