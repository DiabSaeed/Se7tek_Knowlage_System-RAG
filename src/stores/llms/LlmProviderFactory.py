from .Enums import LlmEnums
from .Providers import OpenaiProvider, BGEM3Provider
from helpers.config import Settings
class LlmFactory:
    def __init__ (self, config):
        self.config = Settings() #type: ignore
    def create_provider(self, provider):
        if provider.lower() == LlmEnums.LlmEnums.OPENAI.value.lower():
            return OpenaiProvider(
                open_ai_key=self.config.OPENAI_KEY,
                base_url= self.config.OPENAI_URL,
                default_generation_max_tokens= self.config.GENERATION_DEFAULT_MAX_TOKENS,
                default_generation_temperature= self.config.GENERATION_DEFAULT_TEMPERATURE)
        elif provider.lower() == LlmEnums.LlmEnums.BGEM3.value.lower():
            return BGEM3Provider()