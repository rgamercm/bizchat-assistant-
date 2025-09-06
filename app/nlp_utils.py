import spacy

class NLPModel:
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NLPModel, cls).__new__(cls)
            # Cargar el modelo solo una vez
            try:
                cls._model = spacy.load("es_core_news_md")
                print("Modelo de lenguaje de spaCy cargado exitosamente (Singleton).")
            except OSError:
                print("Error: El modelo de spaCy 'es_core_news_md' no está instalado.")
                exit(1)
        return cls._instance
    
    def get_model(self):
        return self._model

# Instancia global del modelo
nlp_model = NLPModel()