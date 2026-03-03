import './style.css';
import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL;
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY;
const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

const app = document.querySelector('#app');

app.innerHTML = `
  <div class="container">
    <header class="header">
      <div class="logo">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <path d="M14 2v6h6"/>
          <path d="M16 13H8"/>
          <path d="M16 17H8"/>
          <path d="M10 9H8"/>
        </svg>
        <h1>مساعد القانون السعودي</h1>
      </div>
      <p class="subtitle">استفسر عن الأنظمة واللوائح السعودية بالذكاء الاصطناعي</p>
    </header>

    <main class="main">
      <div class="chat-container">
        <div id="messages" class="messages">
          <div class="message assistant">
            <div class="message-content">
              <p>مرحباً! أنا مساعدك للاستفسار عن الأنظمة واللوائح السعودية.</p>
              <p>يمكنك أن تسألني عن أي موضوع قانوني، مثل:</p>
              <ul>
                <li>ما هي ساعات العمل القانونية؟</li>
                <li>ماذا يقول النظام الأساسي للحكم؟</li>
                <li>ما هي حقوق العامل في الإجازات؟</li>
              </ul>
            </div>
          </div>
        </div>

        <form id="chat-form" class="input-container">
          <input
            type="text"
            id="question-input"
            placeholder="اكتب سؤالك القانوني هنا..."
            autocomplete="off"
            required
          />
          <button type="submit" id="send-button">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="22" y1="2" x2="11" y2="13"/>
              <polygon points="22 2 15 22 11 13 2 9 22 2"/>
            </svg>
            <span>إرسال</span>
          </button>
        </form>
      </div>
    </main>

    <footer class="footer">
      <p>⚠️ هذا النظام للأغراض التعليمية فقط. للحصول على استشارة قانونية رسمية، يرجى الرجوع إلى محامٍ مرخص.</p>
    </footer>
  </div>
`;

const messagesContainer = document.getElementById('messages');
const chatForm = document.getElementById('chat-form');
const questionInput = document.getElementById('question-input');
const sendButton = document.getElementById('send-button');

function addMessage(content, isUser = false, citations = []) {
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;

  let citationsHtml = '';
  if (citations && citations.length > 0) {
    citationsHtml = `
      <div class="citations">
        <h4>المصادر القانونية:</h4>
        <ul>
          ${citations.map(citation => `
            <li>
              <strong>${citation.law_name}</strong>
              ${citation.article_number ? `- المادة ${citation.article_number}` : ''}
            </li>
          `).join('')}
        </ul>
      </div>
    `;
  }

  messageDiv.innerHTML = `
    <div class="message-content">
      <p>${content}</p>
      ${citationsHtml}
    </div>
  `;

  messagesContainer.appendChild(messageDiv);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showTypingIndicator() {
  const typingDiv = document.createElement('div');
  typingDiv.className = 'message assistant typing';
  typingDiv.id = 'typing-indicator';
  typingDiv.innerHTML = `
    <div class="message-content">
      <div class="typing-dots">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
  `;
  messagesContainer.appendChild(typingDiv);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function hideTypingIndicator() {
  const typingIndicator = document.getElementById('typing-indicator');
  if (typingIndicator) {
    typingIndicator.remove();
  }
}

function setLoading(loading) {
  sendButton.disabled = loading;
  questionInput.disabled = loading;

  if (loading) {
    sendButton.classList.add('loading');
    showTypingIndicator();
  } else {
    sendButton.classList.remove('loading');
    hideTypingIndicator();
  }
}

async function askQuestion(question) {
  try {
    setLoading(true);
    addMessage(question, true);

    const response = await fetch(`${SUPABASE_URL}/functions/v1/query-law`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    addMessage(data.answer, false, data.citations);

  } catch (error) {
    console.error('Error:', error);
    addMessage('عذراً، حدث خطأ أثناء معالجة سؤالك. يرجى المحاولة مرة أخرى.', false);
  } finally {
    setLoading(false);
  }
}

chatForm.addEventListener('submit', async (e) => {
  e.preventDefault();

  const question = questionInput.value.trim();
  if (!question) return;

  questionInput.value = '';
  await askQuestion(question);
});

questionInput.focus();
