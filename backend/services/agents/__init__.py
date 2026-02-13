"""
Ajan otomatik kayit.

Bu dosya import edildiginde tum ajanlar registry'ye kaydedilir.
Yeni ajan eklemek icin:
1. agents/ klasorune yeni dosya ekle
2. Asagiya import + register satiri ekle
"""

from services.registry import agent_registry

# ── Ajanlari import et ve kaydet ──
from services.agents.content_agent import ContentAgent
agent_registry.register(ContentAgent())

from services.agents.seo_agent import SEOAgent
agent_registry.register(SEOAgent())

from services.agents.legal_agent import LegalAgent
agent_registry.register(LegalAgent())

# Yeni ajanlar buraya eklenecek:
# from services.agents.translation_agent import TranslationAgent
# agent_registry.register(TranslationAgent())
#
# from services.agents.qa_agent import QAAgent
# agent_registry.register(QAAgent())
