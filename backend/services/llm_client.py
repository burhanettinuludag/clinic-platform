"""
LLM API Client - Birlesik istemci.
Groq (birincil) + Gemini (yedek) + fallback mekanizmasi.

Kullanim:
    from services.llm_client import llm_client
    response = llm_client.chat("Merhaba", system_prompt="Sen bir asistansin.")
"""

import json
import logging
import time
from dataclasses import dataclass
from typing import Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """LLM API yanit objesi."""
    content: str
    provider: str
    model: str
    tokens_used: int
    duration_ms: int
    raw: dict


class LLMClient:
    """
    Birlesik LLM API istemcisi.

    - Birincil: Groq (Llama 3.1 70B)
    - Yedek: Google Gemini 2.0 Flash
    - Otomatik fallback + retry
    """

    PROVIDERS = {
        'groq': {
            'url': 'https://api.groq.com/openai/v1/chat/completions',
            'model': 'llama-3.3-70b-versatile',
            'key_setting': 'GROQ_API_KEY',
        },
        'gemini': {
            'url': 'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
            'model': 'gemini-2.0-flash',
            'key_setting': 'GEMINI_API_KEY',
        },
    }

    def __init__(self):
        self.primary = getattr(settings, 'LLM_PRIMARY_PROVIDER', 'groq')
        self.fallback = getattr(settings, 'LLM_FALLBACK_PROVIDER', 'gemini')
        self.max_retries = getattr(settings, 'LLM_MAX_RETRIES', 2)
        self.timeout = getattr(settings, 'LLM_TIMEOUT_SECONDS', 30)

    def chat(
        self,
        user_message: str,
        system_prompt: str = '',
        temperature: float = 0.7,
        max_tokens: int = 2000,
        provider: Optional[str] = None,
    ) -> LLMResponse:
        """
        LLM'e mesaj gonder, yanit al.

        Args:
            user_message: Kullanici mesaji
            system_prompt: Sistem rolu tanimlamasi
            temperature: Yaraticilik (0.0-1.0)
            max_tokens: Maksimum yanit uzunlugu
            provider: Belirli provider zorla (None ise fallback mekanizmasi)

        Returns:
            LLMResponse objesi

        Raises:
            LLMError: Tum providerlar basarisiz olursa
        """
        providers_to_try = (
            [provider] if provider
            else [self.primary, self.fallback]
        )

        last_error = None
        for prov in providers_to_try:
            for attempt in range(self.max_retries):
                try:
                    return self._call_provider(
                        prov, user_message, system_prompt,
                        temperature, max_tokens
                    )
                except Exception as e:
                    last_error = e
                    logger.warning(
                        f"LLM call failed: provider={prov}, "
                        f"attempt={attempt+1}/{self.max_retries}, "
                        f"error={str(e)}"
                    )
                    if attempt < self.max_retries - 1:
                        time.sleep(1 * (attempt + 1))  # Exponential backoff

        raise LLMError(f"Tum LLM providerlari basarisiz: {last_error}")

    def _call_provider(
        self, provider: str, user_message: str,
        system_prompt: str, temperature: float, max_tokens: int
    ) -> LLMResponse:
        """Provider'a ozel API cagrisi."""
        start = time.time()

        if provider == 'groq':
            result = self._call_groq(
                user_message, system_prompt, temperature, max_tokens
            )
        elif provider == 'gemini':
            result = self._call_gemini(
                user_message, system_prompt, temperature, max_tokens
            )
        else:
            raise ValueError(f"Bilinmeyen provider: {provider}")

        duration_ms = int((time.time() - start) * 1000)
        result.duration_ms = duration_ms

        logger.info(
            f"LLM call success: provider={provider}, "
            f"tokens={result.tokens_used}, duration={duration_ms}ms"
        )
        return result

    def _call_groq(
        self, user_message, system_prompt, temperature, max_tokens
    ) -> LLMResponse:
        """Groq API (OpenAI uyumlu)."""
        api_key = getattr(settings, 'GROQ_API_KEY', '')
        if not api_key:
            raise LLMError("GROQ_API_KEY ayarlanmamis")

        config = self.PROVIDERS['groq']
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': user_message})

        resp = requests.post(
            config['url'],
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            },
            json={
                'model': config['model'],
                'messages': messages,
                'temperature': temperature,
                'max_tokens': max_tokens,
            },
            timeout=self.timeout,
        )
        resp.raise_for_status()
        data = resp.json()

        return LLMResponse(
            content=data['choices'][0]['message']['content'],
            provider='groq',
            model=config['model'],
            tokens_used=data.get('usage', {}).get('total_tokens', 0),
            duration_ms=0,
            raw=data,
        )

    def _call_gemini(
        self, user_message, system_prompt, temperature, max_tokens
    ) -> LLMResponse:
        """Google Gemini API."""
        api_key = getattr(settings, 'GEMINI_API_KEY', '')
        if not api_key:
            raise LLMError("GEMINI_API_KEY ayarlanmamis")

        config = self.PROVIDERS['gemini']
        url = config['url'].format(model=config['model']) + f'?key={api_key}'

        contents = []
        if system_prompt:
            contents.append({
                'role': 'user',
                'parts': [{'text': f'[System]: {system_prompt}'}]
            })
            contents.append({
                'role': 'model',
                'parts': [{'text': 'Anladim, bu role gore davranacagim.'}]
            })
        contents.append({
            'role': 'user',
            'parts': [{'text': user_message}]
        })

        resp = requests.post(
            url,
            json={
                'contents': contents,
                'generationConfig': {
                    'temperature': temperature,
                    'maxOutputTokens': max_tokens,
                },
            },
            timeout=self.timeout,
        )
        resp.raise_for_status()
        data = resp.json()

        content = data['candidates'][0]['content']['parts'][0]['text']
        tokens = data.get('usageMetadata', {}).get('totalTokenCount', 0)

        return LLMResponse(
            content=content,
            provider='gemini',
            model=config['model'],
            tokens_used=tokens,
            duration_ms=0,
            raw=data,
        )


class LLMError(Exception):
    """LLM API hatasi."""
    pass


# Singleton instance
llm_client = LLMClient()
