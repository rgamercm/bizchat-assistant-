import json
import os
import random
from typing import List, Dict, Any, Deque
from collections import deque

# Importamos spaCy y cargamos el modelo de lenguaje
import spacy
# Importamos nuestro singleton del modelo NLP
from app.nlp_utils import nlp_model

class Chatbot:
    """Clase principal que representa el chatbot y su lógica."""

    def __init__(self, knowledge_base_path: str, max_history: int = 5):
        """
        Inicializa el chatbot cargando la base de conocimiento.
        """
        self.knowledge_base_path = knowledge_base_path
        self.intents = []
        self.max_history = max_history
        self.conversation_history: Deque[Dict[str, str]] = deque(maxlen=max_history)
        
        # Usamos el modelo singleton en lugar de cargarlo nosotros mismos
        self.nlp = nlp_model.get_model()
        
        self.load_knowledge_base()
        self.preprocess_intents()
        print(f"Chatbot inicializado para sesión. Base de conocimiento: {len(self.intents)} intenciones.")

    def load_knowledge_base(self) -> None:
        """Carga la base de conocimiento desde el archivo JSON."""
        full_path = os.path.join(os.path.dirname(__file__), self.knowledge_base_path)
        try:
            with open(full_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.intents = data.get('intents', [])
                print(f"Base de conocimiento cargada exitosamente. {len(self.intents)} intenciones encontradas.")
        except FileNotFoundError:
            print(f"Error: No se pudo encontrar el archivo en {full_path}.")
            self.intents = []
        except json.JSONDecodeError:
            print("Error: El archivo JSON está mal formado.")
            self.intents = []

    def preprocess_intents(self) -> None:
        """
        Preprocesa todos los 'patterns' de las intenciones.
        Convierte cada pattern en un vector de spaCy (Doc) y lo guarda en una nueva clave 'patterns_processed'.
        Esto optimiza el proceso, ya que solo se hace una vez al inicio.
        """
        for intent in self.intents:
            intent['patterns_processed'] = [self.nlp(pattern) for pattern in intent['patterns']]

    def add_to_history(self, user_message: str, bot_response: str) -> None:
        """
        Añade una interacción (user + bot) al historial de conversación.
        """
        self.conversation_history.append({
            "user": user_message,
            "bot": bot_response
        })

    def get_contextual_input(self, user_input: str) -> str:
        """
        Construye la entrada contextual incluyendo el historial reciente.
        Esto ayuda al chatbot a entender el contexto de la pregunta.
        """
        if not self.conversation_history:
            return user_input  # No hay historial, devolver solo la entrada actual

        # Construir un string con las últimas interacciones
        context_lines = []
        for interaction in self.conversation_history:
            context_lines.append(f"Usuario: {interaction['user']}")
            context_lines.append(f"Asistente: {interaction['bot']}")
        
        # Unimos el historial y añadimos la nueva pregunta
        context = "\n".join(context_lines)
        contextual_input = f"{context}\nUsuario: {user_input}"
        
        return contextual_input

    def get_response(self, user_input: str) -> str:
        """
        Función principal para obtener una respuesta del chatbot.
        Ahora con contexto de conversación.
        """
        if not user_input:
            return "Por favor, escribe algo."

        # 1. Preprocesar la entrada del usuario
        processed_input = self.preprocess_input(user_input)
        print(f"Entrada procesada: '{processed_input.text}'")

        # 2. Obtener entrada contextual (incluye historial)
        contextual_input = self.get_contextual_input(user_input)
        processed_contextual = self.preprocess_input(contextual_input)
        print(f"Entrada contextual: '{processed_contextual.text}'")

        # 3. Encontrar la intención más similar (usando el contexto)
        matched_intent = self.find_most_similar_intent(processed_contextual)

        # 4. Seleccionar una respuesta aleatoria
        if matched_intent and 'responses' in matched_intent:
            response = random.choice(matched_intent['responses'])
            # 5. Añadir esta interacción al historial
            self.add_to_history(user_input, response)
            return response
        else:
            fallback_msg = "Lo siento, no estoy seguro de cómo responder a eso."
            self.add_to_history(user_input, fallback_msg)
            return fallback_msg

    def clear_history(self) -> None:
        """Limpia el historial de conversación."""
        self.conversation_history.clear()
        print("Historial de conversación limpiado.")

    def preprocess_input(self, user_input: str):
        """
        Preprocesa la entrada del usuario de manera más robusta.
        """
        # 1. Convertir a minúsculas
        # 2. Eliminar tildes y caracteres especiales
        # 3. Eliminar signos de puntuación extraños
        processed_text = user_input.lower().strip()
        
        # Eliminar tildes (á → a, é → e, etc.)
        import unicodedata
        processed_text = ''.join(
            c for c in unicodedata.normalize('NFD', processed_text)
            if unicodedata.category(c) != 'Mn'
        )
        
        # Eliminar signos de puntuación (opcional, pero ayuda)
        processed_text = ''.join(c for c in processed_text if c.isalnum() or c.isspace())
        
        return self.nlp(processed_text)

    def find_most_similar_intent(self, processed_input) -> Dict[str, Any]:
        """
        Encuentra la intención cuya lista de patrones es más similar a la entrada del usuario.
        Ahora con logs de debug detallados.
        """
        best_similarity = 0.0
        best_intent = None
        best_pattern = ""

        # Itera sobre cada intención en la base de conocimiento
        for intent in self.intents:
            # Itera sobre cada pattern preprocesado de esta intención
            for pattern_doc in intent['patterns_processed']:
                # spaCy puede calcular la similitud entre dos objetos Doc
                current_similarity = processed_input.similarity(pattern_doc)
                
                # Debug: mostrar todas las comparaciones
                print(f"  Comparando '{processed_input.text}' con '{pattern_doc.text}': {current_similarity}")
                
                # Si encontramos una similitud mayor, la guardamos
                if current_similarity > best_similarity:
                    best_similarity = current_similarity
                    best_intent = intent
                    best_pattern = pattern_doc.text

        # Muestra el mejor match encontrado
        print(f"MEJOR MATCH: '{processed_input.text}' vs '{best_pattern}': {best_similarity}")

        # Define un umbral de similitud. Ajusta este valor según tus pruebas.
        # Umbral más bajo para desarrollo (0.4) - puedes ajustarlo según pruebas
        similarity_threshold = 0.4
        print(f"Similitud más alta encontrada: {best_similarity} (Umbral: {similarity_threshold})")

        # Si la similitud no supera el umbral, devolvemos la intención de fallback
        if best_similarity < similarity_threshold:
            print("La similitud es baja. Usando intención de fallback.")
            for intent in self.intents:
                if intent['tag'] == 'fallback':
                    return intent
        
        # Si la supera, devolvemos la mejor intención encontrada
        return best_intent

    def get_response(self, user_input: str) -> str:
        """
        Función principal para obtener una respuesta del chatbot.
        Orquesta todo el proceso: preprocesar, buscar intención, devolver respuesta.

        Args:
            user_input (str): La pregunta escrita por el usuario.

        Returns:
            str: La respuesta generada por el chatbot.
        """
        if not user_input:
            return "Por favor, escribe algo."

        # 1. Preprocesar la entrada del usuario
        processed_input = self.preprocess_input(user_input)
        print(f"Entrada procesada: '{processed_input.text}'")

        # 2. Encontrar la intención más similar
        matched_intent = self.find_most_similar_intent(processed_input)

        # 3. Seleccionar una respuesta aleatoria del grupo de respuestas de esa intención
        if matched_intent and 'responses' in matched_intent:
            response = random.choice(matched_intent['responses'])
            return response
        else:
            # Esto no debería pasar si la intent 'fallback' está bien configurada, pero es un buen safeguard.
            return "Lo siento, no estoy seguro de cómo responder a eso."

# Bloque de código para pruebas
if __name__ == "__main__":
    # Instanciamos el chatbot
    bot = Chatbot('data/knowledge_base.json')

    # Bucle simple de prueba en la terminal
    print("\n--- Modo Prueba del Chatbot ---")
    print('Escribe "salir" para terminar la prueba.')
    while True:
        user_message = input("Tú: ")
        if user_message.lower() == 'salir':
            break

        bot_response = bot.get_response(user_message)
        print(f"Bot: {bot_response}")