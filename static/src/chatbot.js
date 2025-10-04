document.addEventListener("DOMContentLoaded", function () {
  // --- CÓDIGO PARA OS MENUS ---
  const mobileMenuToggle = document.querySelector(".mobile-menu-toggle");
  const mobileMenuExpanded = document.querySelector(".mobile-menu-expanded");
  if (mobileMenuToggle && mobileMenuExpanded) {
    mobileMenuToggle.addEventListener("click", function () {
      this.classList.toggle("open");
      mobileMenuExpanded.classList.toggle("open");
    });
  }
  const toggleBtn = document.querySelector(".toggle-btn");
  const verticalSidebar = document.querySelector(".vertical-sidebar");
  if (toggleBtn && verticalSidebar) {
    toggleBtn.addEventListener("click", function () {
      verticalSidebar.classList.toggle("collapsed");
    });
  }
  const mobileMenuItems = document.querySelectorAll(".mobile-expanded-item");
  mobileMenuItems.forEach((item) => {
    item.addEventListener("click", function () {
      mobileMenuExpanded.classList.remove("open");
      mobileMenuToggle.classList.remove("open");
    });
  });

  // --- CÓDIGO PARA ABRIR/FECHAR O CHAT ---
  const chatButton = document.getElementById("chat-button");
  const chatContainer = document.getElementById("chat-container");
  const closeChat = document.getElementById("close-chat");
  if (chatButton && chatContainer) {
    chatButton.addEventListener("click", function () {
      chatContainer.style.display =
        chatContainer.style.display === "flex" ? "none" : "flex";
    });
  }
  if (closeChat && chatContainer) {
    closeChat.addEventListener("click", function () {
      chatContainer.style.display = "none";
    });
  }

  // --- INÍCIO: LÓGICA DO CHATBOT ---
  const sendButton = document.getElementById("send-button");
  const chatInput = document.getElementById("chat-input");
  const chatMessages = document.getElementById("chat-messages");

  const sendMessage = async () => {
    const message = chatInput.value.trim();
    if (!message) return;

    // Exibe a mensagem do usuário
    const userMsgDiv = document.createElement("div");
    userMsgDiv.className = "message user";
    userMsgDiv.innerHTML = `<div class="message-content"><p>${message}</p></div>`;
    chatMessages.appendChild(userMsgDiv);
    chatInput.value = "";
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Exibe um indicador de "digitando..."
    const botTypingDiv = document.createElement("div");
    botTypingDiv.className = "message bot";
    botTypingDiv.innerHTML = `<div class="message-content"><p class="typing-indicator"><span></span><span></span><span></span></p></div>`;
    chatMessages.appendChild(botTypingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
      // Envia a mensagem para o backend
      const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mensagem: message }),
      });

      if (!response.ok) {
        throw new Error(`Erro na requisição: ${response.status}`);
      }

      const data = await response.json();

      // Remove o indicador de "digitando"
      chatMessages.removeChild(botTypingDiv);

      // Exibe a resposta do bot
      const botMsgDiv = document.createElement("div");
      botMsgDiv.className = "message bot";
      botMsgDiv.innerHTML = `<div class="message-content"><p>${data.resposta}</p></div>`;
      chatMessages.appendChild(botMsgDiv);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    } catch (error) {
      console.error("Erro ao enviar mensagem:", error);
      // Em caso de erro, remove o indicador e mostra uma mensagem de falha
      chatMessages.removeChild(botTypingDiv);
      const errorMsgDiv = document.createElement("div");
      errorMsgDiv.className = "message bot";
      errorMsgDiv.innerHTML = `<div class="message-content"><p>Desculpe, ocorreu um erro. Tente novamente mais tarde.</p></div>`;
      chatMessages.appendChild(errorMsgDiv);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
  };

  if (sendButton && chatInput && chatMessages) {
    // Envia a mensagem ao clicar no botão
    sendButton.addEventListener("click", sendMessage);
    // Envia a mensagem ao pressionar "Enter"
    chatInput.addEventListener("keypress", function (e) {
      if (e.key === "Enter") {
        sendMessage();
      }
    });
  }
  // --- FIM: LÓGICA DO CHATBOT ---
});
