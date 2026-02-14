#!/usr/bin/env python3
"""
SEO Agent Uctan Uca Test.
Calistirma: cd backend && python3 tests/test_seo_agent_e2e.py
"""
import os, sys, json, logging
from unittest.mock import patch
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django; django.setup()

from services.agents.seo_agent import SEOAgent
from services.base_agent import AgentResult
from services.llm_client import LLMResponse

logging.basicConfig(level=logging.WARNING)
PASSED = FAILED = TOTAL = 0

SAMPLE_INPUT = {
    'title_tr': 'Migren Atagi Sirasinda Ne Yapmali?',
    'body_tr': 'Migren tek tarafli zonklayici siddetli bas agrilarinin eslik ettigi norolojik bir hastaliktir. '
               'Migren atagi sirasinda karanlik sessiz odada dinlenin, soguk kompres uygulayin, '
               'doktorunuzun onerdigi ilaci alin. Atak 72 saatten uzun surerse acil servise basvurun. '
               'Tedavide triptan grubu ilaclar ve preventif tedaviler kullanilir.',
    'excerpt_tr': 'Migren atagi sirasinda yapilmasi gerekenleri ogrenin.',
    'suggested_category': 'noroloji',
    'module': 'migraine',
}

MOCK_JSON = json.dumps({
    'seo_title_tr': 'Migren Atagi: Yapilmasi Gerekenler | Uzman Noroloji',
    'seo_title_en': 'Migraine Attack: What to Do | Expert Neurology',
    'seo_description_tr': 'Migren atagi sirasinda yapilmasi gerekenleri noroloji uzmani anlatiyor.',
    'seo_description_en': 'Learn what to do during a migraine attack from a neurology expert.',
    'schema_type': 'MedicalCondition',
    'schema_json': {'@context': 'https://schema.org', '@type': 'MedicalWebPage'},
    'keywords_tr': ['migren tedavisi', 'migren atagi', 'bas agrisi', 'noroloji', 'triptan'],
    'keywords_en': ['migraine treatment', 'migraine attack', 'headache', 'neurology', 'triptan'],
    'internal_links': [{'text': 'Migren', 'path': '/patient/migraine', 'reason': 'hasta takip'}],
    'eeat_signals': {'author': 'Prof. Dr. Burhanettin Uludag', 'credentials': 'Noroloji Uzmani', 'institution': 'Ege Universitesi'},
})

def mock_llm():
    return LLMResponse(content=MOCK_JSON, provider='mock', model='mock', tokens_used=500, duration_ms=100, raw={})

def t(name):
    def dec(f):
        def w():
            global PASSED, FAILED, TOTAL; TOTAL += 1
            try: f(); PASSED += 1; print(f'  \033[92mPASS\033[0m {name}')
            except Exception as e: FAILED += 1; print(f'  \033[91mFAIL\033[0m {name}: {e}')
        return w
    return dec

@t('1. SEO Agent mock LLM ile calistirma')
def t1():
    a = SEOAgent()
    with patch.object(a, 'llm_call', return_value=mock_llm()):
        r = a.execute(SAMPLE_INPUT)
    assert r.get('seo_title_tr'), 'seo_title_tr bos'
    assert r.get('seo_title_en'), 'seo_title_en bos'
    assert r.get('seo_description_tr'), 'seo_description_tr bos'
    assert len(r['keywords_tr']) == 5, f'keywords {len(r["keywords_tr"])}'
    assert 'Burhanettin' in r['eeat_signals'].get('author', '')
    assert r['title_tr'] == SAMPLE_INPUT['title_tr'], 'input kayboldu'

@t('2. Output validation - basarili')
def t2():
    a = SEOAgent()
    assert a.validate_output({'seo_title_tr': 'Test'}) is None

@t('3. Output validation - bos body')
def t3():
    a = SEOAgent()
    assert a.validate_output({'seo_error': 'bos'}) is not None

@t('4. Output validation - parse hatasi')
def t4():
    assert SEOAgent().validate_output({'seo_parse_error': True}) is not None

@t('5. Output validation - title eksik')
def t5():
    assert SEOAgent().validate_output({'seo_description_tr': 'x'}) is not None

@t('6. SEO title 70 char siniri')
def t6():
    r = SEOAgent()._parse_response(json.dumps({'seo_title_tr': 'A'*80, 'seo_title_en': 'ok', 'seo_description_tr': 'x', 'seo_description_en': 'x', 'keywords_tr': [], 'keywords_en': [], 'internal_links': [], 'eeat_signals': {}}))
    assert len(r['seo_title_tr']) <= 70

@t('7. Bozuk JSON handle')
def t7():
    assert SEOAgent()._parse_response('rastgele metin').get('seo_parse_error')

@t('8. Markdown sarili JSON parse')
def t8():
    r = SEOAgent()._parse_response('```json\n' + MOCK_JSON + '\n```')
    assert r.get('seo_title_tr')

@t('9. BaseAgent.run entegrasyon')
def t9():
    a = SEOAgent()
    with patch.object(a, 'is_enabled', return_value=True), patch.object(a, 'llm_call', return_value=mock_llm()):
        r = a.run(SAMPLE_INPUT)
    assert isinstance(r, AgentResult)
    assert r.success, f'Hata: {r.error}'
    assert r.data.get('seo_title_tr')
    assert r.agent_name == 'seo_agent'

@t('10. FeatureFlag kapali -> skip')
def t10():
    a = SEOAgent()
    with patch.object(a, 'is_enabled', return_value=False):
        r = a.run(SAMPLE_INPUT)
    assert not r.success

@t('11. Prompt build kontrol')
def t11():
    p = SEOAgent()._build_prompt('Test', 'Body', 'noroloji', 'migraine')
    assert 'migren' in p.lower()
    assert 'YMYL' in p
    assert 'E-E-A-T' in p

@t('12. Body kisaltma (1500 char)')
def t12():
    p = SEOAgent()._build_prompt('T', 'X'*3000, 'c', 'general')
    assert 'X'*1501 not in p

@t('13. Schema markup import')
def t13():
    from apps.content.schema_markup import generate_article_schema, generate_news_schema
    assert callable(generate_article_schema)
    assert callable(generate_news_schema)

@t('14. Gercek LLM testi (opsiyonel)')
def t14():
    from django.conf import settings
    key = getattr(settings, 'GROQ_API_KEY', '') or os.environ.get('GROQ_API_KEY', '')
    if not key:
        print('    \033[93mSKIP\033[0m GROQ_API_KEY yok'); return
    a = SEOAgent()
    with patch.object(a, 'is_enabled', return_value=True):
        r = a.run(SAMPLE_INPUT)
    if not r.success:
        print(f'    \033[93mWARN\033[0m {r.error}'); return
    d = r.data
    assert d.get('seo_title_tr'), 'title bos'
    assert len(d['seo_title_tr']) <= 70
    print(f'    Provider:{r.provider} Tokens:{r.tokens_used} {r.duration_ms}ms')
    print(f'    Title: {d["seo_title_tr"]}')

if __name__ == '__main__':
    print('\n' + '='*55 + '\nSEO Agent - Uctan Uca Test\n' + '='*55)
    for fn in [t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12,t13,t14]: fn()
    print(f'\n{"="*55}\nSonuc: {PASSED}/{TOTAL} basarili', end='')
    if FAILED: print(f', \033[91m{FAILED} basarisiz\033[0m')
    else: print(f' \033[92m(tumu gecti!)\033[0m')
    print('='*55 + '\n')
    sys.exit(0 if FAILED == 0 else 1)
