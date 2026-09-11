import os
import json
import logging
import requests
from config import Config

logger = logging.getLogger("decision_ai.llm")

class LLMClient:
    def __init__(self, api_key: str = None):
        self.api_key = (api_key or Config.GEMINI_API_KEY or "").strip()
        # Default Gemini model endpoint
        self.model = "gemini-1.5-flash"
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def has_valid_key(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 10)

    def generate_json(self, system_instruction: str, user_prompt: str) -> dict:
        """
        Calls Gemini API with instructions to return valid JSON.
        If no API key is provided or the network call fails, falls back gracefully.
        """
        if not self.has_valid_key():
            logger.info("No Gemini API key provided. Using built-in simulation engine fallback.")
            return None

        try:
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {"text": f"System Instruction:\n{system_instruction}\n\nTask:\n{user_prompt}\n\nIMPORTANT: Respond ONLY with a valid JSON object. Do not include markdown code block formatting like ```json ... ``` outside the object if possible, or provide raw JSON."}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.3,
                    "topP": 0.95,
                    "responseMimeType": "application/json"
                }
            }

            url = f"{self.endpoint}?key={self.api_key}"
            response = requests.post(url, headers=headers, json=payload, timeout=25)
            
            if response.status_code != 200:
                logger.warning(f"Gemini API returned status {response.status_code}: {response.text}")
                return None

            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                return None

            raw_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            return self._clean_and_parse_json(raw_text)

        except Exception as e:
            logger.error(f"Error communicating with Gemini API: {e}")
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

