import os
import json
import logging
import requests
from config import Config

logger = logging.getLogger("decision_ai.llm")

class LLMClient:
    def __init__(self, openai_key: str = None, gemini_key: str = None):
        self.openai_key = (openai_key or Config.OPENAI_API_KEY or "").strip()
        self.gemini_key = (gemini_key or Config.GEMINI_API_KEY or "").strip()

        # Model settings
        self.openai_model = "gpt-4o-mini"
        self.openai_endpoint = "https://api.openai.com/v1/chat/completions"
        self.gemini_model = "gemini-1.5-flash"
        self.gemini_endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent"

    def get_active_provider(self) -> str:
        if bool(self.openai_key and len(self.openai_key) > 10):
            return "openai"
        elif bool(self.gemini_key and len(self.gemini_key) > 10):
            return "gemini"
        return "simulation"

    def has_valid_key(self) -> bool:
        return self.get_active_provider() in ("openai", "gemini")

    def generate_json(self, system_instruction: str, user_prompt: str) -> dict:
        """
        Calls the active LLM provider (OpenAI or Gemini) instructing it to return valid JSON.
        If no API key is provided or the network call fails, falls back gracefully.
        """
        provider = self.get_active_provider()

        if provider == "openai":
            return self._call_openai(system_instruction, user_prompt)
        elif provider == "gemini":
            return self._call_gemini(system_instruction, user_prompt)
        else:
            logger.info("No valid API key provided. Using built-in simulation engine fallback.")
            return None

    def _call_openai(self, system_instruction: str, user_prompt: str) -> dict:
        """Calls OpenAI Chat Completions API with structured JSON output."""
        try:
            headers = {
                "Authorization": f"Bearer {self.openai_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.openai_model,
                "messages": [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": f"{user_prompt}\n\nIMPORTANT: Return valid JSON only."}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.3
            }

            response = requests.post(self.openai_endpoint, headers=headers, json=payload, timeout=25)
            if response.status_code != 200:
                logger.warning(f"OpenAI API error {response.status_code}: {response.text}")
                return None

            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)

        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return None

    def _call_gemini(self, system_instruction: str, user_prompt: str) -> dict:
        """Calls Google Gemini API with JSON output instruction."""
        try:
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {"text": f"System Instruction:\n{system_instruction}\n\nTask:\n{user_prompt}\n\nIMPORTANT: Respond ONLY with a valid JSON object."}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.3,
                    "topP": 0.95,
                    "responseMimeType": "application/json"
                }
            }

            url = f"{self.gemini_endpoint}?key={self.gemini_key}"
            response = requests.post(url, headers=headers, json=payload, timeout=25)
            
            if response.status_code != 200:
                logger.warning(f"Gemini API error {response.status_code}: {response.text}")
                return None

            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                return None

            raw_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            return self._clean_and_parse_json(raw_text)

        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return None

    def _clean_and_parse_json(self, text: str) -> dict:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        try:
            return json.loads(text)
        except Exception as e:
            logger.error(f"Failed to parse LLM JSON output: {e}\nRaw: {text[:200]}")
            return None
