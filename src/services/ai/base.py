from abc import ABC, abstractmethod


class BaseAIClient(ABC):
    """
    Base interface for AI providers.
    """

    @abstractmethod
    def summarize(self, system_prompt: str, user_prompt: str) -> dict:
        """
        Returns a structured JSON dictionary.
        """
        pass