import json
import logging
import re
from services.base_agent import BaseAgent
from services.prompts.publishing_prompts import PUBLISHING_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class PublishingAgent(BaseAgent):
    name = "publishing_agent"
    description = "Doktor yazilarini degerlendiren yayin editoru ajani"

    def __init__(self):
        super().__init__()
        self.system_prompt = PUBLISHING_SYSTEM_PROMPT

    def execute(self, input_data: dict) -> dict:
        title = input_data.get("title", "")
        body = input_data.get("body", "")
        author_name = input_data.get("author_name", "")
        author_specialty = input_data.get("author_specialty", "")
        author_level = input_data.get("author_level", 0)

        user_prompt = f"""Doktor yazisini degerlendir:

YAZAR: {author_name} ({author_specialty}) - Seviye: {author_level}
BASLIK: {title}
YAZI: {body[:4000]}

Tibbi dogruluk, dil, SEO, etik ve icerik kalitesi puanla. Ilac promosyonu tara."""

        response = self.llm_call(user_prompt)
        result = self._parse_response(response.content)

        overall = result.get("overall_score", 0)
        min_score = {0: 999, 1: 80, 2: 70, 3: 60, 4: 0}.get(author_level, 999)
        result["auto_publish"] = overall >= min_score and not result.get("promotion_flags")
        result["requires_chief_editor"] = author_level == 0
        return result

    def _parse_response(self, content: str) -> dict:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        return {"overall_score": 0, "decision": "reject", "error": "Parse hatasi"}
