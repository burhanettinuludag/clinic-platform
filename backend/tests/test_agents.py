"""
Agent unit tests – ContentAgent, LegalAgent, Orchestrator, BaseAgent.

Tum LLM cagirilari, DB islemleri ve FeatureFlag'ler mock'lanir.
Gercek API cagrisi veya DB erisimi YAPILMAZ.
"""

import json
import pytest
from dataclasses import dataclass, field
from typing import Optional
from unittest.mock import patch, MagicMock, PropertyMock

from services.llm_client import LLMResponse
from services.base_agent import BaseAgent, AgentResult, _NullTask
from services.agents.content_agent import ContentAgent
from services.agents.legal_agent import LegalAgent
from services.orchestrator import Orchestrator, PipelineResult, PIPELINES


# ── helpers ──────────────────────────────────────────────────────────


def make_llm_response(content, provider='groq', model='llama3', tokens=100, duration=250):
    """LLMResponse factory."""
    return LLMResponse(
        content=content,
        provider=provider,
        model=model,
        tokens_used=tokens,
        duration_ms=duration,
        raw={},
    )


class _MockAgent(BaseAgent):
    """Orchestrator testlerinde kullanilacak sahte ajan."""

    def __init__(self, name, output=None, should_fail=False):
        self.name = name
        self._output = output or {}
        self._should_fail = should_fail
        self.feature_flag_key = ''

    def execute(self, input_data: dict) -> dict:
        if self._should_fail:
            raise RuntimeError(f'{self.name} failed intentionally')
        return {**input_data, **self._output}


def _null_create_task(self, input_data, triggered_by, parent_task):
    return _NullTask()


def _noop_log(self, *args, **kwargs):
    pass


def _enabled(self):
    return True


def _disabled(self):
    return False


# ── ContentAgent ─────────────────────────────────────────────────────


class TestContentAgent:
    """ContentAgent unit testleri."""

    def setup_method(self):
        self.agent = ContentAgent()

    # 1 — name & config
    def test_agent_name_and_config(self):
        assert self.agent.name == 'content_agent'
        assert self.agent.task_type == 'generate_content'
        assert self.agent.feature_flag_key == 'agent_content'
        assert self.agent.temperature == 0.7
        assert self.agent.max_tokens == 3000

    # 2 — duz JSON parse
    def test_parse_clean_json(self):
        payload = {
            'title_tr': 'Migren Nedir?',
            'body_tr': 'Migren bir bas agrisi turudur.',
            'excerpt_tr': 'Kisa ozet',
            'seo_title_tr': 'Migren',
            'seo_description_tr': 'Migren hakkinda bilgi',
            'suggested_category': 'migren',
        }
        result = self.agent._parse_response(json.dumps(payload))
        assert result['title_tr'] == 'Migren Nedir?'
        assert result['body_tr'] == 'Migren bir bas agrisi turudur.'
        assert result['suggested_category'] == 'migren'

    # 3 — backtick sarili JSON parse
    def test_parse_backtick_wrapped_json(self):
        payload = {
            'title_tr': 'Epilepsi',
            'body_tr': 'Epilepsi hakkinda yazi.',
            'excerpt_tr': 'Ozet',
            'seo_title_tr': 'Epilepsi',
            'seo_description_tr': 'Epilepsi meta',
            'suggested_category': 'epilepsi',
        }
        raw = f'```json\n{json.dumps(payload)}\n```'
        result = self.agent._parse_response(raw)
        assert result['title_tr'] == 'Epilepsi'
        assert result['body_tr'] == 'Epilepsi hakkinda yazi.'

    # 4 — parse edilemeyen yanit → body_tr fallback
    def test_parse_unparseable_falls_back_to_body_tr(self):
        garbage = 'Bu bir JSON degil, duz metin.'
        result = self.agent._parse_response(garbage)
        assert result['body_tr'] == garbage
        assert result['parse_error'] is True
        assert result['title_tr'] == ''

    # 5 — bos topic → error key
    @patch.object(ContentAgent, 'llm_call')
    def test_empty_topic_returns_error(self, mock_llm):
        result = self.agent.execute({'topic': '', 'module': 'migraine'})
        assert 'error' in result
        mock_llm.assert_not_called()

    # 6 — validate_output: bos body_tr → hata
    def test_validate_output_empty_body_returns_error(self):
        output = {'title_tr': 'Baslik', 'body_tr': ''}
        err = self.agent.validate_output(output)
        assert err is not None
        assert 'body_tr' in err

    # 7 — validate_output: dolu body_tr → None
    def test_validate_output_valid_body_returns_none(self):
        output = {'title_tr': 'Baslik', 'body_tr': 'Icerik var'}
        assert self.agent.validate_output(output) is None

    # 8 — validate_output: parse_error + bos body → None (fallback kabul)
    def test_validate_output_parse_error_with_body(self):
        output = {'body_tr': '', 'parse_error': True}
        # parse_error varsa body_tr bos olsa bile validate gecmeli
        assert self.agent.validate_output(output) is None

    # 9 — tam run() akisi
    @patch.object(BaseAgent, '_log_execution', _noop_log)
    @patch.object(BaseAgent, '_create_task', _null_create_task)
    @patch.object(BaseAgent, 'is_enabled', _enabled)
    @patch.object(ContentAgent, 'llm_call')
    def test_full_run_success(self, mock_llm):
        payload = json.dumps({
            'title_tr': 'Test Baslik',
            'body_tr': 'Test icerik',
            'excerpt_tr': 'Ozet',
            'seo_title_tr': 'SEO',
            'seo_description_tr': 'Meta',
            'suggested_category': 'genel-saglik',
        })
        mock_llm.return_value = make_llm_response(payload)

        result = self.agent.run({'topic': 'Test', 'module': 'general'})

        assert result.success is True
        assert result.data['title_tr'] == 'Test Baslik'
        assert result.data['body_tr'] == 'Test icerik'
        assert result.agent_name == 'content_agent'

    # 10 — disabled agent → success=False
    @patch.object(BaseAgent, '_log_execution', _noop_log)
    @patch.object(BaseAgent, '_create_task', _null_create_task)
    @patch.object(BaseAgent, 'is_enabled', _disabled)
    def test_disabled_agent_returns_failure(self):
        result = self.agent.run({'topic': 'Test'})
        assert result.success is False
        assert 'devre disi' in result.error


