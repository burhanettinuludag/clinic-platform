"""
Agent Registry - Ajan kayit defteri (plug-in sistemi).

Kullanim:
    from services.registry import agent_registry

    # Ajan cagirma:
    content = agent_registry.get('content_agent')
    result = content.run({'topic': 'Migren tetikleyicileri'})

    # Tum ajanlar:
    agent_registry.list_agents()  # ['content_agent', 'seo_agent', ...]

    # Ajan bilgisi:
    agent_registry.info()  # [{'name': ..., 'enabled': ..., 'flag': ...}]
"""

import logging
from typing import Dict, List, Optional

from services.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class AgentRegistry:
    """
    Merkezi ajan kayit defteri.

    Yeni ajan eklemek icin:
        agent_registry.register(MyAgent())

    Orkestrator bu registry uzerinden ajanlara erisir.
    """

    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        """Ajan kaydet."""
        if not agent.name:
            raise ValueError(f"Agent must have a name: {agent.__class__.__name__}")
        if agent.name in self._agents:
            logger.warning(f"Agent '{agent.name}' is being overridden")
        self._agents[agent.name] = agent
        logger.info(f"Agent registered: {agent.name}")

    def get(self, name: str) -> BaseAgent:
        """Ajan getir. Bulamazsa KeyError."""
        if name not in self._agents:
            raise KeyError(
                f"Agent '{name}' bulunamadi. "
                f"Kayitli ajanlar: {list(self._agents.keys())}"
            )
        return self._agents[name]

    def get_or_none(self, name: str) -> Optional[BaseAgent]:
        """Ajan getir veya None."""
        return self._agents.get(name)

    def list_agents(self) -> List[str]:
        """Kayitli ajan isimlerini dondur."""
        return list(self._agents.keys())

    def info(self) -> List[dict]:
        """Tum ajanlarin bilgisini dondur."""
        result = []
        for name, agent in self._agents.items():
            result.append({
                'name': name,
                'class': agent.__class__.__name__,
                'enabled': agent.is_enabled(),
                'feature_flag': agent.feature_flag_key,
                'description': agent.__class__.__doc__ or '',
            })
        return result

    def enabled_agents(self) -> List[str]:
        """Sadece aktif ajanlarin isimlerini dondur."""
        return [
            name for name, agent in self._agents.items()
            if agent.is_enabled()
        ]

    def __contains__(self, name: str) -> bool:
        return name in self._agents

    def __len__(self) -> int:
        return len(self._agents)


# Singleton instance
agent_registry = AgentRegistry()
