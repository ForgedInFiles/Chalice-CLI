"""
LM Studio Provider
Local model inference using LM Studio
"""
import requests
import json
from typing import Dict, Any, List, Optional, Iterator


class LMStudioProvider:
    """
    LM Studio provider for local model inference

    LM Studio provides a user-friendly desktop app for running local LLMs
    Compatible with OpenAI API format
    """

    def __init__(self, base_url: str = "http://localhost:1234/v1"):
        """
        Initialize LM Studio provider

        Args:
            base_url: LM Studio API base URL (OpenAI-compatible)
        """
        self.base_url = base_url.rstrip('/')

    def is_available(self) -> bool:
        """Check if LM Studio is running"""
        try:
            response = requests.get(f"{self.base_url}/models", timeout=2)
            return response.status_code == 200
        except:
            return False

    def list_models(self) -> List[Dict[str, Any]]:
        """
        List available models

        Returns:
            List of model information dictionaries
        """
        try:
            response = requests.get(f"{self.base_url}/models")
            response.raise_for_status()
            data = response.json()

            models = []
            for model in data.get('data', []):
                models.append({
                    'id': model['id'],
                    'object': model.get('object', 'model'),
                    'created': model.get('created', 0),
                    'owned_by': model.get('owned_by', 'lmstudio')
                })

            return models

        except Exception as e:
            print(f"Error listing models: {e}")
            return []

    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Chat completion (OpenAI-compatible)

        Args:
            model: Model ID
            messages: List of message dictionaries
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            stream: Enable streaming
            **kwargs: Additional parameters

        Returns:
            Chat result or iterator if streaming
        """
        try:
            payload = {
                'model': model,
                'messages': messages,
                'temperature': temperature,
                'stream': stream
            }

            if max_tokens:
                payload['max_tokens'] = max_tokens

            # Add additional parameters
            payload.update(kwargs)

            response = requests.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                stream=stream
            )
            response.raise_for_status()

            if stream:
                return self._stream_chat(response)
            else:
                data = response.json()
                return {
                    'id': data.get('id', ''),
                    'object': data.get('object', 'chat.completion'),
                    'created': data.get('created', 0),
                    'model': data.get('model', model),
                    'choices': data.get('choices', []),
                    'usage': data.get('usage', {})
                }

        except Exception as e:
            return {
                'error': str(e),
                'choices': [{'message': {'role': 'assistant', 'content': ''}}],
                'usage': {}
            }

    def _stream_chat(self, response) -> Iterator[Dict[str, Any]]:
        """Stream chat response"""
        for line in response.iter_lines():
            if line:
                line_text = line.decode('utf-8')
                if line_text.startswith('data: '):
                    line_text = line_text[6:]  # Remove 'data: ' prefix

                if line_text == '[DONE]':
                    break

                try:
                    data = json.loads(line_text)
                    yield data
                except json.JSONDecodeError:
                    continue

    def completion(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Text completion (OpenAI-compatible)

        Args:
            model: Model ID
            prompt: Text prompt
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            stream: Enable streaming
            **kwargs: Additional parameters

        Returns:
            Completion result or iterator if streaming
        """
        try:
            payload = {
                'model': model,
                'prompt': prompt,
                'temperature': temperature,
                'stream': stream
            }

            if max_tokens:
                payload['max_tokens'] = max_tokens

            payload.update(kwargs)

            response = requests.post(
                f"{self.base_url}/completions",
                json=payload,
                stream=stream
            )
            response.raise_for_status()

            if stream:
                return self._stream_completion(response)
            else:
                data = response.json()
                return {
                    'id': data.get('id', ''),
                    'object': data.get('object', 'text_completion'),
                    'created': data.get('created', 0),
                    'model': data.get('model', model),
                    'choices': data.get('choices', []),
                    'usage': data.get('usage', {})
                }

        except Exception as e:
            return {
                'error': str(e),
                'choices': [{'text': ''}],
                'usage': {}
            }

    def _stream_completion(self, response) -> Iterator[Dict[str, Any]]:
        """Stream completion response"""
        for line in response.iter_lines():
            if line:
                line_text = line.decode('utf-8')
                if line_text.startswith('data: '):
                    line_text = line_text[6:]

                if line_text == '[DONE]':
                    break

                try:
                    data = json.loads(line_text)
                    yield data
                except json.JSONDecodeError:
                    continue

    def embeddings(
        self,
        model: str,
        input: str
    ) -> Optional[Dict[str, Any]]:
        """
        Generate embeddings (if supported)

        Args:
            model: Model ID
            input: Text to embed

        Returns:
            Embeddings result
        """
        try:
            response = requests.post(
                f"{self.base_url}/embeddings",
                json={
                    'model': model,
                    'input': input
                }
            )
            response.raise_for_status()
            data = response.json()

            return {
                'object': data.get('object', 'list'),
                'data': data.get('data', []),
                'model': data.get('model', model),
                'usage': data.get('usage', {})
            }

        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return None


def get_lmstudio_provider(base_url: str = "http://localhost:1234/v1") -> LMStudioProvider:
    """Get LM Studio provider instance"""
    return LMStudioProvider(base_url)
