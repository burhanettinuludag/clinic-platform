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

from services.agents.news_agent import NewsAgent
agent_registry.register(NewsAgent())

from services.agents.editor_agent import EditorAgent
agent_registry.register(EditorAgent())

from services.agents.publishing_agent import PublishingAgent
agent_registry.register(PublishingAgent())

from services.agents.internal_link_agent import InternalLinkAgent
agent_registry.register(InternalLinkAgent())

from services.agents.quality_agent import QualityAgent
agent_registry.register(QualityAgent())

from services.agents.devops_agent import DevOpsAgent
agent_registry.register(DevOpsAgent())
