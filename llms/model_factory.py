"""
Abstract base class implementation of an LLM. Contains several LLM providers and ways to get LLM outputs for input prompts
"""

from enums import ModelType
from llms.gpt import OpenAILLM
from llms.gemini import Gemini
from llms.claude import Anthropic
from llms.litellm import LiteLLM

import os

class ModelFactory:

    def __init__(self):
        self.MIN_LENGTH = 3
        self.MAX_LENGTH = 32768
        self.TEMP = 0.7

    def get_model(self, model_type: ModelType, model_name: str, cache_dir: str = './cache', temp: float = 0.7):
        
        if model_type == ModelType.open_ai:
            return OpenAILLM(openai_model_name=model_name, temp=temp, max_length=self.MAX_LENGTH, openai_token=os.getenv("OPEN_AI_TOKEN"))

        if model_type == ModelType.gemini:
            return Gemini(gemini_model_name=model_name, temp=temp, max_length=self.MAX_LENGTH, gemini_token=os.environ.get("GEMINI_TOKEN"))

        if model_type == ModelType.anthropic:
            return Anthropic(model_name=model_name, temp=temp, max_length=self.MAX_LENGTH, anthropic_token=os.environ.get("ANTHROPIC_TOKEN"))

        if model_type == ModelType.litellm:
            return LiteLLM(model_name=model_name, temp=1.0, max_length=self.MAX_LENGTH)

        else:
            raise ValueError(f"Unsupported Model type: {model_type}")