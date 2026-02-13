import json
import logging
import re
from typing import Optional
from services.base_agent import BaseAgent
from services.prompts.qa_prompts import QA_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class QAAgent(BaseAgent):
    name = 'qa_agent'
    system_prompt = QA_SYSTEM_PROMPT
    feature_flag_key = 'agent_qa'
    temperature = 0.3
    max_tokens = 2000

    def execute(self, input_data):
        question = input_data.get('question', '').strip()
        language = input_data.get('language', 'tr')
        module = input_data.get('module', None)
        if not question:
            return {'error': 'Soru (question) bos'}
        context_docs = self._search_content(question, language, module)
        if not context_docs:
            return {
                'answer': 'Bu konuda yayinlanmis bir icerik bulunamadi. Lutfen hekiminize danisin.' if language == 'tr'
                    else 'No published content found on this topic. Please consult your physician.',
                'sources': [],
                'disclaimer': self._get_disclaimer(language),
                'confidence': 'low',
                'no_context': True,
            }
        context_text = self._build_context(context_docs, language)
        prompt = self._build_prompt(question, context_text, language)
        response = self.llm_call(prompt)
        result = self._parse_response(response.content)
        result['sources'] = [
            {'id': str(doc['id']), 'title': doc['title'], 'type': doc['type']}
            for doc in context_docs
        ]
        result['disclaimer'] = self._get_disclaimer(language)
        result['qa_provider'] = response.provider
        result['qa_tokens'] = response.tokens_used
        if not result.get('confidence'):
            result['confidence'] = 'high' if len(context_docs) >= 2 else 'medium'
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

    def _build_context(self, docs, language):
        parts = []
        for i, doc in enumerate(docs, 1):
            parts.append(f"--- Kaynak {i}: {doc['title']} ---\n{doc['body']}")
        return '\n\n'.join(parts)

    def _build_prompt(self, question, context, language):
        if language == 'tr':
            return f"""Asagidaki kaynaklara dayanarak hastanin sorusunu yanitla.

HASTA SORUSU: {question}

KAYNAKLAR:
{context}

KURALLAR:
1. SADECE kaynaklardaki bilgilere dayan
2. Tibbi teshis koyma, tedavi onerme, ilac ismi soyleme
3. Yaniti anlasilir ve samimi bir dilde yaz
4. Kaynakta bilgi yoksa Bu konuda yeterli bilgi bulunamadi de

CIKTI (JSON):
{{"answer": "Yanitiniz", "confidence": "high|medium|low", "key_points": ["Noktalar"]}}
SADECE JSON dondur."""
        else:
            return f"""Answer the patient question based on sources below.

QUESTION: {question}

SOURCES:
{context}

RULES: Only use source info. No diagnosis or medication names.

OUTPUT (JSON):
{{"answer": "Your answer", "confidence": "high|medium|low", "key_points": ["Points"]}}
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
