// URL base de nuestra API - ¡IMPORTANTE! Usa la misma que donde corre FastAPI
// Asegúrate de que esta URL sea correcta
// Debe ser el mismo puerto donde corre FastAPI (8000)
const API_BASE_URL = 'http://localhost:8000';
// También puedes usar:
// const API_BASE_URL = 'http://127.0.0.1:8000';

// Elementos del DOM
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatMessages = document.getElementById('chat-messages');

// Función para añadir un mensaje al chat
function addMessage(message, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    const messageText = document.createElement('p');
    messageText.textContent = message;
    
    messageContent.appendChild(messageText);
    messageDiv.appendChild(messageContent);
    chatMessages.appendChild(messageDiv);
    
    // Auto-scroll to the bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Función para enviar mensaje al chatbot
async function sendMessageToChatbot(message) {
    try {
        // Mostrar un indicador de "escribiendo..." (puedes mejorarlo luego)
        // addMessage("Escribiendo...", false);
        
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }

        const data = await response.json();
        return data.response;
        
    } catch (error) {
        console.error('Error al comunicarse con la API:', error);
        return 'Lo siento, hubo un error al procesar tu solicitud.';
    }
}

// Manejar el envío del formulario
chatForm.addEventListener('submit', async function(event) {
    event.preventDefault(); // Prevenir el comportamiento por defecto del formulario
    
    const message = userInput.value.trim();
    
    if (!message) return; // No enviar mensajes vacíos
    
    // Añadir mensaje del usuario al chat y limpiar el input
    addMessage(message, true);
    userInput.value = '';
    
    // Obtener y mostrar la respuesta del chatbot
    const botResponse = await sendMessageToChatbot(message);
    addMessage(botResponse, false);
});

// Focus en el input al cargar la página
userInput.focus();

// Opcional: Permitir enviar con Enter (ya lo hace el formulario, pero por si acaso)
userInput.addEventListener('keypress', function(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
});