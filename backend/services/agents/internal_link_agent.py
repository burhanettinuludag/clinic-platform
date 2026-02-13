import json
import logging
import re
from services.base_agent import BaseAgent
from services.prompts.link_prompts import INTERNAL_LINK_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class InternalLinkAgent(BaseAgent):
    name = "internal_link_agent"
    description = "Icerikler arasi internal link onerisi ajani"
    task_type = "add_links"

    def __init__(self):
        super().__init__()
        self.system_prompt = INTERNAL_LINK_SYSTEM_PROMPT

    def execute(self, input_data: dict) -> dict:
        title = input_data.get("title_tr", "")
        body = input_data.get("body_tr", "")
        existing_pages = input_data.get("existing_pages", [])
        existing_products = input_data.get("existing_products", [])

        user_prompt = f"""Icerik icin internal link oner:

BASLIK: {title}
ICERIK: {body[:3000]}

MEVCUT SAYFALAR: {json.dumps(existing_pages[:30], ensure_ascii=False)}
MEVCUT URUNLER: {json.dumps(existing_products[:10], ensure_ascii=False)}

Dogal ve anlamli linkler oner."""

        response = self.llm_call(user_prompt)
        return self._parse_response(response.content)

    def _parse_response(self, content: str) -> dict:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        return {"suggested_links": [], "error": "Parse hatasi"}
