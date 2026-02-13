"""
Hukuk & Uyumluluk Ajani.

Icerik yayinlanmadan once hukuki kontrol yapar:
- Tibbi oneri iceriyor mu? (YASAK)
- Disclaimer var mi?
- Ilac ismi/dozaj belirtilmis mi? (YASAK)
- KVKK uyumu
- Saglik Bakanligi yonergeleri
- Yaniltici ifade var mi?

Content Agent + SEO Agent'tan sonra, publish oncesi son kontrol.
Red ederse pipeline DURUR, icerik yayinlanmaz.
"""

import json
import logging
from typing import Optional

from services.base_agent import BaseAgent
from services.prompts.legal_prompts import LEGAL_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class LegalAgent(BaseAgent):
    """Saglik hukuku uyumluluk kontrol ajani."""

    name = 'legal_agent'
    system_prompt = LEGAL_SYSTEM_PROMPT
    feature_flag_key = 'agent_legal'
    temperature = 0.1  # Hukuki kontrol icin minimum yaraticilik
    max_tokens = 2000

    def execute(self, input_data: dict) -> dict:
        """
        Hukuki uyumluluk kontrolu yap.

        Input (Content + SEO Agent'tan gelir):
            title_tr: str - Baslik
            body_tr: str - Icerik
            content_type: str - blog/education/social

        Output (input_data + hukuki kontrol sonuclari):
            legal_approved: bool - Onay durumu
            legal_score: int - 0-100 uyumluluk puani
            legal_issues: list - Tespit edilen sorunlar
            legal_warnings: list - Uyarilar (red sebebi degil)
            legal_suggestions: list - Iyilestirme onerileri
            disclaimer_present: bool - Disclaimer var mi
            medical_advice_detected: bool - Tibbi oneri tespit edildi mi
        """
        title = input_data.get('title_tr', '')
        body = input_data.get('body_tr', '')
        content_type = input_data.get('content_type', 'blog')

        if not body:
            return {**input_data, 'legal_approved': False,
                    'legal_issues': ['Icerik bos']}

        prompt = self._build_prompt(title, body, content_type)
        response = self.llm_call(prompt)
        legal_data = self._parse_response(response.content)

        # Mevcut input_data ile merge et
        result = {**input_data, **legal_data}
        result['legal_provider'] = response.provider
        result['legal_tokens'] = response.tokens_used
        return result

    def _build_prompt(self, title, body, content_type):
        """Hukuki kontrol prompt'u."""
        # Body'yi kisalt
        body_preview = body[:2000] if len(body) > 2000 else body

        return f"""Asagidaki saglik icerigini Turk saglik hukuku acisindan denetle.

BASLIK: {title}
ICERIK TIPI: {content_type}

ICERIK:
{body_preview}

KONTROL LISTESI - her birini tek tek degerlendir:

1. TIBBI ONERI: Icerik dogrudan tibbi oneri veriyor mu?
   - "Bu ilaci icin" -> RED
   - "Doktorunuza danisin" -> OK
   - "Gunluk 2 litre su icin" -> UYARI (genel tavsiye, red degil)

2. ILAC/DOZAJ: Spesifik ilac ismi veya dozaj belirtilmis mi?
   - "Sumatriptan 50mg alin" -> RED
   - "Doktorunuzun verdigi ilaci kullanin" -> OK
   - "Agri kesiciler yardimci olabilir" -> OK (genel sinif, spesifik degil)

3. TESHIS: Teshis koyuyor mu?
   - "Bu belirtiler migren oldugunu gosterir" -> RED
   - "Bu belirtiler migrene isaret edebilir, hekiminize basvurun" -> OK

4. DISCLAIMER: Yazi sonunda sorumluluk reddi var mi?
   - "Bu yazi bilgilendirme amaclidir" veya benzeri -> OK
   - Disclaimer yok -> RED

5. YANILTICI IFADE: Abartili veya yaniltici vaat var mi?
   - "Migreninizi kesin olarak tedavi edin" -> RED
   - "Migren belirtilerini yonetmenize yardimci olabilir" -> OK

6. KISISEL VERI: Icerik kisisel veri toplama/isleme ima ediyor mu?
   - KVKK 6698 kapsaminda degerlendirme

7. REKLAM/TANITIM: Gizli reklam veya urun tanitimi var mi?

PUANLAMA:
- 90-100: Yayina uygun
- 70-89: Kucuk duzeltmelerle yayinlanabilir
- 50-69: Onemli duzeltmeler gerekli
- 0-49: Yayinlanamaz

CIKTI FORMATI (JSON):
{{
    "legal_approved": true/false,
    "legal_score": 0-100,
    "legal_issues": ["RED sebebi olan sorunlar"],
    "legal_warnings": ["RED sebebi olmayan uyarilar"],
    "legal_suggestions": ["Iyilestirme onerileri"],
    "disclaimer_present": true/false,
    "medical_advice_detected": true/false,
    "drug_names_detected": true/false,
    "diagnosis_detected": true/false,
    "misleading_claims_detected": true/false,
    "review_summary": "Kisa genel degerlendirme"
}}

SADECE JSON dondur."""

    def _parse_response(self, content: str) -> dict:
        """LLM yanitini parse et."""
        import re
        cleaned = content.strip()
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                # legal_approved zorunlu alan
                if 'legal_approved' not in data:
                    data['legal_approved'] = data.get('legal_score', 0) >= 70
                return data
            except json.JSONDecodeError:
                pass
        logger.warning('LegalAgent: JSON parse hatasi')
        return {
            'legal_approved': False,
            'legal_issues': ['Hukuki kontrol ciktisi parse edilemedi'],
            'legal_parse_error': True,
        }

    def validate_output(self, output: dict) -> Optional[str]:
        """Cikti dogrulama."""
        if output.get('legal_parse_error'):
            return "Hukuki kontrol ciktisi parse edilemedi"
        # legal_approved False ise bu bir HATA degil, basarili bir RED
        # Pipeline'da stop_on_failure=True olsa bile bu gecerli bir sonuc
        return None
