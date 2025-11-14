"""
Ollama Provider
Local model inference using Ollama
"""
import requests
import json
from typing import Dict, Any, List, Optional, Iterator
from pathlib import Path


class OllamaProvider:
    """
    Ollama provider for local model inference

    Ollama provides easy local LLM hosting with models like:
    - Llama 2, Llama 3
    - Mistral, Mixtral
    - CodeLlama
    - And many more
    """

    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama provider

        Args:
            base_url: Ollama API base URL
        """
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api"

    def is_available(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=2)
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
            response = requests.get(f"{self.api_url}/tags")
            response.raise_for_status()
            data = response.json()

            models = []
            for model in data.get('models', []):
                models.append({
                    'name': model['name'],
                    'size': model.get('size', 0),
                    'modified': model.get('modified_at', ''),
                    'digest': model.get('digest', ''),
                    'details': model.get('details', {})
                })

            return models

        except Exception as e:
            print(f"Error listing models: {e}")
            return []

    def pull_model(self, model_name: str) -> bool:
        """
        Pull/download a model

        Args:
            model_name: Model name (e.g., 'llama2', 'mistral')

        Returns:
            bool: True if successful
        """
        try:
            print(f"Pulling model: {model_name}...")

            response = requests.post(
                f"{self.api_url}/pull",
                json={'name': model_name},
                stream=True
            )
            response.raise_for_status()

            # Stream progress
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    status = data.get('status', '')
                    if 'total' in data and 'completed' in data:
                        total = data['total']
                        completed = data['completed']
                        pct = (completed / total * 100) if total > 0 else 0
                        print(f"\r{status}: {pct:.1f}%", end='')
                    else:
                        print(f"\r{status}", end='')

            print("\n✓ Model pulled successfully")
            return True

        except Exception as e:
            print(f"\n✗ Error pulling model: {e}")
            return False

    def delete_model(self, model_name: str) -> bool:
        """
        Delete a model

        Args:
            model_name: Model name

        Returns:
            bool: True if successful
        """
        try:
            response = requests.delete(
                f"{self.api_url}/delete",
                json={'name': model_name}
            )
            response.raise_for_status()
            print(f"✓ Deleted model: {model_name}")
            return True

        except Exception as e:
            print(f"✗ Error deleting model: {e}")
            return False

    def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate completion

        Args:
            model: Model name
            prompt: User prompt
            system: System prompt (optional)
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            stream: Enable streaming
            **kwargs: Additional parameters

        Returns:
            Generation result or iterator if streaming
        """
        try:
            payload = {
                'model': model,
                'prompt': prompt,
                'stream': stream,
                'options': {
                    'temperature': temperature
                }
            }

            if system:
                payload['system'] = system

            if max_tokens:
                payload['options']['num_predict'] = max_tokens

            # Merge additional options
            payload['options'].update(kwargs)

            response = requests.post(
                f"{self.api_url}/generate",
                json=payload,
                stream=stream
            )
            response.raise_for_status()

            if stream:
                return self._stream_generate(response)
            else:
                data = response.json()
                return {
                    'response': data.get('response', ''),
                    'model': model,
                    'done': data.get('done', False),
                    'context': data.get('context', []),
                    'total_duration': data.get('total_duration', 0),
                    'load_duration': data.get('load_duration', 0),
                    'prompt_eval_count': data.get('prompt_eval_count', 0),
                    'eval_count': data.get('eval_count', 0)
                }

        except Exception as e:
            return {
                'error': str(e),
                'response': '',
                'done': True
            }

    def _stream_generate(self, response) -> Iterator[Dict[str, Any]]:
        """Stream generation response"""
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                yield {
                    'response': data.get('response', ''),
                    'done': data.get('done', False)
                }

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
        Chat completion

        Args:
            model: Model name
            messages: List of message dictionaries with 'role' and 'content'
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
                'stream': stream,
                'options': {
                    'temperature': temperature
                }
            }

            if max_tokens:
                payload['options']['num_predict'] = max_tokens

            payload['options'].update(kwargs)

            response = requests.post(
                f"{self.api_url}/chat",
                json=payload,
                stream=stream
            )
            response.raise_for_status()

            if stream:
                return self._stream_chat(response)
            else:
                data = response.json()
                return {
                    'message': data.get('message', {}),
                    'model': model,
                    'done': data.get('done', False),
                    'total_duration': data.get('total_duration', 0),
                    'load_duration': data.get('load_duration', 0),
                    'prompt_eval_count': data.get('prompt_eval_count', 0),
                    'eval_count': data.get('eval_count', 0)
                }

        except Exception as e:
            return {
                'error': str(e),
                'message': {'role': 'assistant', 'content': ''},
                'done': True
            }

    def _stream_chat(self, response) -> Iterator[Dict[str, Any]]:
        """Stream chat response"""
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                yield {
                    'message': data.get('message', {}),
                    'done': data.get('done', False)
                }

    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get model information

        Args:
            model_name: Model name

        Returns:
            Model information dictionary
        """
        try:
            response = requests.post(
                f"{self.api_url}/show",
                json={'name': model_name}
            )
            response.raise_for_status()
            data = response.json()

            return {
                'modelfile': data.get('modelfile', ''),
                'parameters': data.get('parameters', ''),
                'template': data.get('template', ''),
                'details': data.get('details', {}),
                'model_info': data.get('model_info', {})
            }

        except Exception as e:
            print(f"Error getting model info: {e}")
            return None

    def create_model(
        self,
        name: str,
        modelfile: str,
        stream: bool = True
    ) -> bool:
        """
        Create a custom model from a Modelfile

        Args:
            name: Model name
            modelfile: Modelfile content
            stream: Stream creation progress

        Returns:
            bool: True if successful
        """
        try:
            print(f"Creating model: {name}...")

            response = requests.post(
                f"{self.api_url}/create",
                json={
                    'name': name,
                    'modelfile': modelfile,
                    'stream': stream
                },
                stream=stream
            )
            response.raise_for_status()

            if stream:
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        status = data.get('status', '')
                        print(f"\r{status}", end='')

            print("\n✓ Model created successfully")
            return True

        except Exception as e:
            print(f"\n✗ Error creating model: {e}")
            return False

    def embeddings(
        self,
        model: str,
        prompt: str
    ) -> Optional[List[float]]:
        """
        Generate embeddings

        Args:
            model: Model name
            prompt: Text to embed

        Returns:
            List of embedding values
        """
        try:
            response = requests.post(
                f"{self.api_url}/embeddings",
                json={
                    'model': model,
                    'prompt': prompt
                }
            )
            response.raise_for_status()
            data = response.json()

            return data.get('embedding', [])

        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return None


def get_ollama_provider(base_url: str = "http://localhost:11434") -> OllamaProvider:
    """Get Ollama provider instance"""
    return OllamaProvider(base_url)
