"""
Marketing Content Agent - Sosyal medya icerik uretici.

Instagram, LinkedIn, Twitter postlari uretir.
Hekim onaylamadan yayinlanmaz.
"""

import json
import logging
import re
from typing import Optional

from services.base_agent import BaseAgent
from services.prompts.marketing_prompts import MARKETING_CONTENT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class MarketingContentAgent(BaseAgent):
    """Sosyal medya icerik uretici - Instagram, LinkedIn, Twitter postlari."""

    name = 'marketing_content_agent'
    task_type = 'marketing_content'
    system_prompt = MARKETING_CONTENT_SYSTEM_PROMPT
    feature_flag_key = 'agent_marketing_content'
    temperature = 0.8  # Yaraticilik biraz yuksek
    max_tokens = 3000

    def execute(self, input_data: dict) -> dict:
        """
        Sosyal medya icerikleri uret.

        Input:
            theme: str - Haftalik ana tema (or: "migren tetikleyicileri")
            platforms: list - Hedef platformlar (default: ["instagram", "linkedin", "twitter"])
            posts_per_platform: int - Platform basina post sayisi (default: 3)
            language: str - Dil (default: "tr", secenek: "tr", "en", "both")
            tone: str - Ton (default: "educational", secenekler: educational, motivational, awareness, promotional)
            include_video_script: bool - Kisa video script'i dahil mi (default: true)
            target_audience: str - Hedef kitle (default: "patients", secenek: patients, caregivers, doctors, general)

        Output:
            {
                "theme": "...",
                "instagram_posts": [{"text": "...", "hashtags": [...], "suggested_format": "carousel/single/reel"}, ...],
                "linkedin_posts": [{"text_tr": "...", "text_en": "...", "hashtags": [...]}, ...],
                "twitter_posts": [{"text": "...", "hashtags": [...]}, ...],
                "video_script": {"title": "...", "duration_seconds": 30, "hook": "...", "body": "...", "cta": "...", "text_overlay_suggestions": [...]}
            }
        """
        theme = input_data.get('theme', '')
        if not theme:
            return {'error': 'Tema (theme) belirtilmedi'}

        platforms = input_data.get('platforms', ['instagram', 'linkedin', 'twitter'])
        posts_per_platform = input_data.get('posts_per_platform', 3)
        language = input_data.get('language', 'tr')
        tone = input_data.get('tone', 'educational')
        include_video = input_data.get('include_video_script', True)
        audience = input_data.get('target_audience', 'patients')

        prompt = self._build_prompt(
            theme, platforms, posts_per_platform, language,
            tone, include_video, audience
        )
        response = self.llm_call(prompt)

        parsed = self._safe_parse_json(response.content)
        parsed['llm_provider'] = response.provider
        parsed['tokens_used'] = response.tokens_used
        return parsed

    def _build_prompt(
        self, theme, platforms, posts_per_platform,
        language, tone, include_video, audience
    ):
        """LLM'e gonderilecek prompt'u olustur."""
        video_instruction = ""
        if include_video:
            video_instruction = """
"video_script": {{
    "title": "...",
    "duration_seconds": 30-60,
    "hook": "Ilk 3 saniye - dikkat cekici acilis",
    "body": "Ana mesaj",
    "cta": "Kapanis ve yonlendirme",
    "text_overlay_suggestions": ["..."]
}}"""

        return f"""Asagidaki tema icin sosyal medya icerikleri uret:

TEMA: {theme}
PLATFORMLAR: {', '.join(platforms)}
HER PLATFORM ICIN POST SAYISI: {posts_per_platform}
DIL: {language}
TON: {tone}
HEDEF KITLE: {audience}
VIDEO SCRIPTI: {"Evet" if include_video else "Hayir"}

JSON formatinda yanit ver. Her Instagram postu icin suggested_format (carousel/single/reel) belirt.
Twitter postlari 280 karakteri gecmesin.
LinkedIn postlari profesyonel ve detayli olsun.
{"Video scripti 30-60 saniyelik, hook-body-cta yapisinda olsun." if include_video else ""}

Yanit formati:
{{
    "theme": "...",
    "instagram_posts": [{{"text": "...", "hashtags": ["..."], "suggested_format": "carousel"}}],
    "linkedin_posts": [{{"text_tr": "...", "text_en": "...", "hashtags": ["..."]}}],
    "twitter_posts": [{{"text": "...", "hashtags": ["..."]}}]{f', {video_instruction}' if include_video else ''}
}}

SADECE JSON dondur, baska bir sey yazma."""

    def _safe_parse_json(self, content: str) -> dict:
        """JSON parse et, hata durumunda raw text dondur."""
        # Markdown code block temizle
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*', '', content)
        content = content.strip()

        # Dogrudan parse dene
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # En dis { } blogu bul
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        return {'raw_content': content, 'parse_error': True}

    def validate_output(self, output: dict) -> Optional[str]:
        """Cikti dogrulama."""
        if output.get('error'):
            return output['error']
        if output.get('parse_error'):
            return 'JSON parse hatasi'
        if not (
            output.get('instagram_posts')
            or output.get('linkedin_posts')
            or output.get('twitter_posts')
        ):
            return 'Hicbir platform icin icerik uretilemedi'
        return None
