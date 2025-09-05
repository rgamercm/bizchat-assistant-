import json
import os
import random
from typing import List, Dict, Any

# Importamos spaCy y cargamos el modelo de lenguaje
import spacy

class Chatbot:
    """Clase principal que representa el chatbot y su lógica."""

    def __init__(self, knowledge_base_path: str):
        """
        Inicializa el chatbot cargando la base de conocimiento y el modelo de NLP.

        Args:
            knowledge_base_path (str): Ruta al archivo JSON de la base de conocimiento.
        """
        self.knowledge_base_path = knowledge_base_path
        self.intents = []
        # Cargar el modelo de spaCy (asegúrate de haberlo descargado: 'python -m spacy download es_core_news_md')
        try:
            self.nlp = spacy.load("es_core_news_md") # Usa 'en_core_web_md' para inglés
            print("Modelo de lenguaje de spaCy cargado exitosamente.")
        except OSError:
            print("Error: El modelo de spaCy 'es_core_news_md' no está instalado.")
            print("Por favor, ejecuta en tu terminal: 'python -m spacy download es_core_news_md'")
            exit(1)

        self.load_knowledge_base()
        # Preprocesamos TODOS los patterns de la base de conocimiento una sola vez al iniciar
        self.preprocess_intents()

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

    def preprocess_input(self, user_input: str):
        """
        Preprocesa la entrada del usuario usando el mismo pipeline de spaCy.

        Args:
            user_input (str): La pregunta o texto escrito por el usuario.

        Returns:
            Doc: Un objeto Doc de spaCy que representa el texto procesado.
        """
        return self.nlp(user_input.lower().strip())

    def find_most_similar_intent(self, processed_input) -> Dict[str, Any]:
        """
        Encuentra la intención cuya lista de patrones es más similar a la entrada del usuario.

        Args:
            processed_input (Doc): La entrada del usuario, procesada por spaCy.

        Returns:
            Dict[str, Any]: La intención más similar encontrada.
        """
        best_similarity = 0.0
        best_intent = None

        # Itera sobre cada intención en la base de conocimiento
        for intent in self.intents:
            # Itera sobre cada pattern preprocesado de esta intención
            for pattern_doc in intent['patterns_processed']:
                # spaCy puede calcular la similitud entre dos objetos Doc
                # similarity() devuelve un valor entre 0 (nada similar) y 1 (idéntico)
                current_similarity = processed_input.similarity(pattern_doc)
                # print(f"Comparando '{processed_input.text}' con '{pattern_doc.text}': {current_similarity}") # <-- Descomenta para debug

                # Si encontramos una similitud mayor, la guardamos
                if current_similarity > best_similarity:
                    best_similarity = current_similarity
                    best_intent = intent

        # Define un umbral de similitud. Ajusta este valor según tus pruebas (0.5-0.7 es un buen inicio).
        similarity_threshold = 0.6
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