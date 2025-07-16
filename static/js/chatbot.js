/**
 * Chatbot Assistant JavaScript
 * Provides FAQ functionality with hardcoded responses for common queries
 */

class ChatbotAssistant {
    constructor() {
        this.isOpen = false;
        this.isTyping = false;
        this.messages = [];
        this.init();
    }

    init() {
        this.createWidget();
        this.bindEvents();
        this.showWelcomeMessage();
    }

    createWidget() {
        const widgetHTML = `
            <div class="chatbot-widget">
                <button class="chatbot-toggle" id="chatbotToggle">
                    <i class="fas fa-comments"></i>
                    <div class="chatbot-notification" id="chatbotNotification" style="display: none;">1</div>
                </button>
                <div class="chatbot-container" id="chatbotContainer">
                    <div class="chatbot-header">
                        <h3>
                            <i class="fas fa-robot"></i>
                            Assistant
                        </h3>
                        <button class="close-btn" id="chatbotClose">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="chatbot-messages" id="chatbotMessages">
                        <!-- Messages will be inserted here -->
                    </div>
                    <div class="chatbot-input">
                        <input type="text" id="chatbotInput" placeholder="Type your question..." maxlength="200">
                        <button id="chatbotSend">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', widgetHTML);
        
        // Store references
        this.toggleBtn = document.getElementById('chatbotToggle');
        this.container = document.getElementById('chatbotContainer');
        this.messagesContainer = document.getElementById('chatbotMessages');
        this.input = document.getElementById('chatbotInput');
        this.sendBtn = document.getElementById('chatbotSend');
        this.closeBtn = document.getElementById('chatbotClose');
        this.notification = document.getElementById('chatbotNotification');
    }

    bindEvents() {
        // Toggle chatbot
        this.toggleBtn.addEventListener('click', () => {
            this.toggleChatbot();
        });

        // Close chatbot
        this.closeBtn.addEventListener('click', () => {
            this.closeChatbot();
        });

        // Send message on button click
        this.sendBtn.addEventListener('click', () => {
            this.sendMessage();
        });

        // Send message on Enter key
        this.input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Focus input when chatbot opens
        this.container.addEventListener('animationend', () => {
            if (this.isOpen) {
                this.input.focus();
            }
        });
    }

    toggleChatbot() {
        if (this.isOpen) {
            this.closeChatbot();
        } else {
            this.openChatbot();
        }
    }

    openChatbot() {
        this.isOpen = true;
        this.container.classList.add('show');
        this.notification.style.display = 'none';
        this.input.focus();
    }

    closeChatbot() {
        this.isOpen = false;
        this.container.classList.remove('show');
    }

    showWelcomeMessage() {
        const welcomeMessage = {
            type: 'bot',
            content: `
                <div class="welcome-message">
                    <h4>👋 Hello! I'm your Student Assistant</h4>
                    <p>I can help you with 5 main areas:</p>
                    <div class="quick-replies">
                        <button class="quick-reply-btn" data-query="academic">📚 Academic</button>
                        <button class="quick-reply-btn" data-query="campus">🏫 Campus Life</button>
                        <button class="quick-reply-btn" data-query="administrative">📋 Administrative</button>
                        <button class="quick-reply-btn" data-query="support">🔧 Support</button>
                        <button class="quick-reply-btn" data-query="help">❓ Help</button>
                    </div>
                </div>
            `
        };
        
        this.addMessage(welcomeMessage);
        
        // Add click handlers for quick reply buttons
        setTimeout(() => {
            const quickReplyBtns = this.messagesContainer.querySelectorAll('.quick-reply-btn');
            quickReplyBtns.forEach(btn => {
                btn.addEventListener('click', () => {
                    const query = btn.getAttribute('data-query');
                    this.handleQuickReply(query);
                });
            });
        }, 100);
    }

    handleQuickReply(query) {
        const queries = {
            'academic': "Tell me about academic information like classes, exams, assignments, and faculty",
            'campus': "Tell me about campus life like library, sports, canteen, hostel, and events",
            'administrative': "Tell me about administrative matters like fees, notices, holidays, and attendance",
            'support': "I need help with technical issues, emergency contacts, or general support",
            'help': "How can you help me with my student queries?"
        };
        
        this.addUserMessage(queries[query]);
        this.processMessage(queries[query]);
    }

    sendMessage() {
        const message = this.input.value.trim();
        if (!message || this.isTyping) return;

        this.addUserMessage(message);
        this.input.value = '';
        this.processMessage(message);
    }

    addUserMessage(content) {
        const message = {
            type: 'user',
            content: content,
            timestamp: new Date()
        };
        
        this.addMessage(message);
    }

    addMessage(message) {
        this.messages.push(message);
        this.renderMessage(message);
        this.scrollToBottom();
    }

    renderMessage(message) {
        const messageHTML = `
            <div class="chatbot-message ${message.type}">
                <div class="message-avatar ${message.type}">
                    <i class="fas fa-${message.type === 'bot' ? 'robot' : 'user'}"></i>
                </div>
                <div class="message-content ${message.type}">
                    ${message.content}
                </div>
            </div>
        `;
        
        this.messagesContainer.insertAdjacentHTML('beforeend', messageHTML);
    }

    showTypingIndicator() {
        const typingHTML = `
            <div class="chatbot-message bot" id="typingIndicator">
                <div class="message-avatar bot">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        
        this.messagesContainer.insertAdjacentHTML('beforeend', typingHTML);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    async processMessage(message) {
        this.isTyping = true;
        this.showTypingIndicator();
        
        // Simulate typing delay
        await this.delay(1000 + Math.random() * 1000);
        
        this.hideTypingIndicator();
        this.isTyping = false;
        
        const response = this.getResponse(message);
        this.addMessage({
            type: 'bot',
            content: response,
            timestamp: new Date()
        });
    }

    getResponse(message) {
        const lowerMessage = message.toLowerCase();
        
        // Define 5 main categories with comprehensive word matching
        const categories = {
            'academic': {
                keywords: ['class', 'schedule', 'timetable', 'exam', 'test', 'quiz', 'assignment', 'homework', 'project', 'faculty', 'teacher', 'professor', 'instructor', 'subject', 'course', 'lecture', 'study', 'academic', 'grade', 'mark', 'score', 'result', 'performance', 'section', 'room', 'classroom', 'lab', 'practical', 'theory', 'syllabus', 'curriculum'],
                response: `
                    📚 <strong>Academic Information:</strong><br><br>
                    <strong>📅 Class Schedule & Timetable:</strong><br>
                    • View current and upcoming classes on the home page<br>
                    • Section-specific timetables available<br>
                    • Real-time schedule updates based on server time (IST)<br>
                    • Automatic holiday detection and schedule hiding<br><br>
                    
                    <strong>📝 Exams & Tests:</strong><br>
                    • All exam schedules posted as notices<br>
                    • Check "Examination" category in notices<br>
                    • Exam dates, times, and venues clearly specified<br>
                    • Guidelines and procedures announced separately<br><br>
                    
                    <strong>📋 Assignments & Projects:</strong><br>
                    • Assignment due dates and submission guidelines<br>
                    • Project requirements and deadlines<br>
                    • Check "Assignment" category in notices<br>
                    • Extension announcements posted separately<br><br>
                    
                    <strong>👨‍🏫 Faculty & Teachers:</strong><br>
                    • Teacher names displayed in timetables<br>
                    • Subject assignments and faculty details<br>
                    • Contact information through department office<br>
                    • Office hours posted as notices<br><br>
                    
                    <strong>🏫 Rooms & Locations:</strong><br>
                    • Class venues and room numbers in timetables<br>
                    • Lab sessions clearly marked<br>
                    • Room changes announced as notices<br>
                    • Special venues and auditoriums listed<br><br>
                    
                    <a href="/timetables" class="btn btn-sm btn-primary">View Timetables</a>
                    <a href="/notices" class="btn btn-sm btn-primary">Check Notices</a>
                `
            },
            
            'campus': {
                keywords: ['library', 'book', 'reference', 'study material', 'sports', 'event', 'competition', 'tournament', 'game', 'cultural', 'canteen', 'food', 'lunch', 'breakfast', 'snack', 'meal', 'cafeteria', 'hostel', 'dormitory', 'accommodation', 'lodging', 'stay', 'transport', 'bus', 'vehicle', 'commute', 'travel', 'transportation', 'route', 'campus', 'facility', 'amenity'],
                response: `
                    🏫 <strong>Campus Life Information:</strong><br><br>
                    <strong>📚 Library & Study:</strong><br>
                    • Library timings and book availability posted as notices<br>
                    • Reference materials and study resources shared<br>
                    • Digital library access through notices<br>
                    • Library rules and guidelines regularly posted<br><br>
                    
                    <strong>⚽ Sports & Events:</strong><br>
                    • Sports competitions and tournaments announced<br>
                    • Cultural programs and events posted<br>
                    • Event registration details provided in notices<br>
                    • Venues and timings clearly mentioned<br>
                    • Results and achievements announced<br><br>
                    
                    <strong>🍽️ Canteen & Food:</strong><br>
                    • Canteen timings and menu updates posted<br>
                    • Special meal arrangements announced<br>
                    • Food safety and hygiene notices shared<br>
                    • Payment options and facilities listed<br><br>
                    
                    <strong>🏠 Hostel & Accommodation:</strong><br>
                    • Hostel rules and regulations posted<br>
                    • Room allotment procedures announced<br>
                    • Hostel fee information shared via notices<br>
                    • Maintenance schedules and visitor policies<br><br>
                    
                    <strong>🚌 Transportation:</strong><br>
                    • Bus routes and transport schedules posted<br>
                    • Route changes and modifications announced<br>
                    • Transport pass application procedures shared<br>
                    • Emergency transport arrangements<br><br>
                    
                    <em>All campus-related updates are posted on the notice board regularly.</em>
                `
            },
            
            'administrative': {
                keywords: ['notice', 'announcement', 'news', 'recent', 'latest', 'holiday', 'break', 'vacation', 'off', 'closed', 'fee', 'payment', 'tuition', 'due', 'attendance', 'present', 'absent', 'policy', 'rule', 'regulation', 'procedure', 'form', 'document', 'certificate', 'administrative', 'official', 'important'],
                response: `
                    📋 <strong>Administrative Information:</strong><br><br>
                    <strong>📢 Notices & Announcements:</strong><br>
                    • Latest announcements on the home page<br>
                    • Complete notice archive available<br>
                    • Category-based filtering (Examination, Assignment, etc.)<br>
                    • File attachments and PDF downloads<br><br>
                    
                    <strong>🏖️ Holidays & Breaks:</strong><br>
                    • Section-specific holiday scheduling<br>
                    • Current holiday status on home page<br>
                    • Automatic schedule hiding during holidays<br>
                    • Resume dates and break periods clearly shown<br><br>
                    
                    <strong>💰 Fees & Payments:</strong><br>
                    • Fee-related information posted as notices<br>
                    • Payment deadlines and procedures detailed<br>
                    • Fee structure changes announced<br>
                    • Scholarship information posted separately<br><br>
                    
                    <strong>✅ Attendance & Policies:</strong><br>
                    • Attendance requirements posted as notices<br>
                    • Minimum attendance criteria announced<br>
                    • Leave application procedures posted<br>
                    • Attendance tracking by departments<br><br>
                    
                    <strong>📊 Results & Grades:</strong><br>
                    • All results announced through notices<br>
                    • Grade card distribution posted<br>
                    • Revaluation procedures announced<br>
                    • Performance reports and merit lists shared<br><br>
                    
                    <a href="/notices" class="btn btn-sm btn-primary">View All Notices</a>
                `
            },
            
            'support': {
                keywords: ['technical', 'problem', 'issue', 'error', 'not working', 'broken', 'fix', 'support', 'help', 'emergency', 'urgent', 'immediate', 'critical', 'contact', 'assist', 'troubleshoot', 'repair', 'maintenance', 'system', 'login', 'access', 'network', 'internet', 'device', 'hardware', 'software'],
                response: `
                    🔧 <strong>Support & Technical Assistance:</strong><br><br>
                    <strong>🔧 Technical Support:</strong><br>
                    • Contact IT department for technical issues<br>
                    • Report system problems to IT support<br>
                    • Login and access issues handled by system administrator<br>
                    • Hardware and device problems reported to IT<br>
                    • Network and internet connectivity issues<br><br>
                    
                    <strong>🚨 Emergency Support:</strong><br>
                    • Emergency contact numbers posted<br>
                    • First aid procedures and emergency protocols<br>
                    • Safety guidelines and emergency alerts<br>
                    • Immediate assistance through security office<br><br>
                    
                    <strong>📞 General Support:</strong><br>
                    • Contact system administrator for access issues<br>
                    • Department heads for urgent matters<br>
                    • IT department for technical problems<br>
                    • Security office for emergency situations<br><br>
                    
                    <strong>💼 Career Support:</strong><br>
                    • Job opportunities posted as notices<br>
                    • Placement drives and internship information<br>
                    • Career guidance sessions announced<br>
                    • Resume building workshops posted<br><br>
                    
                    <em>For immediate assistance, contact the appropriate department directly.</em>
                `
            },
            
            'help': {
                keywords: ['help', 'how', 'what', 'guide', 'tutorial', 'assist', 'support', 'information', 'tell', 'explain', 'show', 'find', 'where', 'when', 'who', 'why', 'can you', 'do you', 'know', 'understand'],
                response: `
                    ❓ <strong>How can I help you?</strong><br><br>
                    I can assist you with 5 main areas:<br><br>
                    
                    <strong>📚 Academic:</strong> Classes, schedules, exams, assignments, faculty, rooms, sections<br>
                    <strong>🏫 Campus Life:</strong> Library, sports, events, canteen, hostel, transport<br>
                    <strong>📋 Administrative:</strong> Notices, holidays, fees, attendance, results, policies<br>
                    <strong>🔧 Support:</strong> Technical issues, emergency contacts, career guidance<br>
                    <strong>❓ Help:</strong> General assistance and guidance<br><br>
                    
                    Just ask me anything about these areas, and I'll provide detailed information!
                `
            }
        };
        
        // Intelligent word-based matching
        let bestMatch = null;
        let highestScore = 0;
        
        for (const [category, data] of Object.entries(categories)) {
            let score = 0;
            const words = lowerMessage.split(' ');
            
            // Check each word against category keywords
            for (const word of words) {
                if (data.keywords.some(keyword => word.includes(keyword) || keyword.includes(word))) {
                    score += 1;
                }
            }
            
            // Bonus for exact matches
            for (const keyword of data.keywords) {
                if (lowerMessage.includes(keyword)) {
                    score += 2;
                }
            }
            
            if (score > highestScore) {
                highestScore = score;
                bestMatch = category;
            }
        }
        
        // Return response based on best match
        if (bestMatch && highestScore > 0) {
            return categories[bestMatch].response;
        }
        
        // Default response for unrecognized queries
        return `
            🤔 <strong>I'm not sure about that.</strong><br><br>
            I can help you with 5 main areas:<br>
            • 📚 <strong>Academic:</strong> Classes, exams, assignments, faculty<br>
            • 🏫 <strong>Campus Life:</strong> Library, sports, canteen, hostel, transport<br>
            • 📋 <strong>Administrative:</strong> Notices, holidays, fees, attendance<br>
            • 🔧 <strong>Support:</strong> Technical issues, emergency contacts<br>
            • ❓ <strong>Help:</strong> General assistance<br><br>
            Try asking about any of these areas, or type "help" for more options.
        `;
    }

    scrollToBottom() {
        setTimeout(() => {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }, 100);
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Show notification badge
    showNotification() {
        if (!this.isOpen) {
            this.notification.style.display = 'flex';
        }
    }

    // Hide notification badge
    hideNotification() {
        this.notification.style.display = 'none';
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatbot = new ChatbotAssistant();
    
    // Show notification after 5 seconds if chatbot hasn't been opened
    setTimeout(() => {
        if (!window.chatbot.isOpen) {
            window.chatbot.showNotification();
        }
    }, 5000);
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ChatbotAssistant };
} 