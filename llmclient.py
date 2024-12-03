from typing import Optional, Dict, Any
import openai
from enum import Enum
import re
from loguru import logger
import sys
from datetime import datetime
import requests
from typing import Optional, Dict, Any
import json

# Настройка логирования
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)
logger.add(
    "logs/llm_{time}.log",
    rotation="500 MB",
    retention="10 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)


class ModelProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    UNKNOWN = "unknown"


class LLMModel:
    def __init__(self, model_name: str, api_key: Optional[str] = None):
        """
        Инициализация модели LLM

        Args:
            model_name (str): Название модели
            api_key (Optional[str]): API ключ для доступа к модели
        """
        logger.info(f"Initializing LLM model: {model_name}")
        self.model_name = model_name
        self.api_key = api_key
        self.provider = self._parse_provider()
        self.client = self._initialize_client()
        self.request_history = []

    def _parse_provider(self) -> ModelProvider:
        """Определяет провайдера модели на основе имени"""
        model_name_lower = self.model_name.lower()

        logger.debug(f"Parsing provider for model: {self.model_name}")

        if any(name in model_name_lower for name in ["gpt", "text-davinci", "openai"]):
            logger.info("Detected OpenAI provider")
            return ModelProvider.OPENAI
        elif any(name in model_name_lower for name in ["claude", "anthropic"]):
            logger.info("Detected Anthropic provider")
            return ModelProvider.ANTHROPIC
        elif "ollama" in model_name_lower or self._is_ollama_model():
            logger.info("Detected Ollama provider")
            self.model_name = self.model_name.replace("ollama/","")
            logger.debug(self.model_name)
            return ModelProvider.OLLAMA

        logger.warning(f"Unknown provider for model: {self.model_name}")
        return ModelProvider.UNKNOWN

    def _is_ollama_model(self) -> bool:
        """Проверяет, является ли модель Ollama моделью"""
        ollama_models = ["llama", "mistral", "vicuna", "codellama"]
        return any(model in self.model_name.lower() for model in ollama_models)

    def _initialize_client(self) -> Any:
        """Инициализирует клиент в зависимости от провайдера"""
        logger.debug(f"Initializing client for provider: {self.provider}")

        try:
            if self.provider == ModelProvider.OPENAI:
                if not self.api_key:
                    logger.error("API key is required for OpenAI")
                    raise ValueError("API key is required for OpenAI")
                return openai.OpenAI(api_key=self.api_key)
            elif self.provider == ModelProvider.ANTHROPIC:
                # Реализация для Anthropic
                pass
            elif self.provider == ModelProvider.OLLAMA:
                # Реализация для Ollama
                return "http://localhost:11434"  # Стандартный URL для Ollama
            else:
                logger.error(f"Unsupported model provider: {self.provider}")
                raise ValueError(f"Unsupported model provider: {self.provider}")
        except Exception as e:
            logger.error(f"Error initializing client: {str(e)}")
            raise

    def generate(self,
                 prompt: str,
                 max_tokens: int = 1000,
                 temperature: float = 0.7,
                 **kwargs) -> str:
        """
        Генерирует ответ на основе промпта

        Args:
            prompt (str): Входной текст
            max_tokens (int): Максимальное количество токенов в ответе
            temperature (float): Температура генерации
            **kwargs: Дополнительные параметры

        Returns:
            str: Сгенерированный текст
        """
        start_time = datetime.now()
        logger.info(f"Generating response for prompt: {prompt[:100]}...")

        try:
            if self.provider == ModelProvider.OPENAI:
                response = self._generate_openai(prompt, max_tokens, temperature, **kwargs)
            elif self.provider == ModelProvider.ANTHROPIC:
                response = self._generate_anthropic(prompt, max_tokens, temperature, **kwargs)
            elif self.provider == ModelProvider.OLLAMA:
                response = self._generate_ollama(prompt, max_tokens, temperature, **kwargs)
            else:
                logger.error(f"Unsupported provider: {self.provider}")
                raise ValueError(f"Unsupported provider: {self.provider}")

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Сохраняем информацию о запросе
            request_info = {
                "timestamp": start_time,
                "duration": duration,
                "prompt": prompt,
                "response": response,
                "parameters": {
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    **kwargs
                }
            }
            self.request_history.append(request_info)

            logger.info(f"Generated response in {duration:.2f} seconds")
            logger.debug(f"Response: {response[:100]}...")

            return response

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}", exc_info=True)
            raise

    def _generate_openai(self,
                         prompt: str,
                         max_tokens: int,
                         temperature: float,
                         **kwargs) -> str:
        """Генерация текста с помощью OpenAI API"""
        logger.debug("Sending request to OpenAI API")

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise

    def _generate_anthropic(self,
                            prompt: str,
                            max_tokens: int,
                            temperature: float,
                            **kwargs) -> str:
        """Генерация текста с помощью Anthropic API"""
        logger.debug("Sending request to Anthropic API")
        # Реализация для Anthropic
        pass


    @property
    def model_info(self) -> Dict[str, Any]:
        """Возвращает информацию о модели"""
        info = {
            "model_name": self.model_name,
            "provider": self.provider.value,
            "api_key_set": bool(self.api_key),
            "total_requests": len(self.request_history),
            "average_response_time": self._calculate_average_response_time(),
            "last_request_timestamp": self._get_last_request_timestamp()
        }
        logger.debug(f"Model info: {info}")
        return info

    def _calculate_average_response_time(self) -> float:
        """Вычисляет среднее время ответа"""
        if not self.request_history:
            return 0.0
        total_duration = sum(req["duration"] for req in self.request_history)
        return total_duration / len(self.request_history)

    def _get_last_request_timestamp(self) -> Optional[datetime]:
        """Возвращает временную метку последнего запроса"""
        if not self.request_history:
            return None
        return self.request_history[-1]["timestamp"]

    def get_request_history(self, limit: Optional[int] = None) -> list:
        """
        Возвращает историю запросов

        Args:
            limit (Optional[int]): Ограничение количества возвращаемых записей

        Returns:
            list: История запросов
        """
        history = self.request_history
        if limit:
            history = history[-limit:]
        return history

    def clear_history(self):
        """Очищает историю запросов"""
        logger.info("Clearing request history")
        self.request_history = []

    def save_history_to_file(self, filename: str):
        """
        Сохраняет историю запросов в файл

        Args:
            filename (str): Путь к файлу
        """
        import json
        from datetime import datetime

        logger.info(f"Saving request history to file: {filename}")

        try:
            # Конвертируем datetime объекты в строки
            history = []
            for request in self.request_history:
                request_copy = request.copy()
                request_copy["timestamp"] = request_copy["timestamp"].isoformat()
                history.append(request_copy)

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)

            logger.success(f"Successfully saved history to {filename}")
        except Exception as e:
            logger.error(f"Error saving history to file: {str(e)}")
            raise

    def load_history_from_file(self, filename: str):
        """
        Загружает историю запросов из файла

        Args:
            filename (str): Путь к файлу
        """
        import json
        from datetime import datetime

        logger.info(f"Loading request history from file: {filename}")

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                history = json.load(f)

            # Конвертируем строки обратно в datetime
            for request in history:
                request["timestamp"] = datetime.fromisoformat(request["timestamp"])

            self.request_history = history
            logger.success(f"Successfully loaded history from {filename}")
        except Exception as e:
            logger.error(f"Error loading history from file: {str(e)}")
            raise

    def get_statistics(self) -> Dict[str, Any]:
        """
        Возвращает статистику использования модели

        Returns:
            Dict[str, Any]: Статистика использования
        """
        if not self.request_history:
            return {
                "total_requests": 0,
                "average_response_time": 0,
                "total_tokens_generated": 0
            }

        total_requests = len(self.request_history)
        avg_response_time = self._calculate_average_response_time()

        logger.info(f"Calculating statistics for {total_requests} requests")

        return {
            "total_requests": total_requests,
            "average_response_time": avg_response_time,
            "first_request_time": self.request_history[0]["timestamp"],
            "last_request_time": self.request_history[-1]["timestamp"],
            "most_common_temperature": self._get_most_common_temperature(),
            "average_prompt_length": self._calculate_average_prompt_length()
        }

    def _get_most_common_temperature(self) -> float:
        """Возвращает наиболее часто используемое значение temperature"""
        if not self.request_history:
            return 0.0

        temperatures = [req["parameters"]["temperature"] for req in self.request_history]
        from collections import Counter
        return Counter(temperatures).most_common(1)[0][0]

    def _calculate_average_prompt_length(self) -> float:
        """Вычисляет среднюю длину промпта"""
        if not self.request_history:
            return 0.0

        total_length = sum(len(req["prompt"]) for req in self.request_history)
        return total_length / len(self.request_history)

    def _generate_ollama(self,
                         prompt: str,
                         max_tokens: int,
                         temperature: float,
                         **kwargs) -> str:
        """
        Генерация текста с помощью Ollama API

        Args:
            prompt (str): Входной текст
            max_tokens (int): Максимальное количество токенов
            temperature (float): Температура генерации
            **kwargs: Дополнительные параметры

        Returns:
            str: Сгенерированный текст
        """
        logger.debug(f"Sending request to Ollama API with model: {self.model_name}")

        # Формируем URL для запроса
        url = f"{self.client}/api/generate"

        # Подготавливаем параметры запроса
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False  # Отключаем потоковую передачу
        }

        # Добавляем дополнительные параметры из kwargs
        supported_params = [
            "top_k", "top_p", "repeat_penalty", "presence_penalty",
            "frequency_penalty", "stop", "system"
        ]
        for param in supported_params:
            if param in kwargs:
                payload[param] = kwargs[param]

        try:
            logger.debug(f"Ollama request payload: {payload}")
            response = requests.post(url, json=payload)

            if response.status_code != 200:
                error_msg = f"Ollama API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)

            response_json = response.json()
            generated_text = response_json.get('response', '')

            # Логируем дополнительную информацию о генерации
            if 'eval_count' in response_json:
                logger.debug(f"Tokens generated: {response_json['eval_count']}")
            if 'eval_duration' in response_json:
                logger.debug(f"Generation time: {response_json['eval_duration']}ns")

            return generated_text

        except requests.exceptions.ConnectionError:
            error_msg = "Failed to connect to Ollama server. Make sure it's running on localhost:11434"
            logger.error(error_msg)
            raise ConnectionError(error_msg)
        except Exception as e:
            logger.error(f"Error in Ollama generation: {str(e)}")
            raise

    def get_available_ollama_models(self) -> list:
        """
        Получает список доступных моделей Ollama

        Returns:
            list: Список доступных моделей
        """
        if self.provider != ModelProvider.OLLAMA:
            logger.warning("This method is only available for Ollama provider")
            return []

        try:
            url = f"{self.client}/api/tags"
            response = requests.get(url)

            if response.status_code != 200:
                logger.error(f"Failed to get Ollama models: {response.status_code}")
                return []

            models = response.json().get('models', [])
            logger.info(f"Available Ollama models: {models}")
            return models

        except Exception as e:
            logger.error(f"Error getting Ollama models: {str(e)}")
            return []

    def pull_ollama_model(self, model_name: str) -> bool:
        """
        Загружает модель Ollama

        Args:
            model_name (str): Название модели для загрузки

        Returns:
            bool: True если успешно, False в противном случае
        """
        if self.provider != ModelProvider.OLLAMA:
            logger.warning("This method is only available for Ollama provider")
            return False

        try:
            url = f"{self.client}/api/pull"
            payload = {"name": model_name}

            logger.info(f"Pulling Ollama model: {model_name}")
            response = requests.post(url, json=payload)

            if response.status_code != 200:
                logger.error(f"Failed to pull model: {response.status_code}")
                return False

            logger.success(f"Successfully pulled model: {model_name}")
            return True

        except Exception as e:
            logger.error(f"Error pulling Ollama model: {str(e)}")
            return False

