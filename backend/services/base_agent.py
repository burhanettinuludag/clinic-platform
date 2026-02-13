"""
Base Agent - Tum ajanlarin miras aldigi soyut temel sinif.

Her ajan su ozelliklere sahiptir:
- name: Benzersiz ajan ismi
- system_prompt: LLM rolu
- feature_flag_key: Admin'den acip kapatma
- task_type: AgentTask kaydi icin gorev tipi
- execute(): Ana calistirma metodu
- validate_output(): Teknik cikti dogrulama
- check_gatekeeper_decision(): Is mantigi red karari (pipeline kontrolu)
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

from django.utils import timezone

from services.llm_client import llm_client, LLMResponse, LLMError

logger = logging.getLogger(__name__)


class _NullTask:
    """
    AgentTask olusturulamadigi durumda no-op stub.
    DB erisim hatasi olsa bile pipeline kirilmasini onler.
    """
    id = None

    def mark_running(self):
        pass

    def mark_completed(self, **kwargs):
        pass

    def mark_failed(self, error_message=''):
        pass

    def save(self, **kwargs):
        pass


@dataclass
class AgentResult:
    """Ajan calistirma sonucu."""
    success: bool
    data: dict = field(default_factory=dict)
    error: str = ''
    agent_name: str = ''
    provider: str = ''
    tokens_used: int = 0
    duration_ms: int = 0
    task_id: Optional[str] = None  # AgentTask.id (UUID string)


class BaseAgent(ABC):
    """
    Soyut temel ajan sinifi.

    Yeni ajan olusturmak icin:
        1. Bu sinifi miras al
        2. name, system_prompt, feature_flag_key, task_type tanimla
        3. execute() metodunu override et
        4. Gatekeeper ajan ise check_gatekeeper_decision() override et
        5. registry'ye kaydet
    """

    name: str = ''
    system_prompt: str = ''
    feature_flag_key: str = ''
    task_type: str = 'generate_content'  # AgentTask.TASK_TYPES'dan biri
    temperature: float = 0.7
    max_tokens: int = 2000

    # Son LLM cagrisi bilgileri (AgentTask icin)
    _last_provider: str = ''
    _last_model: str = ''
    _last_tokens: int = 0

    def is_enabled(self) -> bool:
        """FeatureFlag kontrolu. Flag yoksa veya aktifse True."""
        if not self.feature_flag_key:
            return True
        try:
            from apps.common.models import FeatureFlag
            flag = FeatureFlag.objects.filter(key=self.feature_flag_key).first()
            if flag is None:
                return False  # Flag tanimlanmamissa kapali kabul et
            return flag.is_enabled
        except Exception:
            return False

    def llm_call(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """
        LLM'e istek at. Fallback ve retry otomatik.

        Args:
            message: Kullanici mesaji / prompt
            system_prompt: Override system prompt (None ise sinif default)
            temperature: Override temperature
            max_tokens: Override max tokens

        Returns:
            LLMResponse objesi
        """
        response = llm_client.chat(
            user_message=message,
            system_prompt=system_prompt or self.system_prompt,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens or self.max_tokens,
        )
        # Son LLM cagrisi bilgisini sakla (AgentTask icin)
        self._last_provider = response.provider
        self._last_model = response.model
        self._last_tokens = response.tokens_used
        return response

    def run(
        self,
        input_data: dict,
        triggered_by=None,
        parent_task=None,
        is_gatekeeper: bool = False,
    ) -> AgentResult:
        """
        Ajan calistirma wrapper. FeatureFlag, AgentTask lifecycle,
        gatekeeper kontrolu, loglama ve hata yonetimi.

        Bu metodu OVERRIDE ETME - execute() metodunu override et.

        Args:
            input_data: Girdi verisi
            triggered_by: Tetikleyen kullanici (AuditLog + AgentTask icin)
            parent_task: Ust pipeline AgentTask (subtask iliskisi icin)
            is_gatekeeper: Bu ajan pipeline'da gatekeeper mi?
        """
        # 1. Feature flag kontrolu
        if not self.is_enabled():
            logger.info(f"Agent {self.name} is disabled via FeatureFlag")
            task = self._create_task(input_data, triggered_by, parent_task)
            task.status = 'skipped'
            task.error_message = f"Agent '{self.name}' devre disi (FeatureFlag)"
            task.save(update_fields=['status', 'error_message'])
            return AgentResult(
                success=False,
                error=f"Agent '{self.name}' devre disi (FeatureFlag)",
                agent_name=self.name,
                task_id=str(task.id) if task.id else None,
            )

        # 2. AgentTask olustur ve running isaretle
        task = self._create_task(input_data, triggered_by, parent_task)
        task.mark_running()

        # 3. Calistir
        start = timezone.now()
        try:
            result = self.execute(input_data)

            # 4. Teknik dogrulama
            validation_error = self.validate_output(result)
            if validation_error:
                duration = int((timezone.now() - start).total_seconds() * 1000)
                logger.warning(
                    f"Agent {self.name} output validation failed: {validation_error}"
                )
                task.mark_failed(f"Cikti dogrulama hatasi: {validation_error}")
                task.duration_ms = duration
                task.output_data = result if isinstance(result, dict) else {}
                task.save(update_fields=['duration_ms', 'output_data'])
                self._log_execution(
                    input_data, result, triggered_by, duration,
                    success=False, error=validation_error
                )
                return AgentResult(
                    success=False,
                    error=f"Cikti dogrulama hatasi: {validation_error}",
                    agent_name=self.name,
                    data=result,
                    duration_ms=duration,
                    task_id=str(task.id) if task.id else None,
                )

            # 5. Gatekeeper is mantigi kontrolu
            if is_gatekeeper:
                gatekeeper_error = self.check_gatekeeper_decision(result)
                if gatekeeper_error:
                    duration = int((timezone.now() - start).total_seconds() * 1000)
                    logger.warning(
                        f"Agent {self.name} gatekeeper red: {gatekeeper_error}"
                    )
                    task.mark_failed(f"Gatekeeper red: {gatekeeper_error}")
                    task.duration_ms = duration
                    task.output_data = result if isinstance(result, dict) else {}
                    task.tokens_used = self._last_tokens
                    task.llm_provider = self._last_provider
                    task.llm_model = self._last_model
                    task.save(update_fields=[
                        'duration_ms', 'output_data', 'tokens_used',
                        'llm_provider', 'llm_model',
                    ])
                    self._log_execution(
                        input_data, result, triggered_by, duration,
                        success=False, error=gatekeeper_error
                    )
                    return AgentResult(
                        success=False,
                        data=result,  # Partial data'yi yine dondur
                        error=f"Gatekeeper red: {gatekeeper_error}",
                        agent_name=self.name,
                        provider=self._last_provider,
                        tokens_used=self._last_tokens,
                        duration_ms=duration,
                        task_id=str(task.id) if task.id else None,
                    )

            # 6. Basarili - logla ve AgentTask guncelle
            duration = int((timezone.now() - start).total_seconds() * 1000)
            task.mark_completed(
                output_data=result if isinstance(result, dict) else {},
                tokens=self._last_tokens,
                duration=duration,
                provider=self._last_provider,
                model_name=self._last_model,
            )
            self._log_execution(
                input_data, result, triggered_by, duration, success=True
            )

            return AgentResult(
                success=True,
                data=result,
                agent_name=self.name,
                provider=self._last_provider,
                tokens_used=self._last_tokens,
                duration_ms=duration,
                task_id=str(task.id) if task.id else None,
            )

        except LLMError as e:
            duration = int((timezone.now() - start).total_seconds() * 1000)
            task.mark_failed(str(e))
            task.duration_ms = duration
            task.save(update_fields=['duration_ms'])
            self._log_execution(
                input_data, {}, triggered_by, duration,
                success=False, error=str(e)
            )
            return AgentResult(
                success=False,
                error=str(e),
                agent_name=self.name,
                duration_ms=duration,
                task_id=str(task.id) if task.id else None,
            )

        except Exception as e:
            logger.exception(f"Agent {self.name} unexpected error")
            task.mark_failed(f"Beklenmeyen hata: {str(e)}")
            return AgentResult(
                success=False,
                error=f"Beklenmeyen hata: {str(e)}",
                agent_name=self.name,
                task_id=str(task.id) if task.id else None,
            )

    @abstractmethod
    def execute(self, input_data: dict) -> dict:
        """
        Ana calistirma metodu. Her ajan OVERRIDE eder.

        Args:
            input_data: Girdi verisi (onceki ajandan veya kullanicidan)

        Returns:
            dict: Sonuc verisi (bir sonraki ajana veya kullaniciya)
        """
        pass

    def validate_output(self, output: dict) -> Optional[str]:
        """
        Teknik cikti dogrulama. Override ederek ozel dogrulama eklenebilir.
        Ornek: parse hatasi, zorunlu alan eksikligi.

        Returns:
            None: Gecerli
            str: Hata mesaji
        """
        return None

    def check_gatekeeper_decision(self, output: dict) -> Optional[str]:
        """
        Gatekeeper is mantigi kontrolu.

        Pipeline tanimi bu ajani gatekeeper olarak isaretlediyse,
        run() metodu bu metodu cagirarak is mantigi red karari kontrol eder.

        Ornek: LegalAgent legal_approved=False dondurur -> pipeline durur
        Ornek: QualityAgent decision=reject dondurur -> pipeline durur

        Override edilmeli.

        Returns:
            None: Onaylandi, pipeline devam eder
            str: Red mesaji, pipeline durur (stop_on_failure ise)
        """
        return None

    def _create_task(self, input_data, triggered_by, parent_task):
        """AgentTask olustur. DB hatasi olursa _NullTask dondur."""
        try:
            from apps.common.models import AgentTask
            return AgentTask.objects.create(
                agent_name=self.name,
                task_type=self.task_type,
                input_data={k: str(v)[:200] for k, v in input_data.items()},
                status='pending',
                created_by=triggered_by if triggered_by and hasattr(triggered_by, 'pk') else None,
                parent_task=parent_task,
            )
        except Exception as e:
            logger.error(f"AgentTask olusturulamadi: {e}")
            return _NullTask()

    def _log_execution(
        self, input_data, output, triggered_by, duration_ms,
        success=True, error=''
    ):
        """AuditLog'a kayit."""
        try:
            from apps.common.models import AuditLog
            AuditLog.objects.create(
                user=triggered_by,
                action='agent_execution',
                resource_type=self.name,
                details={
                    'input_summary': str(input_data)[:500],
                    'output_summary': str(output)[:500],
                    'success': success,
                    'error': error,
                    'duration_ms': duration_ms,
                },
            )
        except Exception as e:
            logger.error(f"Failed to log agent execution: {e}")
