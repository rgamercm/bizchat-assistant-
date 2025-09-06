from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.chatbot import Chatbot  # Importamos nuestra clase Chatbot

# Usaremos un diccionario para almacenar instancias de chatbot por sesión
# En una app real, usarías cookies o bases de datos para sessions
user_sessions = {}

def get_chatbot_for_session(session_id: str) -> Chatbot:
    """Obtiene o crea una instancia de chatbot para una sesión específica."""
    if session_id not in user_sessions:
        user_sessions[session_id] = Chatbot('data/knowledge_base.json', max_history=5)
        print(f"Nueva sesión creada: {session_id}")
    return user_sessions[session_id]


# Define un modelo Pydantic para la estructura de la solicitud (request)
# Esto valida automáticamente que los datos entrantes tengan el formato correcto.
class ChatRequest(BaseModel):
    message: str

# Define un modelo Pydantic para la estructura de la respuesta (response)
class ChatResponse(BaseModel):
    response: str

# Instancia la aplicación FastAPI
app = FastAPI(
    title="BizChat Assistant API",
    description="Una API para un chatbot conversacional de dominio específico.",
    version="1.0.0"
)

# Configura CORS (Crucial para que el frontend se comunique con el backend)
# Esto le dice al backend que acepte requests desde el origen (frontend) que especificaremos.
# Configura CORS - SOLUCIÓN DEFINITIVA para desarrollo local
# Permite cualquier puerto de localhost (127.0.0.1) y localhost
origins = [
    "http://localhost",       # Permite cualquier puerto de localhost
    "http://localhost:*",     # Patrón comodín para cualquier puerto (algunos middleware lo soportan)
    "http://127.0.0.1",       # Permite cualquier puerto de 127.0.0.1  
    "http://127.0.0.1:*",     # Patrón comodín para cualquier puerto
]

# Si lo anterior no funciona, usa esta alternativa más agresiva pero efectiva:
# origins = ["*"]  # ¡CUIDADO! Esto permite todos los orígenes, solo para desarrollo local

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",  # Regex para localhost en cualquier puerto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Instancia global del chatbot
# Se crea al iniciar la aplicación y estará disponible para todos los requests.
chatbot = Chatbot('data/knowledge_base.json')

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest, session_id: str = "default"):
    """
    Endpoint para enviar un mensaje al chatbot y recibir su respuesta.

    - **message**: El mensaje/texto del usuario.
    - **session_id**: ID de sesión para mantener contexto (opcional).
    """
    print(f"[API] Received message from session '{session_id}': '{chat_request.message}'")
    
    # Obtener el chatbot para esta sesión específica
    session_chatbot = get_chatbot_for_session(session_id)
    
    # Usa la instancia del chatbot para obtener una respuesta
    bot_response = session_chatbot.get_response(chat_request.message)
    
    print(f"[API] Sending response: '{bot_response}'")
    
    return ChatResponse(response=bot_response)

# Nuevo endpoint para limpiar el historial de una sesión
@app.post("/clear-history")
async def clear_history(session_id: str = "default"):
    """Limpia el historial de conversación para una sesión específica."""
    if session_id in user_sessions:
        user_sessions[session_id].clear_history()
        return {"message": f"Historial de sesión {session_id} limpiado."}
    return {"message": "Sesión no encontrada."}


# Endpoint de prueba para verificar que la API está funcionando
@app.get("/")
async def root():
    return {"message": "¡BizChat Assistant API está en línea!"}

# Endpoint para listar las intenciones cargadas (útil para debug)
@app.get("/intents")
async def list_intents():
    intents_list = [{"tag": intent["tag"]} for intent in chatbot.get_intents()]
    return {"intents": intents_list}

# Este bloque permite ejecutar la app con 'python main.py' para desarrollo
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)