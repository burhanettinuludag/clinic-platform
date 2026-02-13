import json
import logging
import re
from services.base_agent import BaseAgent
from services.prompts.editor_prompts import EDITOR_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class EditorAgent(BaseAgent):
    name = "editor_agent"
    description = "Otonom icerik son kontrol ve yayin karari ajani"

    def __init__(self):
        super().__init__()
        self.system_prompt = EDITOR_SYSTEM_PROMPT

    def execute(self, input_data: dict) -> dict:
        content = input_data.get("content", input_data)
        qa_result = input_data.get("qa_result", {})
        seo_result = input_data.get("seo_result", {})

        user_prompt = f"""Icerik ve degerlendirme sonuclarini inceleyerek yayin karari ver:

BASLIK: {content.get("title_tr", "")}
ICERIK (ilk 2000 karakter): {content.get("body_tr", "")[:2000]}

QA SKOR: {qa_result.get("overall_score", 0)}
QA KARAR: {qa_result.get("decision", "bilinmiyor")}

Son karari ver: yayinla, duzelt veya reddet."""

        response = self.llm_call(user_prompt)
        return self._parse_response(response.content)

    def _parse_response(self, content: str) -> dict:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        return {"decision": "revise", "final_score": 0, "error": "Parse hatasi"}
