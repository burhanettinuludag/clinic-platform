"""
Visual Brief Agent - Sosyal medya gorselleri icin tasarim brief'leri.

MarketingContentAgent ciktisindaki postlar icin
Canva/Figma uyumlu gorsel brief'ler uretir.
"""

import json
import logging
import re
from typing import Optional

from services.base_agent import BaseAgent
from services.prompts.marketing_prompts import VISUAL_BRIEF_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class VisualBriefAgent(BaseAgent):
    """Sosyal medya gorselleri icin tasarim brief'leri ureten agent."""

    name = 'visual_brief_agent'
    task_type = 'visual_brief'
    system_prompt = VISUAL_BRIEF_SYSTEM_PROMPT
    feature_flag_key = 'agent_visual_brief'
    temperature = 0.7
    max_tokens = 2000

    def execute(self, input_data: dict) -> dict:
        """
        Her post icin gorsel brief uret.

        Input:
            posts: list - MarketingContentAgent ciktisindan gelen postlar
                         (veya pipeline data'sindan instagram_posts/linkedin_posts/twitter_posts)
            theme: str - Ana tema
            brand_style: str - Stil tercihi (default: "clean_medical")

        Output:
            {
                "briefs": [
                    {
                        "post_index": 0,
                        "platform": "instagram",
                        "format": "carousel",
                        "dimensions": "1080x1080",
                        "color_palette": ["#1B4F72", "#FFFFFF", "#00BCD4"],
                        "layout_description": "...",
                        "visual_elements": ["beyin illustrasyonu", "checklist ikonlari"],
                        "text_on_image": ["Slide 1: Baslik", "Slide 2: Madde 1"],
                        "canva_notes": "...",
                        "mood": "informative, hopeful, clean"
                    }
                ]
            }
        """
        theme = input_data.get('theme', '')

        # Pipeline'dan gelen postlari topla
        posts = input_data.get('posts', [])
        if not posts:
            posts = self._collect_posts_from_pipeline(input_data)

        if not posts:
            return {'error': 'Post verisi (posts) belirtilmedi', 'briefs': []}

        prompt = self._build_prompt(theme, posts)
        response = self.llm_call(prompt)

        parsed = self._safe_parse_json(response.content)
        parsed['llm_provider'] = response.provider
        parsed['tokens_used'] = response.tokens_used
        return parsed

    def _collect_posts_from_pipeline(self, data: dict) -> list:
        """Pipeline data'sindan postlari topla (MarketingContentAgent ciktisi)."""
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

    def _build_prompt(self, theme: str, posts: list) -> str:
        """LLM'e gonderilecek prompt'u olustur."""
        post_summary = []
        for i, post in enumerate(posts):
            platform = post.get('platform', 'unknown')
            text = post.get('text', post.get('text_tr', ''))[:200]
            fmt = post.get('suggested_format', 'single')
            post_summary.append(f"Post {i+1} ({platform}, {fmt}): {text}...")

        return f"""Asagidaki sosyal medya postlari icin gorsel tasarim brief'leri olustur:

TEMA: {theme}

POSTLAR:
{chr(10).join(post_summary)}

Her post icin detayli brief uret. Canva veya benzeri aracta uygulanabilir talimatlar ver.
Boyutlar: Instagram post 1080x1080, story 1080x1920, LinkedIn 1200x627, Twitter 1600x900.

JSON formatinda yanit ver:
{{
    "briefs": [
        {{
            "post_index": 0,
            "platform": "...",
            "format": "...",
            "dimensions": "...",
            "color_palette": ["#1B4F72", "#FFFFFF", "#00BCD4"],
            "layout_description": "...",
            "visual_elements": ["..."],
            "text_on_image": ["..."],
            "canva_notes": "...",
            "mood": "..."
        }}
    ]
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

        return {'raw_content': content, 'parse_error': True, 'briefs': []}

    def validate_output(self, output: dict) -> Optional[str]:
        """Cikti dogrulama."""
        if output.get('error'):
            return output['error']
        if output.get('parse_error'):
            return 'JSON parse hatasi'
        if not output.get('briefs'):
            return 'Hicbir brief uretilemedi'
        return None
