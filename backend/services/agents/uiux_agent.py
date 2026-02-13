"""
UI/UX Tasarimci Ajan.

3 modda calisir:
1. design_system: Renk, font, spacing kurallari + Tailwind config onerisi
2. analyze_page: Mevcut sayfa kodunu analiz et, iyilestirme oner
3. generate_component: React/Tailwind komponent kodu uret

Diger ajanlardan bagimsiz calisabilir veya orkestrator ile zincirlenir.
"""

import json
import logging
import re
from typing import Optional

from services.base_agent import BaseAgent
from services.prompts.uiux_prompts import (
    DESIGN_SYSTEM_PROMPT,
    PAGE_ANALYZER_PROMPT,
    COMPONENT_GENERATOR_PROMPT,
)

logger = logging.getLogger(__name__)


# Mevcut Norosera design token'lari - globals.css'den alinmis
NOROSERA_DESIGN_TOKENS = {
    'colors': {
        'primary': {'name': 'Teal/Cyan', 'hex': '#06b6d4', 'use': 'Medical, calming'},
        'secondary': {'name': 'Deep Purple', 'hex': '#9333ea', 'use': 'Neurology, brand'},
        'accent': {'name': 'Soft Rose', 'hex': '#f43f5e', 'use': 'Warmth, care'},
        'success': '#10b981',
        'warning': '#f59e0b',
        'error': '#ef4444',
        'info': '#3b82f6',
    },
    'module_colors': {
        'migraine': '#8b5cf6',
        'epilepsy': '#f59e0b',
        'parkinson': '#10b981',
        'dementia': '#ec4899',
    },
    'font': 'Inter, system-ui, -apple-system, sans-serif',
    'framework': 'Tailwind CSS 4 + @tailwindcss/typography',
    'existing_components': [
        'BrainIcon', 'DisclaimerBanner', 'ErrorBoundary',
        'LanguageSwitcher', 'LoadingSpinner', 'NeuralAnimation', 'WhaleAnimation',
    ],
    'css_classes': [
        'gradient-medical', 'gradient-hero', 'gradient-card',
        'glass', 'glass-dark', 'card-medical',
        'btn-primary', 'btn-secondary', 'text-gradient', 'brain-glow',
        'neural-bg', 'animate-neuron-pulse', 'animate-float', 'animate-pulse-slow',
    ],
}