# ── LegalAgent ───────────────────────────────────────────────────────


class TestLegalAgent:
    """LegalAgent unit testleri."""

    def setup_method(self):
        self.agent = LegalAgent()

    # 1 — onaylanan icerik
    def test_approved_content(self):
        payload = json.dumps({
            'legal_approved': True,
            'legal_score': 95,
            'legal_issues': [],
            'legal_warnings': [],
            'legal_suggestions': [],
            'disclaimer_present': True,
            'medical_advice_detected': False,
        })
        result = self.agent._parse_response(payload)
        assert result['legal_approved'] is True
        assert result['disclaimer_present'] is True

    # 2 — reddedilen icerik
    def test_rejected_content(self):
        payload = json.dumps({
            'legal_approved': False,
            'legal_score': 30,
            'legal_issues': ['Tibbi oneri tespit edildi'],
            'medical_advice_detected': True,
        })
        result = self.agent._parse_response(payload)
        assert result['legal_approved'] is False
        assert result['medical_advice_detected'] is True

    # 3 — bos body → legal_approved=False
    @patch.object(LegalAgent, 'llm_call')
    def test_empty_body_returns_not_approved(self, mock_llm):
        result = self.agent.execute({'title_tr': 'Baslik', 'body_tr': ''})
        assert result['legal_approved'] is False
        assert 'Icerik bos' in result['legal_issues']
        mock_llm.assert_not_called()

    # 4 — parse hatasi → legal_parse_error=True
    def test_parse_error_returns_flag(self):
        result = self.agent._parse_response('tamamen bozuk veri {{{{')
        assert result['legal_parse_error'] is True
        assert result['legal_approved'] is False

    # 5 — check_gatekeeper_decision: approved → None
    def test_gatekeeper_approved_returns_none(self):
        output = {'legal_approved': True, 'legal_score': 90}
        assert self.agent.check_gatekeeper_decision(output) is None

    # 6 — check_gatekeeper_decision: rejected → hata mesaji
    def test_gatekeeper_rejected_returns_error(self):
        output = {
            'legal_approved': False,
            'legal_score': 25,
            'legal_issues': ['Ilac dozaji belirtilmis', 'Disclaimer yok'],
        }
        err = self.agent.check_gatekeeper_decision(output)
        assert err is not None
        assert 'skor: 25' in err
        assert 'Ilac dozaji' in err

    # 7 — input data passthrough (merge)
    @patch.object(BaseAgent, '_log_execution', _noop_log)
    @patch.object(BaseAgent, '_create_task', _null_create_task)
    @patch.object(BaseAgent, 'is_enabled', _enabled)
    @patch.object(LegalAgent, 'llm_call')
    def test_input_data_passthrough(self, mock_llm):
        legal_response = json.dumps({
            'legal_approved': True,
            'legal_score': 92,
            'legal_issues': [],
            'disclaimer_present': True,
            'medical_advice_detected': False,
        })
        mock_llm.return_value = make_llm_response(legal_response)

        input_data = {
            'title_tr': 'Onceki Baslik',
            'body_tr': 'Onceki icerik metni',
            'content_type': 'blog',
            'seo_title_tr': 'SEO baslik',
        }
        result = self.agent.run(input_data)

        assert result.success is True
        # Onceki ajanin verileri korunmali
        assert result.data['title_tr'] == 'Onceki Baslik'
        assert result.data['seo_title_tr'] == 'SEO baslik'
        # Legal verileri eklenmeli
        assert result.data['legal_approved'] is True
        assert result.data['legal_score'] == 92

    # 8 — legal_approved olmadan score-based inference
    def test_infer_approval_from_score(self):
        payload = json.dumps({
            'legal_score': 85,
            'legal_issues': [],
        })
        result = self.agent._parse_response(payload)
        assert result['legal_approved'] is True  # 85 >= 70

    def test_infer_rejection_from_low_score(self):
        payload = json.dumps({
            'legal_score': 40,
            'legal_issues': ['Ciddi sorun'],
        })
        result = self.agent._parse_response(payload)
        assert result['legal_approved'] is False  # 40 < 70


