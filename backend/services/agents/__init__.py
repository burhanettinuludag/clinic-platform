from services.registry import agent_registry

from services.agents.content_agent import ContentAgent
agent_registry.register(ContentAgent())

from services.agents.seo_agent import SEOAgent
agent_registry.register(SEOAgent())

from services.agents.legal_agent import LegalAgent
agent_registry.register(LegalAgent())

from services.agents.translation_agent import TranslationAgent
agent_registry.register(TranslationAgent())

from services.agents.uiux_agent import UIUXAgent
agent_registry.register(UIUXAgent())

from services.agents.qa_agent import QAAgent
agent_registry.register(QAAgent())