class UIUXAgent(BaseAgent):
    """Kapsamli UI/UX tasarim ajani - design system, analiz, component uretimi."""

    name = 'uiux_agent'
    system_prompt = DESIGN_SYSTEM_PROMPT  # Default, mode'a gore degisir
    feature_flag_key = 'agent_uiux'
    temperature = 0.5
    max_tokens = 4000

    def execute(self, input_data: dict) -> dict:
        """
        UI/UX gorevi calistir.

        Input:
            mode: str - 'design_system' | 'analyze_page' | 'generate_component'

            design_system modu:
                aspect: str - 'colors' | 'typography' | 'spacing' | 'full_audit'

            analyze_page modu:
                page_code: str - TSX/JSX sayfa kodu
                page_name: str - Sayfa ismi
                role: str - 'patient' | 'doctor' | 'public'

            generate_component modu:
                component_name: str - Olusturulacak komponent ismi
                description: str - Ne yapmasi gerektiginin aciklamasi
                role: str - 'patient' | 'doctor' | 'public'
                variant: str - 'card' | 'form' | 'modal' | 'list' | 'chart' | 'custom'

        Output:
            mode'a gore degisir
        """
        mode = input_data.get('mode', 'design_system')

        if mode == 'design_system':
            return self._design_system(input_data)
        elif mode == 'analyze_page':
            return self._analyze_page(input_data)
        elif mode == 'generate_component':
            return self._generate_component(input_data)
        else:
            return {'error': f"Bilinmeyen mod: {mode}. Gecerli: design_system, analyze_page, generate_component"}

    def _design_system(self, input_data: dict) -> dict:
        """Design system analizi ve onerisi."""
        self.system_prompt = DESIGN_SYSTEM_PROMPT
        aspect = input_data.get('aspect', 'full_audit')

        prompt = f"""Mevcut Norosera design token'larini analiz et ve iyilestirme oner.

MEVCUT DESIGN TOKENS:
{json.dumps(NOROSERA_DESIGN_TOKENS, indent=2, ensure_ascii=False)}

ANALIZ ALANI: {aspect}

PLATFORM BILGISI:
- Noroloji klinigi platformu (migren, epilepsi, demans modulleri)
- Hasta paneli (sakin, rahatlatici) + Doktor paneli (data-yogun, profesyonel)
- Tailwind CSS 4, Next.js 16, lucide-react ikonlar
- Mobil oncelikli tasarim

CIKTI FORMATI (JSON):
{{
    "analysis": "Mevcut durum degerlendirmesi",
    "score": 0-100,
    "issues": ["Tespit edilen sorunlar"],
    "recommendations": [
        {{
            "area": "colors|typography|spacing|accessibility|consistency",
            "current": "Mevcut durum",
            "suggested": "Onerilen degisiklik",
            "reason": "Neden",
            "priority": "high|medium|low",
            "code_snippet": "Tailwind/CSS kodu (varsa)"
        }}
    ],
    "accessibility": {{
        "wcag_level": "A|AA|AAA",
        "contrast_issues": ["Kontrast sorunlari"],
        "suggestions": ["Erisebilirlik onerileri"]
    }},
    "tailwind_config": "Onerilen Tailwind config degisiklikleri (varsa)"
}}

SADECE JSON dondur."""

        response = self.llm_call(prompt)
        result = self._parse_response(response.content)
        result['mode'] = 'design_system'
        result['aspect'] = aspect
        return result

    def _analyze_page(self, input_data: dict) -> dict:
        """Mevcut sayfa kodunu analiz et."""
        self.system_prompt = PAGE_ANALYZER_PROMPT
        page_code = input_data.get('page_code', '')
        page_name = input_data.get('page_name', 'unknown')
        role = input_data.get('role', 'patient')

        if not page_code:
            return {'error': 'page_code zorunlu'}

        # Kodu kisalt
        code_preview = page_code[:3000] if len(page_code) > 3000 else page_code

        prompt = f"""Bu React sayfa kodunu UI/UX acisindan analiz et.

SAYFA: {page_name}
ROL: {role} (hasta=sakin/rahatlatici, doktor=data-yogun/profesyonel)

MEVCUT DESIGN TOKENS:
Primary: Teal #06b6d4 | Secondary: Purple #9333ea | Accent: Rose #f43f5e
Mevcut CSS siniflar: {', '.join(NOROSERA_DESIGN_TOKENS['css_classes'])}

SAYFA KODU:
{code_preview}

ANALIZ KRITERLERI:
1. Renk tutarliligi (design token'lara uyum)
2. Tipografi hiyerarsisi
3. Spacing ve hizalama
4. Responsive tasarim (mobile-first)
5. Erisebilirlik (WCAG 2.1 AA)
6. Kullanici deneyimi (UX flow)
7. Loading/error/empty state yonetimi
8. Performans (gereksiz re-render, buyuk bundle)

CIKTI FORMATI (JSON):
{{
    "page_name": "{page_name}",
    "overall_score": 0-100,
    "ux_score": 0-100,
    "accessibility_score": 0-100,
    "consistency_score": 0-100,
    "issues": [
        {{
            "severity": "critical|warning|info",
            "area": "color|typography|spacing|accessibility|ux|performance",
            "description": "Sorun aciklamasi",
            "line_hint": "Ilgili kod parcasi",
            "fix": "Onerilen duzeltme"
        }}
    ],
    "suggestions": [
        {{
            "area": "...",
            "description": "Iyilestirme onerisi",
            "code_snippet": "Onerilen kod"
        }}
    ],
    "missing_states": ["loading", "error", "empty"],
    "accessibility_issues": ["..."]
}}

SADECE JSON dondur."""

        response = self.llm_call(prompt)
        result = self._parse_response(response.content)
        result['mode'] = 'analyze_page'
        result['page_name'] = page_name
        return result

    def _generate_component(self, input_data: dict) -> dict:
        """React komponent kodu uret."""
        self.system_prompt = COMPONENT_GENERATOR_PROMPT
        comp_name = input_data.get('component_name', 'MyComponent')
        description = input_data.get('description', '')
        role = input_data.get('role', 'patient')
        variant = input_data.get('variant', 'custom')

        if not description:
            return {'error': 'description zorunlu'}

        role_guide = {
            'patient': 'Sakin, rahatlatici, buyuk font, bol bosluk, teal/cyan agirlikli, anlasilir ikonlar',
            'doctor': 'Data-yogun, kompakt, tablolar, grafikler, profesyonel, purple agirlikli',
            'public': 'Modern, dikkat cekici, gradient-medical, hero section, CTA butonlari',
        }

        prompt = f"""Asagidaki aciklamaya gore bir React komponenti olustur.

KOMPONENT: {comp_name}
ACIKLAMA: {description}
ROL: {role} - {role_guide.get(role, role)}
VARYANT: {variant}

TASARIM KURALLARI:
- Tailwind CSS 4 kullan (custom class yerine utility-first)
- Norosera design token'lari kullan (primary=teal, secondary=purple, accent=rose)
- Mevcut CSS siniflari kullanabilirsin: {', '.join(NOROSERA_DESIGN_TOKENS['css_classes'][:8])}
- lucide-react ikonlari import et
- TypeScript + React functional component
- Props ile interface tanimla
- Responsive (mobile-first)
- WCAG 2.1 AA uyumlu (aria-label, contrast, keyboard nav)
- Loading, error, empty state'leri icersin
- 'use client' ekle (Next.js)

CIKTI FORMATI (JSON):
{{
    "component_name": "{comp_name}",
    "code": "Tam TSX kodu (string olarak)",
    "props_interface": "TypeScript interface tanimlamasi",
    "usage_example": "Ornek kullanim kodu",
    "dependencies": ["lucide-react", "diger paketler"],
    "design_notes": "Tasarim kararlari aciklamasi",
    "accessibility_notes": "Erisebilirlik notlari"
}}

SADECE JSON dondur."""

        response = self.llm_call(prompt, max_tokens=4000)
        result = self._parse_response(response.content)
        result['mode'] = 'generate_component'
        result['component_name'] = comp_name
        return result

    def _parse_response(self, content: str) -> dict:
        """LLM yanitini parse et - multiline code bloklari icin robust."""
        cleaned = content.strip()
        if cleaned.startswith('```'):
            cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned).strip()
        # 1. Dogrudan parse
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass
        # 2. En dis { } bul
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            raw = match.group(0)
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                pass
            # 3. code alani multiline - key-value extraction
            result = {}
            for key in ['component_name', 'design_notes', 'analysis', 'page_name',
                        'accessibility_notes', 'usage_example', 'props_interface',
                        'tailwind_config', 'wcag_level']:
                km = re.search(r'"' + key + r'"\s*:\s*"((?:[^"\\]|\\.)*)"', raw)
                if km:
                    result[key] = km.group(1).replace('\\n', '\n').replace('\\"', '"')
            # score alanlari (int)
            for key in ['score', 'overall_score', 'ux_score', 'accessibility_score', 'consistency_score']:
                km = re.search(r'"' + key + r'"\s*:\s*(\d+)', raw)
                if km:
                    result[key] = int(km.group(1))
            # array alanlari
            for key in ['dependencies', 'issues', 'missing_states', 'accessibility_issues']:
                km = re.search(r'"' + key + r'"\s*:\s*\[(.*?)\]', raw, re.DOTALL)
                if km:
                    try:
                        result[key] = json.loads('[' + km.group(1) + ']')
                    except json.JSONDecodeError:
                        items = re.findall(r'"((?:[^"\\]|\\.)*)"', km.group(1))
                        if items:
                            result[key] = items
            # code alani - ozel: son key'e kadar al
            cm = re.search(r'"code"\s*:\s*"(.*?)"\s*(?:,\s*"(?!code)|\}$)', raw, re.DOTALL)
            if not cm:
                cm = re.search(r'"code"\s*:\s*"(.*)"\s*\}', raw, re.DOTALL)
            if cm:
                code = cm.group(1).replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"')
                result['code'] = code
            # recommendations array (complex objects)
            rm = re.search(r'"recommendations"\s*:\s*\[(.*)\]', raw, re.DOTALL)
            if rm:
                try:
                    result['recommendations'] = json.loads('[' + rm.group(1) + ']')
                except json.JSONDecodeError:
                    result['recommendations'] = [{'raw': rm.group(1)[:300]}]
            if result:
                return result
        logger.warning('UIUXAgent: JSON parse hatasi')
        return {'uiux_parse_error': True, 'raw_response': cleaned[:500]}

    def validate_output(self, output: dict) -> Optional[str]:
        if output.get('error'):
            return output['error']
        if output.get('uiux_parse_error'):
            return "UI/UX ciktisi parse edilemedi"
        return None
