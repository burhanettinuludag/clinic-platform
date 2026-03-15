# AI Agent System Skill

## Triggers
agent, AI agent, content agent, pipeline, orchestrator, LLM, Groq, Gemini, FeatureFlag

## Architecture

### LLM Provider
- **Primary:** Groq Llama 3.3 70B Versatile (OpenAI-compatible API)
- **Fallback:** Google Gemini 2.0 Flash
- Client: `backend/services/llm_client.py` (singleton `LLMClient`)
- Auto-retry (2 retries per provider) + automatic fallback

Do NOT use Anthropic/OpenAI APIs. This project uses Groq + Gemini.

### Agent Framework
Base class: `backend/services/base_agent.py`
```python
from services.base_agent import BaseAgent

class MyAgent(BaseAgent):
    name = "my_agent"
    system_prompt = "Your role description..."
    feature_flag_key = "agent_my_feature"
    task_type = "my_task_type"
    temperature = 0.7
    max_tokens = 2000

    def execute(self, input_data: dict) -> dict:
        prompt = self.build_prompt(input_data)
        response = self.llm_call(prompt)
        return self.parse_response(response)
```

Lifecycle: `run()` → check FeatureFlag → create AgentTask → `execute()` → `validate_output()` → `check_gatekeeper_decision()` → log AuditLog

### Registered Agents (15)
All in `backend/services/agents/`:

| Agent | Purpose | Feature Flag |
|-------|---------|-------------|
| `content_agent` | Turkish medical content | `agent_content` |
| `seo_agent` | SEO optimization | `agent_seo` |
| `legal_agent` | Medical compliance (gatekeeper) | `agent_legal` |
| `translation_agent` | TR → EN translation | `agent_translation` |
| `uiux_agent` | UI/UX suggestions | `agent_uiux` |
| `qa_agent` | Patient Q&A (RAG) | `agent_qa` |
| `news_agent` | News article generation | — |
| `editor_agent` | Content editing | — |
| `publishing_agent` | Publishing preparation | — |
| `internal_link_agent` | Internal linking | — |
| `quality_agent` | Quality control (gatekeeper) | — |
| `devops_agent` | Code generation/review | — |
| `marketing_content_agent` | Social media content | `agent_marketing_content` |
| `visual_brief_agent` | Image/visual briefs | — |
| `scheduling_agent` | Publication scheduling | — |

### Registry
- `backend/services/registry.py` — singleton `agent_registry`
- Registration: `backend/services/agents/__init__.py`
- `agent_registry.get('content_agent')` to retrieve

### Orchestrator Pipelines (12)
`backend/services/orchestrator.py` — singleton `orchestrator`

| Pipeline | Steps | Gatekeeper |
|----------|-------|-----------|
| `full_content_v5` | content → seo → link → quality → editor | quality_agent |
| `publish_article` | content → seo → legal → translation | legal_agent |
| `news_pipeline` | news → seo → link → quality → editor | quality_agent |
| `doctor_article_review` | publishing → seo → link | — |
| `marketing_weekly` | marketing → visual_brief → scheduling | — |
| `answer_question` | qa_agent | — |
| `seo_optimize` | seo_agent | — |
| `legal_audit` | legal_agent | — |
| `content_with_translation` | content → translation | — |
| `quality_check` | quality → editor | — |
| `devops_code` | devops_agent | — |
| `devops_review` | devops_agent | — |

### Data Models
- `AgentTask` (`apps/common/models.py`): tracks token usage, cost, duration, status
- `FeatureFlag`: admin-controlled on/off per agent
- `SiteConfig`: key-value config (auto_content_topics, etc.)

### Prompts
All in `backend/services/prompts/` (14 files).

### Celery Tasks
- `auto_generate_weekly_content` — Monday 09:00
- `cleanup_old_agent_tasks` — daily 03:00
- `send_weekly_content_report` — Friday 17:00

### Creating a New Agent
1. Create `backend/services/agents/my_agent.py` with BaseAgent subclass
2. Create `backend/services/prompts/my_prompts.py`
3. Register in `backend/services/agents/__init__.py`
4. Add FeatureFlag in Django admin
5. Add to pipeline in orchestrator if needed
6. Add task_type to `AgentTask.TASK_TYPES`
