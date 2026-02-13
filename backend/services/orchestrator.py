"""
Orkestrator - Ajan zincirleme ve is akisi yonetimi.

Iki mod destekler:
1. Senkron zincir (run_chain): View'dan dogrudan cagrilir
2. Asenkron pipeline (run_pipeline_async): Celery task olarak calisir

Ozellikler:
- Pipeline-level AgentTask tracking (parent-subtask iliskisi)
- Gatekeeper mekanizmasi (is mantigi red -> pipeline durur)
- Partial data propagasyonu (basarisiz agent ciktisi sonrakine gecer)

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
    error_details: dict = field(default_factory=dict)  # {step_name: error_msg}


# ─── Onceden tanimli pipeline'lar ───
PIPELINES = {
    'publish_article': {
        'description': 'Icerik uret -> SEO optimize -> Hukuk kontrol -> Cevir',
        'steps': ['content_agent', 'seo_agent', 'legal_agent', 'translation_agent'],
        'stop_on_failure': True,
        'gatekeeper_steps': ['legal_agent'],
    },
    'answer_question': {
        'description': 'Hasta sorusuna RAG ile yanit ver',
        'steps': ['qa_agent'],
        'stop_on_failure': True,
        'gatekeeper_steps': [],
    },
    'seo_optimize': {
        'description': 'Mevcut icerik icin SEO optimizasyonu',
        'steps': ['seo_agent'],
        'stop_on_failure': False,
        'gatekeeper_steps': [],
    },
    'legal_audit': {
        'description': 'Hukuki uyumluluk denetimi (bilgi amacli)',
        'steps': ['legal_agent'],
        'stop_on_failure': False,
        'gatekeeper_steps': [],  # Bilgi amacli - red pipeline durdurmuyor
    },
    'content_with_translation': {
        'description': 'Icerik uret + EN cevirisi',
        'steps': ['content_agent', 'translation_agent'],
        'stop_on_failure': True,
        'gatekeeper_steps': [],
    },

    'full_content_v5': {
        'description': 'v5 tam icerik pipeline: uret -> SEO -> link -> QA -> editor',
        'steps': ['content_agent', 'seo_agent', 'internal_link_agent', 'quality_agent', 'editor_agent'],
        'stop_on_failure': True,
        'gatekeeper_steps': ['quality_agent'],
    },
    'news_pipeline': {
        'description': 'Haber icerigi pipeline',
        'steps': ['news_agent', 'seo_agent', 'internal_link_agent', 'quality_agent', 'editor_agent'],
        'stop_on_failure': True,
        'gatekeeper_steps': ['quality_agent'],
    },
    'doctor_article_review': {
        'description': 'Doktor yazisi degerlendirme pipeline',
        'steps': ['publishing_agent', 'seo_agent', 'internal_link_agent'],
        'stop_on_failure': False,
        'gatekeeper_steps': [],
    },
    'quality_check': {
        'description': 'Kalite kontrol: QA + Editor (bilgi amacli)',
        'steps': ['quality_agent', 'editor_agent'],
        'stop_on_failure': False,
        'gatekeeper_steps': [],  # Bilgi amacli - red pipeline durdurmuyor
    },
}


class Orchestrator:
    """
    Ajan orkestratoru.

    Pipeline'lari sirayla calistirir, her adimin ciktisini
    bir sonraki adimin girdisi olarak aktarir.

    Ozellikler:
    - AgentTask parent-subtask tracking
    - Gatekeeper mekanizmasi (pipeline seviyesinde is mantigi kontrolu)
    - Partial data propagasyonu (basarisiz step'in ciktisi da aktarilir)
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
        pipeline_def = PIPELINES.get(pipeline_name, {})
        gatekeeper_steps = pipeline_def.get('gatekeeper_steps', [])

        if steps is None:
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

        # Pipeline-level parent AgentTask olustur
        parent_task = self._create_pipeline_task(pipeline_name, input_data, triggered_by)

        completed = []
        failed = []
        skipped = []
        step_results = []
        error_details = {}
        current_data = dict(input_data)

        for step_name in steps:
            # Ajan var mi kontrol et
            if step_name not in agent_registry:
                logger.warning(f"Agent '{step_name}' not in registry, skipping")
                skipped.append(step_name)
                continue

            agent = agent_registry.get(step_name)
            is_gatekeeper = step_name in gatekeeper_steps

            # Calistir
            result = agent.run(
                current_data,
                triggered_by=triggered_by,
                parent_task=parent_task,
                is_gatekeeper=is_gatekeeper,
            )
            step_results.append(result)

            if result.success:
                completed.append(step_name)
                # Ciktiyi bir sonraki adimin girdisine merge et
                current_data.update(result.data)
                logger.info(f"  Step '{step_name}' basarili")
            else:
                failed.append(step_name)
                error_details[step_name] = result.error
                logger.warning(
                    f"  Step '{step_name}' basarisiz: {result.error}"
                )

                # Partial data'yi merge et (sonraki agent gorsun)
                if result.data:
                    current_data.update(result.data)

                # Hata metadata'si ekle
                current_data[f'__{step_name}_failed'] = True
                current_data[f'__{step_name}_error'] = result.error

                if stop_on_failure:
                    # Kalan adimlari skip olarak isaretle
                    remaining = steps[steps.index(step_name) + 1:]
                    skipped.extend(remaining)
                    break

        duration = int((timezone.now() - start).total_seconds() * 1000)
        success = len(failed) == 0

        # Parent task'i guncelle
        if parent_task:
            try:
                if success:
                    parent_task.mark_completed(
                        output_data={
                            'completed': completed,
                            'skipped': skipped,
                        },
                        duration=duration,
                    )
                else:
                    parent_task.mark_failed(
                        f"Basarisiz adimlar: {', '.join(failed)}"
                    )
                    parent_task.duration_ms = duration
                    parent_task.save(update_fields=['duration_ms'])
            except Exception as e:
                logger.error(f"Pipeline parent task guncellenemedi: {e}")

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
            error_details=error_details,
        )

    def _create_pipeline_task(self, pipeline_name, input_data, triggered_by):
        """Pipeline-level parent AgentTask olustur."""
        try:
            from apps.common.models import AgentTask
            return AgentTask.objects.create(
                agent_name='orchestrator',
                task_type='full_pipeline',
                input_data={
                    'pipeline': pipeline_name,
                    **{k: str(v)[:200] for k, v in input_data.items()},
                },
                status='running',
                created_by=triggered_by if triggered_by and hasattr(triggered_by, 'pk') else None,
            )
        except Exception as e:
            logger.error(f"Pipeline AgentTask olusturulamadi: {e}")
            return None

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
                'gatekeeper_steps': definition.get('gatekeeper_steps', []),
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