# ── Orchestrator ─────────────────────────────────────────────────────


class TestOrchestrator:
    """Orchestrator unit testleri."""

    def setup_method(self):
        self.orchestrator = Orchestrator()

    @staticmethod
    def _setup_registry(mock_reg, agents):
        """Mock agent_registry'yi agents dict ile yapilandir."""
        mock_reg.__contains__ = MagicMock(side_effect=lambda name: name in agents)
        mock_reg.get = MagicMock(side_effect=lambda name: agents[name])

    # 1 — 2 adimli basarili pipeline
    @patch('services.orchestrator.agent_registry')
    @patch.object(Orchestrator, '_create_pipeline_task', return_value=None)
    def test_two_step_success_pipeline(self, mock_task, mock_reg):
        agent_a = _MockAgent('agent_a', output={'key_a': 'val_a'})
        agent_b = _MockAgent('agent_b', output={'key_b': 'val_b'})

        agents = {'agent_a': agent_a, 'agent_b': agent_b}
        self._setup_registry(mock_reg, agents)

        # is_enabled ve task mock'lari
        with patch.object(BaseAgent, 'is_enabled', _enabled), \
             patch.object(BaseAgent, '_create_task', _null_create_task), \
             patch.object(BaseAgent, '_log_execution', _noop_log):

            result = self.orchestrator.run_chain(
                'test_pipeline',
                input_data={'topic': 'test'},
                steps=['agent_a', 'agent_b'],
            )

        assert result.success is True
        assert result.steps_completed == ['agent_a', 'agent_b']
        assert result.steps_failed == []
        assert result.final_data['key_a'] == 'val_a'
        assert result.final_data['key_b'] == 'val_b'

    # 2 — stop_on_failure=True: fail → kalan skipped
    @patch('services.orchestrator.agent_registry')
    @patch.object(Orchestrator, '_create_pipeline_task', return_value=None)
    def test_stop_on_failure_skips_remaining(self, mock_task, mock_reg):
        agent_a = _MockAgent('agent_a', should_fail=True)
        agent_b = _MockAgent('agent_b', output={'key_b': 'val_b'})

        agents = {'agent_a': agent_a, 'agent_b': agent_b}
        self._setup_registry(mock_reg, agents)

        with patch.object(BaseAgent, 'is_enabled', _enabled), \
             patch.object(BaseAgent, '_create_task', _null_create_task), \
             patch.object(BaseAgent, '_log_execution', _noop_log):

            result = self.orchestrator.run_chain(
                'test_pipeline',
                input_data={'topic': 'test'},
                steps=['agent_a', 'agent_b'],
                stop_on_failure=True,
            )

        assert result.success is False
        assert 'agent_a' in result.steps_failed
        assert 'agent_b' in result.steps_skipped

    # 3 — stop_on_failure=False: fail olsa bile devam
    @patch('services.orchestrator.agent_registry')
    @patch.object(Orchestrator, '_create_pipeline_task', return_value=None)
    def test_continue_on_failure(self, mock_task, mock_reg):
        agent_a = _MockAgent('agent_a', should_fail=True)
        agent_b = _MockAgent('agent_b', output={'key_b': 'val_b'})

        agents = {'agent_a': agent_a, 'agent_b': agent_b}
        self._setup_registry(mock_reg, agents)

        with patch.object(BaseAgent, 'is_enabled', _enabled), \
             patch.object(BaseAgent, '_create_task', _null_create_task), \
             patch.object(BaseAgent, '_log_execution', _noop_log):

            result = self.orchestrator.run_chain(
                'test_pipeline',
                input_data={'topic': 'test'},
                steps=['agent_a', 'agent_b'],
                stop_on_failure=False,
            )

        assert result.success is False  # bir step fail oldu
        assert 'agent_a' in result.steps_failed
        assert 'agent_b' in result.steps_completed
        assert result.final_data['key_b'] == 'val_b'

    # 4 — registry'de olmayan agent → skipped
    @patch('services.orchestrator.agent_registry')
    @patch.object(Orchestrator, '_create_pipeline_task', return_value=None)
    def test_missing_agent_skipped(self, mock_task, mock_reg):
        agent_a = _MockAgent('agent_a', output={'key_a': 'val_a'})

        agents = {'agent_a': agent_a}
        self._setup_registry(mock_reg, agents)

        with patch.object(BaseAgent, 'is_enabled', _enabled), \
             patch.object(BaseAgent, '_create_task', _null_create_task), \
             patch.object(BaseAgent, '_log_execution', _noop_log):

            result = self.orchestrator.run_chain(
                'test_pipeline',
                input_data={'topic': 'test'},
                steps=['agent_a', 'nonexistent_agent'],
            )

        assert 'nonexistent_agent' in result.steps_skipped
        assert 'agent_a' in result.steps_completed

    # 5 — tanimsiz pipeline → error
    def test_undefined_pipeline_returns_error(self):
        result = self.orchestrator.run_chain(
            'totally_fake_pipeline',
            input_data={'topic': 'test'},
        )
        assert result.success is False
        assert 'tanimlanmamis' in result.error

    # 6 — data propagation: her adimin ciktisi sonrakine aktarilir
    @patch('services.orchestrator.agent_registry')
    @patch.object(Orchestrator, '_create_pipeline_task', return_value=None)
    def test_data_propagation_between_steps(self, mock_task, mock_reg):
        agent_a = _MockAgent('agent_a', output={'from_a': 'hello'})
        agent_b = _MockAgent('agent_b', output={'from_b': 'world'})

        agents = {'agent_a': agent_a, 'agent_b': agent_b}
        self._setup_registry(mock_reg, agents)

        with patch.object(BaseAgent, 'is_enabled', _enabled), \
             patch.object(BaseAgent, '_create_task', _null_create_task), \
             patch.object(BaseAgent, '_log_execution', _noop_log):

            result = self.orchestrator.run_chain(
                'test_pipeline',
                input_data={'initial': 'data'},
                steps=['agent_a', 'agent_b'],
            )

        # agent_b'nin girdisinde agent_a'nin ciktisi olmali
        assert result.final_data['initial'] == 'data'
        assert result.final_data['from_a'] == 'hello'
        assert result.final_data['from_b'] == 'world'

    # 7 — failure metadata eklenir
    @patch('services.orchestrator.agent_registry')
    @patch.object(Orchestrator, '_create_pipeline_task', return_value=None)
    def test_failure_metadata_added_to_data(self, mock_task, mock_reg):
        agent_a = _MockAgent('agent_a', should_fail=True)
        agent_b = _MockAgent('agent_b', output={'key_b': 'val_b'})

        agents = {'agent_a': agent_a, 'agent_b': agent_b}
        self._setup_registry(mock_reg, agents)

        with patch.object(BaseAgent, 'is_enabled', _enabled), \
             patch.object(BaseAgent, '_create_task', _null_create_task), \
             patch.object(BaseAgent, '_log_execution', _noop_log):

            result = self.orchestrator.run_chain(
                'test_pipeline',
                input_data={'topic': 'test'},
                steps=['agent_a', 'agent_b'],
                stop_on_failure=False,
            )

        assert result.final_data['__agent_a_failed'] is True
        assert '__agent_a_error' in result.final_data


