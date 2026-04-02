import json
import logging
from abc import ABC, abstractmethod
from src.core.llm_config import LLMConfigManager

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    def __init__(self, raw_send=False, raw_return=False):
        self.raw_send = raw_send
        self.raw_return = raw_return

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Takes standard standard prompt and returns standard string response."""
        pass

    def _log_raw_send(self, payload):
        if self.raw_send:
        if self.raw_send:
            logger.info(f"[RAW SEND]: {json.dumps(payload, indent=2, default=str)}")

    def _log_raw_return(self, response):
        if self.raw_return:
            # Attempt to stringify if not string
            if not isinstance(response, str):
                response = json.dumps(response, indent=2, default=str)
            logger.info(f"[RAW RETURN]: {response}")
            print(f"[RAW RETURN]: {response}")

class OpenAIProvider(LLMProvider):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("OpenAI SDK not installed. Run initialization or 'pip install openai'.")

        config_mgr = LLMConfigManager()
        api_key = config_mgr.get_api_key('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY missing from environment.")

        self.client = OpenAI(api_key=api_key)

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        payload = {"model": "gpt-4o", "messages": messages}
        self._log_raw_send(payload)

        response = self.client.chat.completions.create(**payload)

        # We try to get the raw model_dump if raw_return is on
        if self.raw_return and hasattr(response, 'model_dump'):
            self._log_raw_return(response.model_dump())
        else:
             self._log_raw_return(str(response))

        return response.choices[0].message.content


class GeminiProvider(LLMProvider):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            from google import genai
        except ImportError:
            raise ImportError("Gemini SDK not installed. Run initialization or 'pip install google-genai'.")

        config_mgr = LLMConfigManager()
        api_key = config_mgr.get_api_key('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY missing from environment.")

        self.client = genai.Client(api_key=api_key)

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        from google.genai import types
        # Gemini often uses a single text stream, but we can configure system instructions.
        payload = {
            "model": "gemini-2.5-pro",
            "contents": user_prompt,
            "config": types.GenerateContentConfig(
                system_instruction=system_prompt,
            )
        }

        self._log_raw_send({"model": payload["model"], "contents": payload["contents"], "system": system_prompt})

        response = self.client.models.generate_content(**payload)

        self._log_raw_return(str(response))
        return response.text


class JulesProvider(LLMProvider):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Assuming Jules provides an OpenAI-compatible endpoint or custom SDK.
        # Fallback to OpenAI SDK with custom URL for now as placeholder unless Jules SDK exists.
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("SDK for Jules (openai) not installed. Run initialization.")

        config_mgr = LLMConfigManager()
        api_key = config_mgr.get_api_key('JULES_API_KEY')
        if not api_key:
            raise ValueError("JULES_API_KEY missing from environment.")

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.jules.ai/v1" # Example fallback endpoint
        )

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        payload = {"model": "jules-agent-1", "messages": messages}
        self._log_raw_send(payload)

        response = self.client.chat.completions.create(**payload)
        self._log_raw_return(str(response))
        return response.choices[0].message.content


class OllamaProvider(LLMProvider):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            import ollama
        except ImportError:
            raise ImportError("Ollama SDK not installed. Run initialization or 'pip install ollama'.")

        self.client = ollama
        config_mgr = LLMConfigManager()
        self.model = config_mgr.get_api_key('OLLAMA_MODEL') or 'llama3'

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        payload = {"model": self.model, "messages": messages}
        self._log_raw_send(payload)

        response = self.client.chat(model=self.model, messages=messages)
        self._log_raw_return(response)

        return response['message']['content']


class LlamaCppProvider(LLMProvider):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            from llama_cpp import Llama
        except ImportError:
            raise ImportError("llama-cpp-python not installed. Run initialization or 'pip install llama-cpp-python'.")

        config_mgr = LLMConfigManager()
        self.model_path = config_mgr.get_api_key('LLAMACPP_MODEL_PATH')
        if not self.model_path:
             raise ValueError("LLAMACPP_MODEL_PATH missing from environment.")

        self.llm = Llama(
            model_path=self.model_path,
            n_ctx=2048,
            verbose=False
        )

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        # Simple formatting for Llama models
        prompt = f"System: {system_prompt}\n\nUser: {user_prompt}\n\nAssistant:"

        payload = {"prompt": prompt, "max_tokens": 1024}
        self._log_raw_send(payload)

        response = self.llm(prompt, max_tokens=1024)
        self._log_raw_return(response)

        return response['choices'][0]['text']

def get_llm_provider(provider_name=None, raw_send=False, raw_return=False):
    if not provider_name:
        config_mgr = LLMConfigManager()
        provider_name = config_mgr.get_active_provider()

    if not provider_name:
        raise ValueError("No LLM provider selected. Please run initialization or pass --llm.")

    provider_name = provider_name.lower()
    kwargs = {"raw_send": raw_send, "raw_return": raw_return}

    if provider_name == 'openai':
        return OpenAIProvider(**kwargs)
    elif provider_name == 'gemini':
        return GeminiProvider(**kwargs)
    elif provider_name == 'jules':
        return JulesProvider(**kwargs)
    elif provider_name == 'ollama':
        return OllamaProvider(**kwargs)
    elif provider_name == 'llamacpp':
        return LlamaCppProvider(**kwargs)
    else:
        raise ValueError(f"Unknown LLM provider: {provider_name}")
