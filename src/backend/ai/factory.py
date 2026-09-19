import json
from .providers.deepseek import DeepSeekProvider
from .providers.openai_provider import OpenAIProvider
from .providers.claude import ClaudeProvider
from .providers.gemini import GeminiProvider
from .providers.ollama import OllamaProvider

class AIProviderFactory:
    @staticmethod
    def create_provider(provider_name: str, api_key: str = "", model: str = None):
        name = provider_name.lower()
        if name == "deepseek":
            return DeepSeekProvider(api_key=api_key, model=model or "deepseek-chat")
        elif name == "openai":
            return OpenAIProvider(api_key=api_key, model=model or "gpt-3.5-turbo")
        elif name == "claude":
            return ClaudeProvider(api_key=api_key, model=model or "claude-3-sonnet-20240229")
        elif name == "gemini":
            return GeminiProvider(api_key=api_key, model=model or "gemini-pro")
        elif name == "ollama":
            return OllamaProvider(model=model or "llama2")
        else:
            raise ValueError(f"Unknown AI provider: {provider_name}")