# ── BaseAgent Mechanics ──────────────────────────────────────────────


class TestBaseAgentMechanics:
    """BaseAgent yardimci sinif ve davranis testleri."""

    # 1 — _NullTask tum metodlari no-op
    def test_null_task_is_noop(self):
        task = _NullTask()
        assert task.id is None
        # Hicbir cagri hata vermemeli
        task.mark_running()
        task.mark_completed(output_data={}, tokens=10, duration=100)
        task.mark_failed(error_message='test error')
        task.save(update_fields=['status'])

    # 2 — AgentResult default degerleri
    def test_agent_result_defaults(self):
        result = AgentResult(success=True)
        assert result.data == {}
        assert result.error == ''
        assert result.agent_name == ''
        assert result.provider == ''
        assert result.tokens_used == 0
        assert result.duration_ms == 0
        assert result.task_id is None

    # 3 — PIPELINES tanimlarinin hepsinde steps ve description olmali
    def test_all_pipelines_have_required_keys(self):
        for name, defn in PIPELINES.items():
            assert 'steps' in defn, f"Pipeline '{name}' missing 'steps'"
            assert 'description' in defn, f"Pipeline '{name}' missing 'description'"
            assert isinstance(defn['steps'], list), f"Pipeline '{name}' steps not a list"
            assert len(defn['steps']) > 0, f"Pipeline '{name}' has empty steps"
            assert isinstance(defn['description'], str), f"Pipeline '{name}' description not str"
