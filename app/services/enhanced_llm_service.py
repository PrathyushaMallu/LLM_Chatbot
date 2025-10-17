"""Enhanced LLM service supporting multiple providers (OpenAI and Gemini).

This module exposes a single global instance `enhanced_llm_service` which
wraps configured providers and provides a safe local fallback. It accepts
provider names as either strings ("openai", "gemini") or as the
LLMProvider enum.
"""

import asyncio
import time
import logging
import sys
import os
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum

from config.settings import settings
from app.models.chat_models import LLMConfig

try:
    import openai
except Exception:
    openai = None


class LLMProvider(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"


class GeminiService:
    """Thin wrapper for google-generativeai client. Lazily imported."""

    def __init__(self, api_key: str):
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key
        self._client = None

    async def _get_client(self):
        if self._client is None:
            try:
                import google.generativeai as genai

                genai.configure(api_key=self.api_key)
                self._client = genai
                self.logger.info("Gemini client initialized successfully")
            except ImportError:
                raise ImportError(
                    "google-generativeai package not installed. Install with: pip install google-generativeai"
                )
            except Exception as e:
                self.logger.error(f"Failed to initialize Gemini client: {e}")
                raise
        return self._client

    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        parts: List[str] = []
        for m in messages:
            r = m.get("role", "user")
            c = m.get("content", "")
            if r == "system":
                parts.append(f"System: {c}")
            elif r == "user":
                parts.append(f"User: {c}")
            else:
                parts.append(f"Assistant: {c}")
        return "\n\n".join(parts) + "\n\nAssistant:"

    async def generate_response(
        self,
        messages: List[Dict[str, Any]],
        model: str = "gemini-pro",
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> Dict[str, Any]:
        client = await self._get_client()
        prompt = self._convert_messages_to_prompt(messages)
        generation_config = {"temperature": temperature, "max_output_tokens": max_tokens}
        model_instance = client.GenerativeModel(model_name=model, generation_config=generation_config)
        start = time.time()
        # run blocking generate on a thread
        response = await asyncio.to_thread(model_instance.generate_content, prompt)
        elapsed = time.time() - start

        # Gemini responses can come in several shapes. The simple `.text` accessor
        # only works for single-Part responses. Newer responses expose parts under
        # `result.parts` or under `candidates[index].content.parts`. Handle them robustly.
        def _extract_text_from_gemini(resp) -> str:
            try:
                # 1) simple text attribute (older/simpler responses)
                if hasattr(resp, "text") and resp.text:
                    return resp.text

                # 2) support resp.result.parts
                res = getattr(resp, "result", None)
                if res is not None:
                    parts = getattr(res, "parts", None)
                    if parts:
                        # parts may be a list of strings
                        return "".join(parts)

                # 3) support candidates -> content -> parts
                candidates = getattr(resp, "candidates", None)
                if candidates:
                    # take first candidate
                    first = candidates[0]
                    # candidate may be a dict-like or object
                    content = getattr(first, "content", None) or (first.get("content") if isinstance(first, dict) else None)
                    if content is not None:
                        parts = getattr(content, "parts", None) or (content.get("parts") if isinstance(content, dict) else None)
                        if parts:
                            return "".join(parts)

                # 4) some SDKs return a `.candidates` where parts are nested under .content[0].parts
                # try defensive introspection
                try:
                    # try dict-style access as a fallback
                    if isinstance(resp, dict):
                        # check for result.parts
                        if "result" in resp and isinstance(resp["result"], dict) and "parts" in resp["result"]:
                            return "".join(resp["result"]["parts"])
                        if "candidates" in resp and isinstance(resp["candidates"], list) and resp["candidates"]:
                            c = resp["candidates"][0]
                            if isinstance(c, dict):
                                cont = c.get("content")
                                if isinstance(cont, dict) and "parts" in cont:
                                    return "".join(cont["parts"])
                except Exception:
                    pass

                # 5) last resort: stringify the response - may include useful text
                return str(resp)
            except Exception:
                return ""

        text = _extract_text_from_gemini(response) or ""
        tokens = int(len(text.split()) * 1.3) if text else 0
        return {
            "response": text or "",
            "model": model,
            "provider": LLMProvider.GEMINI.value,
            "tokens_used": tokens,
            "response_time": elapsed,
            "processing_time": elapsed,
            "timestamp": datetime.utcnow().isoformat(),
            "finish_reason": "stop",
        }


class EnhancedLLMService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.providers: Dict[LLMProvider, Any] = {}

        # Initialize OpenAI client if configured and available
        if getattr(settings, "openai_api_key", None) and openai is not None:
            try:
                # openai.AsyncOpenAI may not always be available depending on SDK
                # fallback to openai if necessary
                client = getattr(openai, "AsyncOpenAI", None)
                if client is not None:
                    self.providers[LLMProvider.OPENAI] = client(api_key=settings.openai_api_key)
                else:
                    self.providers[LLMProvider.OPENAI] = openai
                self.logger.info("OpenAI client initialized")
            except Exception as e:
                self.logger.warning(f"OpenAI init failed: {e}")

        # Initialize Gemini service if configured
        if getattr(settings, "gemini_api_key", None):
            try:
                self.providers[LLMProvider.GEMINI] = GeminiService(settings.gemini_api_key)
                self.logger.info("Gemini client registered")
            except Exception as e:
                self.logger.warning(f"Gemini init failed: {e}")

        # default provider (map string to enum safely)
        self.default_provider: Optional[LLMProvider] = None
        if getattr(settings, "default_llm_provider", None):
            try:
                val = getattr(settings, "default_llm_provider")
                self.default_provider = self._map_provider(val)
            except Exception:
                self.default_provider = None

    def _map_provider(self, provider: Optional[Union[str, LLMProvider]]) -> Optional[LLMProvider]:
        if provider is None:
            return None
        if isinstance(provider, LLMProvider):
            return provider
        try:
            p = str(provider).lower()
            return LLMProvider(p)
        except Exception:
            return None

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        provider: Optional[Union[str, LLMProvider]] = None,
        config: Optional[LLMConfig] = None,
    ) -> Dict[str, Any]:
        # normalize provider
        mapped = self._map_provider(provider) if provider is not None else None

        # choose provider: explicit -> default -> prefer Gemini -> first available -> local fallback
        provider_to_use = mapped or self.default_provider
        if provider_to_use is None:
            if LLMProvider.GEMINI in self.providers:
                provider_to_use = LLMProvider.GEMINI
            elif self.providers:
                provider_to_use = list(self.providers.keys())[0]

        # pick config defaults - make provider-aware so Gemini gets a Gemini model
        if config is None:
            cfg_temp = getattr(settings, "temperature", 0.7)
            cfg_max = getattr(settings, "max_tokens", 4000)
            if provider_to_use == LLMProvider.GEMINI:
                cfg_model = getattr(settings, "gemini_model", "gemini-1.0")
            else:
                cfg_model = getattr(settings, "openai_model", "gpt-3.5-turbo")
            config = LLMConfig(model=cfg_model, temperature=cfg_temp, max_tokens=cfg_max)

        # no external providers
        if provider_to_use is None or provider_to_use not in self.providers:
            self.logger.info("No external provider selected/available - using local fallback")
            return await self._generate_local_response(messages, config)

        # route to provider with runtime safety
        try:
            if provider_to_use == LLMProvider.GEMINI:
                svc = self.providers.get(LLMProvider.GEMINI)
                if svc is None:
                    return await self._generate_local_response(messages, config)
                # prefer gemini model from settings unless overridden by config
                gemini_model = config.model if (config and config.model) else getattr(settings, "gemini_model", "gemini-1.0")
                self.logger.info(f"Routing to Gemini model={gemini_model} temp={config.temperature} max_tokens={config.max_tokens}")
                return await svc.generate_response(messages=messages, model=gemini_model, temperature=config.temperature, max_tokens=config.max_tokens)

            if provider_to_use == LLMProvider.OPENAI:
                return await self._generate_openai_response(messages, config)

            return await self._generate_local_response(messages, config)
        except Exception as e:
            self.logger.exception(f"LLM provider {provider_to_use} failed: {e}")
            return await self._generate_local_response(messages, config)

    async def _generate_openai_response(self, messages: List[Dict[str, str]], config: LLMConfig) -> Dict[str, Any]:
        client = self.providers.get(LLMProvider.OPENAI)
        if client is None:
            return await self._generate_local_response(messages, config)
        start = time.time()
        # Try to use the modern SDK interface if available; otherwise fall back
        if hasattr(client, "chat"):
            # openai.AsyncOpenAI or openai module
            resp = await client.chat.completions.create(model=config.model, messages=messages, max_tokens=config.max_tokens, temperature=config.temperature, stream=False)
            elapsed = time.time() - start
            content = resp.choices[0].message.content
            tokens = getattr(resp.usage, "total_tokens", None)
        else:
            # Fallback: call sync API on a thread (older SDKs)
            def _sync_call():
                return openai.ChatCompletion.create(model=config.model, messages=messages, max_tokens=config.max_tokens, temperature=config.temperature)

            resp = await asyncio.to_thread(_sync_call)
            elapsed = time.time() - start
            content = resp["choices"][0]["message"]["content"]
            tokens = resp.get("usage", {}).get("total_tokens")

        return {
            "response": content,
            "model": config.model,
            "provider": LLMProvider.OPENAI.value,
            "tokens_used": tokens,
            "response_time": elapsed,
            "processing_time": elapsed,
            "timestamp": datetime.utcnow().isoformat(),
            "finish_reason": getattr(resp.choices[0], "finish_reason", None) if hasattr(resp, "choices") else None,
        }

    async def _generate_local_response(self, messages: List[Dict[str, str]], config: Optional[LLMConfig] = None) -> Dict[str, Any]:
        start = time.time()
        last_user = None
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user = m.get("content")
                break
        if not last_user:
            reply = "Hello! I'm running in local fallback mode. How can I help you?"
        else:
            reply = f"(Local) I received: '{last_user}'. This is a local fallback response."
        elapsed = time.time() - start
        return {
            "response": reply,
            "model": "local-fallback",
            "provider": "local",
            "tokens_used": len(reply.split()),
            "response_time": elapsed,
            "processing_time": elapsed,
            "timestamp": datetime.utcnow().isoformat(),
            "finish_reason": "local",
        }


# single global instance for the app to reuse
enhanced_llm_service = EnhancedLLMService()