import json
import os
from typing import List, Dict, Any

class Chatbot:
    """Clase principal que representa el chatbot y su lógica."""

    def __init__(self, knowledge_base_path: str):
        """
        Inicializa el chatbot cargando la base de conocimiento.

        Args:
            knowledge_base_path (str): Ruta al archivo JSON de la base de conocimiento.
        """
        self.knowledge_base_path = knowledge_base_path
        self.intents = []  # Aquí guardaremos la lista de intenciones cargadas
        self.load_knowledge_base()

    def load_knowledge_base(self) -> None:
        """Carga la base de conocimiento desde el archivo JSON."""
        # Usamos 'os.path' para construir la ruta de forma correcta en cualquier SO
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

    def get_intents(self) -> List[Dict[str, Any]]:
        """Devuelve la lista completa de intenciones."""
        return self.intents

# Bloque de código para pruebas simples
if __name__ == "__main__":
    # Instanciamos el chatbot apuntando a nuestra base de conocimiento
    bot = Chatbot('data/knowledge_base.json')
    
    # Probamos que se hayan cargado las intenciones
    intents = bot.get_intents()
    print("Tags de intenciones cargadas:")
    for intent in intents:
        print(f" - {intent['tag']}")