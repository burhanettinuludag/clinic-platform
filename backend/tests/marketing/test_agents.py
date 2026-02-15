"""
Unit tests for Marketing Agents.
Tests agent registration, initialization, and validation logic.
"""

import pytest

# Import agents module to trigger registration
import services.agents  # noqa: F401

from services.registry import agent_registry


@pytest.mark.django_db
class TestMarketingAgentRegistration:
    """Tests for marketing agent registration in the registry."""

    def test_marketing_content_agent_registered(self):
        assert 'marketing_content_agent' in agent_registry

    def test_visual_brief_agent_registered(self):
        assert 'visual_brief_agent' in agent_registry

    def test_scheduling_agent_registered(self):
        assert 'scheduling_agent' in agent_registry

    def test_marketing_content_agent_properties(self):
        agent = agent_registry.get('marketing_content_agent')
        assert agent.name == 'marketing_content_agent'
        assert agent.task_type == 'marketing_content'
        assert agent.feature_flag_key == 'agent_marketing_content'

    def test_visual_brief_agent_properties(self):
        agent = agent_registry.get('visual_brief_agent')
        assert agent.name == 'visual_brief_agent'
        assert agent.task_type == 'visual_brief'
        assert agent.feature_flag_key == 'agent_visual_brief'

    def test_scheduling_agent_properties(self):
        agent = agent_registry.get('scheduling_agent')
        assert agent.name == 'scheduling_agent'
        assert agent.task_type == 'schedule_plan'
        assert agent.feature_flag_key == 'agent_scheduling'


class TestMarketingContentAgentValidation:
    """Tests for MarketingContentAgent output validation."""

    def test_valid_output(self):
        agent = agent_registry.get('marketing_content_agent')
        data = {
            'instagram_posts': [{'content': 'Test', 'hashtags': ['#test']}],
            'linkedin_posts': [{'content': 'Test'}],
            'twitter_posts': [{'content': 'Test'}],
        }
        result = agent.validate_output(data)
        assert result is None  # None = valid

    def test_missing_posts_key(self):
        agent = agent_registry.get('marketing_content_agent')
        data = {'some_other_key': 'value'}
        result = agent.validate_output(data)
        assert result is not None  # str = error message

    def test_empty_data(self):
        agent = agent_registry.get('marketing_content_agent')
        result = agent.validate_output({})
        assert result is not None


class TestVisualBriefAgentValidation:
    """Tests for VisualBriefAgent output validation."""

    def test_valid_output(self):
        agent = agent_registry.get('visual_brief_agent')
        data = {
            'briefs': [{'layout': 'single', 'colors': ['#1B4F72']}],
        }
        result = agent.validate_output(data)
        assert result is None

    def test_empty_briefs(self):
        agent = agent_registry.get('visual_brief_agent')
        data = {'briefs': []}
        result = agent.validate_output(data)
        assert result is not None

    def test_missing_briefs_key(self):
        agent = agent_registry.get('visual_brief_agent')
        data = {'other': 'value'}
        result = agent.validate_output(data)
        assert result is not None


class TestSchedulingAgentValidation:
    """Tests for SchedulingAgent output validation."""

    def test_valid_output(self):
        agent = agent_registry.get('scheduling_agent')
        data = {
            'schedule': [{'day': 'Monday', 'time': '09:00', 'platform': 'instagram'}],
        }
        result = agent.validate_output(data)
        assert result is None

    def test_empty_schedule(self):
        agent = agent_registry.get('scheduling_agent')
        data = {'schedule': []}
        result = agent.validate_output(data)
        assert result is not None

    def test_missing_schedule_key(self):
        agent = agent_registry.get('scheduling_agent')
        data = {'other': 'value'}
        result = agent.validate_output(data)
        assert result is not None
