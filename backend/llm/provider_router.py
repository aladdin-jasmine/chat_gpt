class ProviderRouter:
    def __init__(self):
        self.providers = {
            'openai': 'OpenAI',
            'claude': 'Claude',
            'gemini': 'Gemini',
            'ollama': 'Ollama',
            'groq': 'Groq',
            'huggingface': 'HuggingFace'
        }

    def route(self, provider_name):
        return self.providers.get(provider_name, 'fallback')
