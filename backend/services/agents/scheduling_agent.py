"""
Scheduling Agent - Haftalik sosyal medya yayin takvimi.

MarketingContentAgent ciktisindaki postlari gun ve saatlere dagitir.
En iyi engagement saatlerine gore plan olusturur.
"""

import json
import logging
import re
from typing import Optional

from services.base_agent import BaseAgent
from services.prompts.marketing_prompts import SCHEDULING_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class SchedulingAgent(BaseAgent):
    """Haftalik sosyal medya yayin takvimi olusturan agent."""

    name = 'scheduling_agent'
    task_type = 'schedule_plan'
    system_prompt = SCHEDULING_SYSTEM_PROMPT
    feature_flag_key = 'agent_scheduling'
    temperature = 0.5  # Daha deterministik
    max_tokens = 1500

    def execute(self, input_data: dict) -> dict:
        """
        Haftalik yayin plani olustur.

        Input:
            posts: list - Uretilen tum postlar (content agent ciktisi)
                         (veya pipeline data'sindan instagram_posts/linkedin_posts/twitter_posts)
            week_start: str - Hafta baslangici (ISO date, or: "2026-02-17")
            platforms: list - Platformlar

        Output:
            {
                "week_start": "2026-02-17",
                "week_end": "2026-02-23",
                "schedule": [
                    {
                        "day": "Pazartesi",
                        "date": "2026-02-17",
                        "slots": [
                            {
                                "time": "09:00",
                                "platform": "instagram",
                                "post_index": 0,
                                "post_preview": "Ilk 50 karakter...",
                                "content_type": "carousel",
                                "notes": "Sabah motivasyon postu"
                            }
                        ]
                    }
                ],
                "summary": "Bu hafta 5 Instagram, 3 LinkedIn, 3 Twitter postu planlandi.",
                "tips": ["Cuma postu engage orani yuksek, interaktif soru sorun"]
            }
        """
        # Pipeline'dan gelen postlari topla
        posts = input_data.get('posts', [])
        if not posts:
            posts = self._collect_posts_from_pipeline(input_data)

        week_start = input_data.get('week_start', '')
        platforms = input_data.get('platforms', ['instagram', 'linkedin', 'twitter'])

        if not posts:
            return {'error': 'Post verisi belirtilmedi'}

        prompt = self._build_prompt(posts, week_start, platforms)
        response = self.llm_call(prompt)

        parsed = self._safe_parse_json(response.content)
        parsed['llm_provider'] = response.provider
        parsed['tokens_used'] = response.tokens_used
        return parsed

    def _collect_posts_from_pipeline(self, data: dict) -> list:
        """Pipeline data'sindan postlari topla."""
        posts = []

        for post in data.get('instagram_posts', []):
            posts.append({
                'platform': 'instagram',
                'text': post.get('text', ''),
                'suggested_format': post.get('suggested_format', 'single'),
            })

        for post in data.get('linkedin_posts', []):
            posts.append({
                'platform': 'linkedin',
                'text': post.get('text_tr', post.get('text', '')),
                'suggested_format': 'single',
            })

        for post in data.get('twitter_posts', []):
            posts.append({
                'platform': 'twitter',
                'text': post.get('text', ''),
                'suggested_format': 'single',
            })

        return posts

    def _build_prompt(self, posts: list, week_start: str, platforms: list) -> str:
        """LLM'e gonderilecek prompt'u olustur."""
        post_summary = []
        for i, post in enumerate(posts):
            platform = post.get('platform', 'unknown')
            text = post.get('text', post.get('text_tr', ''))[:100]
            fmt = post.get('suggested_format', 'single')
            post_summary.append(f"Post {i}: [{platform}] ({fmt}) {text}")

        return f"""Asagidaki postlar icin haftalik yayin plani olustur:

HAFTA BASLANGICI: {week_start or 'Bu haftanin Pazartesi gunu'}
PLATFORMLAR: {', '.join(platforms)}

MEVCUT POSTLAR:
{chr(10).join(post_summary)}

Kurallar:
- Gunde en fazla 2 post
- Ayni platforma arka arkaya gunlerde post atma
- Sabah (08-09), ogle (12-13), aksam (19-21) slotlarini kullan
- Pazartesi motivasyon, Carsamba bilgi, Cuma wellness agirlikli

JSON formatinda yanit ver:
{{
    "week_start": "...",
    "week_end": "...",
    "schedule": [
        {{
            "day": "Pazartesi",
            "date": "...",
            "slots": [
                {{
                    "time": "09:00",
                    "platform": "...",
                    "post_index": 0,
                    "post_preview": "Ilk 50 karakter...",
                    "content_type": "...",
                    "notes": "..."
                }}
            ]
        }}
    ],
    "summary": "...",
    "tips": ["..."]
}}

SADECE JSON dondur, baska bir sey yazma."""

    def _safe_parse_json(self, content: str) -> dict:
        """JSON parse et, hata durumunda raw text dondur."""
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*', '', content)
        content = content.strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

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
        if not output.get('schedule'):
            return 'Yayin plani uretilemedi'
        return None
