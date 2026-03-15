# Skill: AI Agents — Norosera

## Trigger
agent, AI agent, content agent, SEO agent, social media agent, otomasyon, yapay zeka

## Norosera Agent Registry

### 12 Agents
| Agent | Purpose | Trigger |
|-------|---------|---------|
| Content Agent | Blog yazıları, medikal içerik üretimi | "içerik yaz", "blog" |
| SEO Agent | Meta tag, sitemap, keyword optimization | "SEO", "arama motoru" |
| Legal Agent | KVKK metinleri, aydınlatma metni | "KVKK", "yasal" |
| Translation Agent | TR↔EN çeviri | "çevir", "translate" |
| UI/UX Agent | Component design, accessibility | "tasarım", "UI" |
| Q&A RAG Agent | Hasta soruları, bilgi tabanı | "soru-cevap", "RAG" |
| Social Media Agent | Instagram/LinkedIn post oluşturma | "sosyal medya", "post" |
| Analytics Agent | Site analytics, raporlama | "analytics", "rapor" |
| Patient Intake Agent | Hasta kayıt form optimizasyonu | "hasta kayıt" |
| Appointment Agent | Randevu yönetimi | "randevu" |
| Notification Agent | Email/SMS bildirim | "bildirim", "notification" |
| Report Agent | Klinik raporları oluşturma | "rapor oluştur" |

### Agent Implementation Pattern
```python
# apps/ai_agents/base.py
from abc import ABC, abstractmethod
from anthropic import Anthropic

class BaseAgent(ABC):
    def __init__(self):
        self.client = Anthropic()
        self.model = "claude-sonnet-4-20250514"

    @abstractmethod
    def system_prompt(self) -> str:
        pass

    @abstractmethod
    def process(self, input_data: dict) -> dict:
        pass

    def call_llm(self, messages: list, max_tokens: int = 2000) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=self.system_prompt(),
            messages=messages,
        )
        return response.content[0].text
```

### Agent as Celery Task
```python
# apps/ai_agents/tasks.py
@shared_task(bind=True, max_retries=2)
def run_content_agent(self, topic: str, language: str = "tr"):
    agent = ContentAgent()
    result = agent.process({"topic": topic, "language": language})
    BlogDraft.objects.create(
        title=result["title"],
        content=result["content"],
        seo_meta=result["meta"],
        status="draft",
    )
    return result
```

### Sub-agent Spawning in Claude Code
For complex tasks, spawn parallel sub-agents:
```
"Run Content Agent to draft a blog post about migren tedavisi,
 then pass output to SEO Agent for optimization,
 then pass to Translation Agent for EN version"
```
Claude Code will chain these as sequential sub-agents automatically.
