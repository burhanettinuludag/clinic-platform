"""
Orkestrator - Ajan zincirleme ve is akisi yonetimi.

Iki mod destekler:
1. Senkron zincir (run_chain): View'dan dogrudan cagrilir
2. Asenkron pipeline (run_pipeline_async): Celery task olarak calisir

Kullanim:
    from services.orchestrator import orchestrator

    # Senkron:
    result = orchestrator.run_chain(
        'publish_article',
        input_data={'topic': 'Migren'},
        steps=['content_agent', 'seo_agent', 'legal_agent']
    )

    # Asenkron:
    task = orchestrator.run_pipeline_async(
        'publish_article',
        input_data={'topic': 'Migren'},
        steps=['content_agent', 'seo_agent']
    )
"""

import logging
from dataclasses import dataclass, field
from typing import List, Optional

from django.utils import timezone

from services.registry import agent_registry
from services.base_agent import AgentResult

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Pipeline calistirma sonucu."""
    success: bool
    pipeline_name: str
    steps_completed: List[str] = field(default_factory=list)
    steps_failed: List[str] = field(default_factory=list)
    steps_skipped: List[str] = field(default_factory=list)
    final_data: dict = field(default_factory=dict)
    step_results: List[AgentResult] = field(default_factory=list)
    total_duration_ms: int = 0
    error: str = ''


# ─── Onceden tanimli pipeline'lar ───
PIPELINES = {
    'publish_article': {
        'description': 'Icerik uret -> SEO optimize -> Hukuk kontrol -> Cevir',
        'steps': ['content_agent', 'seo_agent', 'legal_agent', 'translation_agent'],
        'stop_on_failure': True,
    },
    'answer_question': {
        'description': 'Hasta sorusuna RAG ile yanit ver',
        'steps': ['qa_agent'],
        'stop_on_failure': True,
    },
    'seo_optimize': {
        'description': 'Mevcut icerik icin SEO optimizasyonu',
        'steps': ['seo_agent'],
        'stop_on_failure': False,
    },
    'legal_audit': {
        'description': 'Hukuki uyumluluk denetimi',
        'steps': ['legal_agent'],
        'stop_on_failure': False,
    },
    'content_with_translation': {
        'description': 'Icerik uret + EN cevirisi',
        'steps': ['content_agent', 'translation_agent'],
        'stop_on_failure': True,
    },
}


class Orchestrator:
    """
    Ajan orkestratoru.

    Pipeline'lari sirayla calistirir, her adimin ciktisini
    bir sonraki adimin girdisi olarak aktarir.
    """

    def run_chain(
        self,
        pipeline_name: str,
        input_data: dict,
        steps: Optional[List[str]] = None,
        triggered_by=None,
        stop_on_failure: bool = True,
    ) -> PipelineResult:
        """
        Senkron ajan zinciri calistir.

        Args:
            pipeline_name: Pipeline ismi (loglama icin)
            input_data: Baslangic verisi
            steps: Ajan isimleri listesi (None ise PIPELINES'dan alinir)
            triggered_by: Tetikleyen kullanici (AuditLog icin)
            stop_on_failure: Bir ajan basarisiz olursa dur mu?

        Returns:
            PipelineResult
        """
        start = timezone.now()

        # Pipeline tanimini al
        if steps is None:
            pipeline_def = PIPELINES.get(pipeline_name)
            if not pipeline_def:
                return PipelineResult(
                    success=False,
                    pipeline_name=pipeline_name,
                    error=f"Pipeline '{pipeline_name}' tanimlanmamis. "
                          f"Tanimli: {list(PIPELINES.keys())}",
                )
            steps = pipeline_def['steps']
            stop_on_failure = pipeline_def.get('stop_on_failure', True)

        logger.info(
            f"Pipeline '{pipeline_name}' basliyor: "
            f"steps={steps}, input_keys={list(input_data.keys())}"
        )

        completed = []
        failed = []
        skipped = []
        step_results = []
        current_data = dict(input_data)

        for step_name in steps:
            # Ajan var mi kontrol et
            if step_name not in agent_registry:
                logger.warning(f"Agent '{step_name}' not in registry, skipping")
                skipped.append(step_name)
                continue

            agent = agent_registry.get(step_name)

            # Calistir
            result = agent.run(current_data, triggered_by=triggered_by)
            step_results.append(result)

            if result.success:
                completed.append(step_name)
                # Ciktiyi bir sonraki adimin girdisine merge et
                current_data.update(result.data)
                logger.info(f"  Step '{step_name}' basarili")
            else:
                failed.append(step_name)
                logger.warning(
                    f"  Step '{step_name}' basarisiz: {result.error}"
                )
                if stop_on_failure:
                    # Kalan adimlari skip olarak isaretle
                    remaining = steps[steps.index(step_name) + 1:]
                    skipped.extend(remaining)
                    break

        duration = int((timezone.now() - start).total_seconds() * 1000)
        success = len(failed) == 0

        logger.info(
            f"Pipeline '{pipeline_name}' tamamlandi: "
            f"success={success}, completed={completed}, "
            f"failed={failed}, skipped={skipped}, "
            f"duration={duration}ms"
        )

        return PipelineResult(
            success=success,
            pipeline_name=pipeline_name,
            steps_completed=completed,
            steps_failed=failed,
            steps_skipped=skipped,
            final_data=current_data,
            step_results=step_results,
            total_duration_ms=duration,
            error=step_results[-1].error if failed and step_results else '',
        )

    def run_pipeline_async(
        self,
        pipeline_name: str,
        input_data: dict,
        steps: Optional[List[str]] = None,
        triggered_by_id=None,
    ):
        """
        Asenkron pipeline - Celery task olarak calistirir.

        Args:
            pipeline_name: Pipeline ismi
            input_data: Baslangic verisi
            steps: Ajan listesi (opsiyonel)
            triggered_by_id: Kullanici ID (UUID serializable)

        Returns:
            Celery AsyncResult
        """
        from services.tasks import run_pipeline_task
        return run_pipeline_task.delay(
            pipeline_name=pipeline_name,
            input_data=input_data,
            steps=steps,
            triggered_by_id=str(triggered_by_id) if triggered_by_id else None,
        )

    def list_pipelines(self) -> dict:
        """Tanimli pipeline'lari listele."""
        result = {}
        for name, definition in PIPELINES.items():
            result[name] = {
                'description': definition['description'],
                'steps': definition['steps'],
                'available_steps': [
                    s for s in definition['steps']
                    if s in agent_registry
                ],
                'missing_steps': [
                    s for s in definition['steps']
                    if s not in agent_registry
                ],
            }
        return result


# Singleton instance
orchestrator = Orchestrator()
