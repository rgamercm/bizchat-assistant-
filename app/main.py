from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.chatbot import Chatbot  # Importamos nuestra clase Chatbot

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

# Define el endpoint principal de la API
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest):
    """
    Endpoint para enviar un mensaje al chatbot y recibir su respuesta.

    - **message**: El mensaje/texto del usuario.
    """
    print(f"[API] Received message: '{chat_request.message}'")
    
    # Usa la instancia del chatbot para obtener una respuesta
    bot_response = chatbot.get_response(chat_request.message)
    
    print(f"[API] Sending response: '{bot_response}'")
    
    # Devuelve la respuesta empaquetada en el modelo de respuesta
    return ChatResponse(response=bot_response)

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