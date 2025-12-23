// Conversation history to maintain context
let conversationHistory = [];

// Handle Enter key press in textarea
document.getElementById('user-input').addEventListener('keydown', function(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});

// Send message to the chat API
async function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();
    
    if (!message) {
        return;
    }
    
    // Disable input and button while processing
    const sendButton = document.getElementById('send-button');
    input.disabled = true;
    sendButton.disabled = true;
    
    // Update button to show loading state
    document.getElementById('send-icon').innerHTML = '<span class="loading"></span>';
    document.getElementById('send-text').textContent = 'Sending...';
    
    // Add user message to chat
    addMessage('user', message);
    
    // Clear input
    input.value = '';
    
    try {
        // Send request to backend
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                history: conversationHistory
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to get response');
        }
        
        const data = await response.json();
        
        // Add assistant response to chat
        addMessage('assistant', data.response);
        
        // Update conversation history
        conversationHistory.push({
            role: 'user',
            content: message
        });
        conversationHistory.push({
            role: 'assistant',
            content: data.response
        });
        
        // Keep history manageable (last 20 messages)
        if (conversationHistory.length > 20) {
            conversationHistory = conversationHistory.slice(-20);
        }
        
    } catch (error) {
        console.error('Error:', error);
        addErrorMessage(`Error: ${error.message}`);
    } finally {
        // Re-enable input and button
        input.disabled = false;
        sendButton.disabled = false;
        document.getElementById('send-icon').innerHTML = '📤';
        document.getElementById('send-text').textContent = 'Send';
        input.focus();
    }
}

// Add a message to the chat display
function addMessage(role, content) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Format the message
    const roleLabel = role === 'user' ? 'You' : 'Assistant';
    
    // Convert markdown-like formatting to HTML
    let formattedContent = content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // Bold
        .replace(/\*(.*?)\*/g, '<em>$1</em>')              // Italic
        .replace(/`(.*?)`/g, '<code>$1</code>')            // Code
        .replace(/\n/g, '<br>');                           // Line breaks
    
    contentDiv.innerHTML = `<strong>${roleLabel}:</strong> ${formattedContent}`;
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Add an error message to the chat display
function addErrorMessage(errorText) {
    const chatMessages = document.getElementById('chat-messages');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = `<strong>⚠️ Error:</strong> ${errorText}`;
    chatMessages.appendChild(errorDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Check health status on page load
async function checkHealth() {
    try {
        const response = await fetch('/api/health');
        const health = await response.json();
        console.log('Health check:', health);
        
        // Show warning if services are not configured
        if (!health.azure_ai_configured || !health.mcp_endpoints_configured) {
            let warnings = [];
            if (!health.azure_ai_configured) {
                warnings.push('Azure AI is not configured');
            }
            if (!health.mcp_endpoints_configured) {
                warnings.push('MCP endpoints are not configured');
            }
            console.warn('Configuration issues:', warnings.join(', '));
        }
    } catch (error) {
        console.error('Health check failed:', error);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    checkHealth();
    document.getElementById('user-input').focus();
});
