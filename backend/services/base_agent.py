"""
Base Agent - Tum ajanlarin miras aldigi soyut temel sinif.

Her ajan su ozelliklere sahiptir:
- name: Benzersiz ajan ismi
- system_prompt: LLM rolu
- feature_flag_key: Admin'den acip kapatma
- execute(): Ana calistirma metodu
- validate_output(): Cikti dogrulama
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

from django.utils import timezone

from services.llm_client import llm_client, LLMResponse, LLMError

logger = logging.getLogger(__name__)


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


class BaseAgent(ABC):
    """
    Soyut temel ajan sinifi.

    Yeni ajan olusturmak icin:
        1. Bu sinifi miras al
        2. name, system_prompt, feature_flag_key tanimla
        3. execute() metodunu override et
        4. registry'ye kaydet
    """

    name: str = ''
    system_prompt: str = ''
    feature_flag_key: str = ''
    temperature: float = 0.7
    max_tokens: int = 2000

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
        return llm_client.chat(
            user_message=message,
            system_prompt=system_prompt or self.system_prompt,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens or self.max_tokens,
        )

    def run(self, input_data: dict, triggered_by=None) -> AgentResult:
        """
        Ajan calistirma wrapper. FeatureFlag, loglama ve hata yonetimi.

        Bu metodu OVERRIDE ETME - execute() metodunu override et.
        """
        # 1. Feature flag kontrolu
        if not self.is_enabled():
            logger.info(f"Agent {self.name} is disabled via FeatureFlag")
            return AgentResult(
                success=False,
                error=f"Agent '{self.name}' devre disi (FeatureFlag)",
                agent_name=self.name,
            )

        # 2. Calistir
        start = timezone.now()
        try:
            result = self.execute(input_data)

            # 3. Dogrula
            validation_error = self.validate_output(result)
            if validation_error:
                logger.warning(
                    f"Agent {self.name} output validation failed: {validation_error}"
                )
                return AgentResult(
                    success=False,
                    error=f"Cikti dogrulama hatasi: {validation_error}",
                    agent_name=self.name,
                    data=result,
                )

            # 4. Logla
            duration = int((timezone.now() - start).total_seconds() * 1000)
            self._log_execution(
                input_data, result, triggered_by, duration, success=True
            )

            return AgentResult(
                success=True,
                data=result,
                agent_name=self.name,
                duration_ms=duration,
            )

        except LLMError as e:
            duration = int((timezone.now() - start).total_seconds() * 1000)
            self._log_execution(
                input_data, {}, triggered_by, duration,
                success=False, error=str(e)
            )
            return AgentResult(
                success=False,
                error=str(e),
                agent_name=self.name,
                duration_ms=duration,
            )

        except Exception as e:
            logger.exception(f"Agent {self.name} unexpected error")
            return AgentResult(
                success=False,
                error=f"Beklenmeyen hata: {str(e)}",
                agent_name=self.name,
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
        Cikti dogrulama. Override ederek ozel dogrulama eklenebilir.

        Returns:
            None: Gecerli
            str: Hata mesaji
        """
        return None

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
