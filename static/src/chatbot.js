const chatButton = document.getElementById('chat-button');
const chatContainer = document.getElementById('chat-container');
const chatInput = document.getElementById('chat-input');
const chatMessages = document.getElementById('chat-messages');

chatButton.addEventListener('click', () => {
    chatContainer.style.display = chatContainer.style.display === 'flex' ? 'none' : 'flex';
});

chatInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter' && this.value.trim()) {
        const userMessage = this.value.trim();

        // Adiciona a mensagem do usuário ao chat
        const msg = document.createElement('div');
        msg.className = 'message user';
        msg.textContent = userMessage;
        chatMessages.appendChild(msg);
        this.value = '';

        fetch('/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: userMessage })
        })
        .then(response => response.json())
        .then(data => {
            // Adiciona a resposta do bot ao chat
            const reply = document.createElement('div');
            reply.className = 'message bot';
            reply.textContent = data.reply || 'Desculpe, não entendi.';
            chatMessages.appendChild(reply);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        })
        .catch(error => {
            console.error('Erro ao enviar a mensagem:', error);
            const errorReply = document.createElement('div');
            errorReply.className = 'message bot';
            errorReply.textContent = 'Erro ao conectar com o servidor.';
            chatMessages.appendChild(errorReply);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        });
    }
});
