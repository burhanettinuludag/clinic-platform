import json
import logging
import re
from services.base_agent import BaseAgent

logger = logging.getLogger(__name__)

QUALITY_PROMPT = """Sen bir tibbi icerik kalite kontrol uzmanisin.
Icerigi tibbi dogruluk, dil kalitesi, platform uyumu ve etik acisindan degerlendir.

Her kategoriyi 0-100 arasi puanla. Sonucu JSON formatinda don:
{
    "medical_accuracy": {"score": 85, "issues": []},
    "language_quality": {"score": 90, "issues": []},
    "platform_compliance": {"score": 75, "issues": []},
    "ethics": {"score": 95, "issues": []},
    "overall_score": 86,
    "decision": "publish",
    "summary": "Genel degerlendirme"
}

decision kurallari:
- overall_score >= 80 -> "publish"
- overall_score 60-79 -> "revise"
- overall_score < 60 -> "reject"
"""


class QualityAgent(BaseAgent):
    name = "quality_agent"
    description = "Icerik kalite kontrol ajani"

    def __init__(self):
        super().__init__()
        self.system_prompt = QUALITY_PROMPT

    def execute(self, input_data: dict) -> dict:
        title = input_data.get("title_tr", "")
        body = input_data.get("body_tr", "")

        user_prompt = f"""Asagidaki icerigi degerlendir:

BASLIK: {title}

ICERIK:
{body[:3000]}

Puanla ve JSON formatinda don."""

        response = self.llm_call(user_prompt)
        return self._parse_response(response.content)

    def _parse_response(self, content: str) -> dict:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group(0))
                if "overall_score" not in parsed:
                    scores = []
                    for key in ["medical_accuracy", "language_quality", "platform_compliance", "ethics"]:
                        if isinstance(parsed.get(key), dict):
                            scores.append(parsed[key].get("score", 0))
                    parsed["overall_score"] = sum(scores) // max(len(scores), 1)
                if "decision" not in parsed:
                    s = parsed["overall_score"]
                    parsed["decision"] = "publish" if s >= 80 else "revise" if s >= 60 else "reject"
                return parsed
            except json.JSONDecodeError:
                pass
        return {"overall_score": 0, "decision": "reject", "error": "Parse hatasi"}

    def validate_output(self, output: dict):
        return None
