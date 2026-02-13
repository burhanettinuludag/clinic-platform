import json
import logging
import re
from services.base_agent import BaseAgent
from services.prompts.news_prompts import NEWS_SYSTEM_PROMPT, NEWS_FDA_PROMPT, NEWS_CLINICAL_TRIAL_PROMPT

logger = logging.getLogger(__name__)


class NewsAgent(BaseAgent):
    name = "news_agent"
    description = "Noroloji haber icerigi ureten ajan"

    def __init__(self):
        super().__init__()
        self.system_prompt = NEWS_SYSTEM_PROMPT

    def execute(self, input_data: dict) -> dict:
        news_type = input_data.get("type", "general")
        topic = input_data.get("topic", "")
        source = input_data.get("source", "")

        if news_type == "fda_approval":
            user_prompt = NEWS_FDA_PROMPT.format(topic=topic, source=source)
        elif news_type == "clinical_trial":
            study = input_data.get("study", topic)
            journal = input_data.get("journal", "")
            user_prompt = NEWS_CLINICAL_TRIAL_PROMPT.format(study=study, journal=journal, source=source)
        else:
            user_prompt = f"Asagidaki noroloji konusu hakkinda haber yaz:\nKonu: {topic}\nKaynak: {source}"

        response = self.llm_call(user_prompt)
        return self._parse_response(response.content)

    def _parse_response(self, content: str) -> dict:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        return {"title_tr": "", "body_tr": content, "category": "popular_science", "parse_error": True}
