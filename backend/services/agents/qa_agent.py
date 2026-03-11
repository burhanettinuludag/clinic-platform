import json
import logging
import re
from typing import Optional
from services.base_agent import BaseAgent
from services.prompts.qa_prompts import QA_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class QAAgent(BaseAgent):
    name = 'qa_agent'
    task_type = 'check_quality'
    system_prompt = QA_SYSTEM_PROMPT
    feature_flag_key = 'agent_qa'
    temperature = 0.6
    max_tokens = 3000

    def execute(self, input_data):
        question = input_data.get('question', '').strip()
        language = input_data.get('language', 'tr')
        module = input_data.get('module', None)
        if not question:
            return {'error': 'Soru (question) bos'}
        context_docs = self._search_content(question, language, module)
        if context_docs:
            context_text = self._build_context(context_docs, language)
            prompt = self._build_prompt(question, context_text, language)
        else:
            prompt = self._build_general_prompt(question, language, module)
        response = self.llm_call(prompt)
        result = self._parse_response(response.content)
        result['sources'] = [
            {'id': str(doc['id']), 'title': doc['title'], 'type': doc['type']}
            for doc in context_docs
        ] if context_docs else []
        result['disclaimer'] = self._get_disclaimer(language)
        result['qa_provider'] = response.provider
        result['qa_tokens'] = response.tokens_used
        if not result.get('confidence'):
            if context_docs:
                result['confidence'] = 'high' if len(context_docs) >= 2 else 'medium'
            else:
                result['confidence'] = 'medium'
                result['general_response'] = True
        return result

    def _search_content(self, question, language, module=None, max_results=3):
        try:
            from django.db.models import Q
            from apps.content.models import Article, EducationItem
            stop_words_tr = {'bir', 've', 'ile', 'bu', 'da', 'de', 'mi', 'mu',
                           'ne', 'nasil', 'neden', 'hangi', 'icin', 'ben', 'benim',
                           'var', 'yok', 'olan', 'olarak', 'gibi', 'daha', 'en'}
            stop_words_en = {'a', 'an', 'the', 'is', 'are', 'was', 'were', 'what',
                           'how', 'why', 'when', 'which', 'do', 'does', 'can', 'my',
                           'i', 'me', 'and', 'or', 'but', 'in', 'on', 'at', 'to'}
            stop_words = stop_words_tr if language == 'tr' else stop_words_en
            words = [w.lower() for w in re.split(r'\s+', question) if len(w) > 2 and w.lower() not in stop_words]
            if not words:
                words = [w.lower() for w in re.split(r'\s+', question) if len(w) > 1]
            results = []
            tf = 'title_tr' if language == 'tr' else 'title_en'
            bf = 'body_tr' if language == 'tr' else 'body_en'
            article_q = Q(status='published')
            wq = Q()
            for word in words[:5]:
                wq |= Q(**{f'{tf}__icontains': word}) | Q(**{f'{bf}__icontains': word})
            article_q &= wq
            for a in Article.objects.filter(article_q)[:max_results]:
                body = getattr(a, bf, '') or ''
                results.append({'id': a.id, 'title': getattr(a, tf, ''), 'body': body[:1000], 'type': 'article'})
            edu_q = Q(is_published=True)
            ewq = Q()
            for word in words[:5]:
                ewq |= Q(**{f'{tf}__icontains': word}) | Q(**{f'{bf}__icontains': word})
            edu_q &= ewq
            if module:
                edu_q &= Q(disease_module__disease_type=module)
            for e in EducationItem.objects.filter(edu_q)[:max_results]:
                body = getattr(e, bf, '') or ''
                results.append({'id': e.id, 'title': getattr(e, tf, ''), 'body': body[:1000], 'type': 'education'})
            return results[:max_results]
        except Exception as e:
            logger.error(f"Content search error: {e}")
            return []

    def _build_general_prompt(self, question, language, module=None):
        module_info = ''
        if module:
            module_names = {
                'migraine': 'migren', 'epilepsy': 'epilepsi',
                'dementia': 'demans', 'parkinson': 'parkinson'
            }
            module_info = f"\nHastanin takip modulu: {module_names.get(module, module)}"
        if language == 'tr':
            return f"""Sen Norosera noroloji platformunun hasta destek asistani Nora'sin.
Hasta sana bir soru soruyor. Sicak, empatik ve bilgilendirici bir sekilde yanit ver.
{module_info}
HASTA SORUSU: {question}

YANITLAMA TARZI:
1. Once hastaya empati goster - "Gecmis olsun", "Sizi anliyorum" gibi ifadelerle basla
2. Soruyu detayli ve anlasilir sekilde acikla - en az 5-8 cumle yaz
3. Pratik gunluk hayat onerileri sun (dinlenme, su icme, stres yonetimi, uyku duzeni vb.)
4. Genel saglik bilgisi ver ama kesin teshis koyma
5. Spesifik ilac ismi veya dozaj soyleme
6. Ciddi belirtilerde dogal bir sekilde hekime yonlendir
7. Sicak, anlayisli, insani bir dil kullan - robot gibi konusma

CIKTI (JSON):
{{"answer": "Yanitiniz (detayli, empatik, en az 5-8 cumle)", "confidence": "medium", "key_points": ["Onemli noktalar"]}}
SADECE JSON dondur."""
        else:
            return f"""You are Nora, Norosera neurology platform's patient support assistant.
A patient is asking you a question. Respond with warmth, empathy and detailed information.
{module_info}
PATIENT QUESTION: {question}

RESPONSE STYLE:
1. Start with empathy - "I'm sorry to hear that", "I understand how difficult this must be"
2. Explain the topic in detail - write at least 5-8 sentences
3. Offer practical daily life advice (rest, hydration, stress management, sleep hygiene etc.)
4. Provide general health information but don't make definitive diagnoses
5. Don't mention specific medication names or dosages
6. Naturally suggest seeing a doctor for serious symptoms
7. Use a warm, understanding, human tone - don't sound robotic

OUTPUT (JSON):
{{"answer": "Your answer (detailed, empathetic, at least 5-8 sentences)", "confidence": "medium", "key_points": ["Key points"]}}
Return ONLY JSON."""

    def _build_context(self, docs, language):
        parts = []
        for i, doc in enumerate(docs, 1):
            parts.append(f"--- Kaynak {i}: {doc['title']} ---\n{doc['body']}")
        return '\n\n'.join(parts)

    def _build_prompt(self, question, context, language):
        if language == 'tr':
            return f"""Sen Nora'sin - Norosera'nin hasta destek asistani. Asagidaki kaynaklara dayanarak hastanin sorusuna sicak ve detayli bir yanit ver.

HASTA SORUSU: {question}

KAYNAKLAR:
{context}

YANITLAMA TARZI:
1. Once hastaya empati goster - "Gecmis olsun", "Sizi anliyorum" gibi ifadelerle basla
2. Kaynaklardaki bilgileri kendi cumlelerinle, anlasilir sekilde anlat - en az 5-8 cumle
3. Pratik oneriler ve gunluk hayat ipuclari ekle
4. Kaynakta bilgi yoksa "Bu konuda daha fazla arastirma yapiyoruz" de
5. Kesin teshis koyma, spesifik ilac ismi soyleme
6. Dogal, sicak ve insani bir dil kullan

CIKTI (JSON):
{{"answer": "Yanitiniz (detayli, empatik, en az 5-8 cumle)", "confidence": "high|medium|low", "key_points": ["Onemli noktalar"]}}
SADECE JSON dondur."""
        else:
            return f"""You are Nora - Norosera's patient support assistant. Answer the patient's question based on the sources below with warmth and detail.

QUESTION: {question}

SOURCES:
{context}

RESPONSE STYLE:
1. Start with empathy - "I'm sorry to hear that", "I understand"
2. Explain using the source information in your own words - at least 5-8 sentences
3. Add practical tips and daily life advice
4. If sources don't cover the topic, say "We're researching more on this topic"
5. Don't make diagnoses or mention specific medications
6. Use a natural, warm, human tone

OUTPUT (JSON):
{{"answer": "Your answer (detailed, empathetic, at least 5-8 sentences)", "confidence": "high|medium|low", "key_points": ["Key points"]}}
Return ONLY JSON."""

    def _parse_response(self, content):
        cleaned = content.strip()
        if cleaned.startswith('```'):
            cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
            raw = match.group(0)
            am = re.search(r'"answer"\s*:\s*"(.*?)"(?:\s*,\s*"(?:confidence|key_)|\s*\})', raw, re.DOTALL)
            if am:
                return {'answer': am.group(1).replace('\\n', '\n'), 'confidence': 'medium'}
        return {'answer': content, 'confidence': 'low', 'parse_error': True}

    def _get_disclaimer(self, language):
        if language == 'tr':
            return 'Bu yanit yayinlanmis iceriklerimize dayanmaktadir ve tibbi oneri yerine gecmez. Lutfen hekiminize danisiniz.'
        return 'This answer is based on our published content and does not replace medical advice. Please consult your physician.'

    def validate_output(self, output):
        if output.get('error'):
            return output['error']
        if not output.get('answer'):
            return 'Yanit (answer) bos'
        return None
