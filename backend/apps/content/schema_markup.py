"""E-E-A-T Schema Markup Generator. JSON-LD structured data for Google."""
from django.conf import settings

SITE_URL = getattr(settings, 'SITE_URL', 'https://neurocare.com.tr')
SITE_NAME = getattr(settings, 'SITE_NAME', 'NeuroCare')
ORG_LOGO = SITE_URL + '/images/logo.png'


def _get_lang(request=None):
    if request and hasattr(request, 'headers'):
        return request.headers.get('Accept-Language', 'tr')[:2]
    return 'tr'


def _build_person_schema(author_user):
    person = {'@type': 'Person', 'name': author_user.get_full_name()}
    try:
        da = author_user.doctor_profile.author_profile
        person['jobTitle'] = da.get_primary_specialty_display()
        if da.institution:
            person['affiliation'] = {'@type': 'Organization', 'name': da.institution}
            if da.department:
                person['affiliation']['department'] = {'@type': 'Organization', 'name': da.department}
        if da.bio_tr:
            person['description'] = da.bio_tr[:300]
        if da.profile_photo:
            person['image'] = SITE_URL + da.profile_photo.url
        same_as = []
        if da.orcid_id:
            same_as.append('https://orcid.org/' + da.orcid_id)
        if da.google_scholar_url:
            same_as.append(da.google_scholar_url)
        if da.linkedin_url:
            same_as.append(da.linkedin_url)
        if same_as:
            person['sameAs'] = same_as
        if da.website_url:
            person['url'] = da.website_url
        if da.is_verified:
            person['hasCredential'] = {
                '@type': 'EducationalOccupationalCredential',
                'credentialCategory': 'Medical Doctor',
                'recognizedBy': {'@type': 'Organization', 'name': da.institution or 'T.C. Saglik Bakanligi'},
            }
        if da.education:
            person['alumniOf'] = []
            for edu in da.education[:3]:
                name = edu.get('institution', edu.get('name', '')) if isinstance(edu, dict) else str(edu)
                if name:
                    person['alumniOf'].append({'@type': 'EducationalOrganization', 'name': name})
    except Exception:
        pass
    return person


def _build_organization_schema():
    return {'@type': 'Organization', 'name': SITE_NAME, 'url': SITE_URL, 'logo': {'@type': 'ImageObject', 'url': ORG_LOGO}}


def _build_review_schema(article):
    try:
        review = article.reviews.filter(decision='publish').order_by('-created_at').first()
        if not review:
            return None
        s = {'@type': 'Review', 'reviewRating': {'@type': 'Rating', 'ratingValue': review.overall_score, 'bestRating': 100, 'worstRating': 0}}
        if review.reviewer:
            s['author'] = {'@type': 'Person', 'name': review.reviewer.get_full_name()}
        return s
    except Exception:
        return None


def generate_article_schema(article, request=None):
    lang = _get_lang(request)
    title = getattr(article, 'title_' + lang, article.title_tr)
    excerpt = getattr(article, 'excerpt_' + lang, article.excerpt_tr) or ''
    body = getattr(article, 'body_' + lang, article.body_tr) or ''
    seo_title = getattr(article, 'seo_title_' + lang, '') or title
    seo_desc = getattr(article, 'seo_description_' + lang, '') or excerpt[:160]

    schema = {
        '@context': 'https://schema.org',
        '@type': ['MedicalWebPage', 'Article'],
        'headline': seo_title,
        'name': title,
        'description': seo_desc,
        'url': SITE_URL + '/blog/' + article.slug,
        'inLanguage': 'tr' if lang == 'tr' else 'en',
        'isAccessibleForFree': True,
        'publisher': _build_organization_schema(),
        'medicalAudience': {'@type': 'MedicalAudience', 'audienceType': 'Patient'},
    }
    if article.published_at:
        schema['datePublished'] = article.published_at.isoformat()
    if article.updated_at:
        schema['dateModified'] = article.updated_at.isoformat()
    author_user = None
    if hasattr(article, 'doctor_author') and article.doctor_author:
        author_user = article.doctor_author.doctor.user
    elif article.author:
        author_user = article.author
    if author_user:
        schema['author'] = _build_person_schema(author_user)
    if article.featured_image:
        schema['image'] = {'@type': 'ImageObject', 'url': SITE_URL + article.featured_image.url}
    if article.category:
        schema['articleSection'] = getattr(article.category, 'name_' + lang, article.category.name_tr)
    if body:
        schema['wordCount'] = len(body.split())
    review_s = _build_review_schema(article)
    if review_s:
        schema['review'] = review_s
    schema['lastReviewed'] = (article.updated_at or article.published_at or article.created_at).strftime('%Y-%m-%d')
    schema['mainEntity'] = {'@type': 'WebPage', 'breadcrumb': {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Ana Sayfa', 'item': SITE_URL},
        {'@type': 'ListItem', 'position': 2, 'name': 'Blog', 'item': SITE_URL + '/blog'},
        {'@type': 'ListItem', 'position': 3, 'name': title},
    ]}}
    return schema


def generate_news_schema(news_article, request=None):
    lang = _get_lang(request)
    title = getattr(news_article, 'title_' + lang, news_article.title_tr) or news_article.title_tr
    excerpt = getattr(news_article, 'excerpt_' + lang, news_article.excerpt_tr) or ''
    body = getattr(news_article, 'body_' + lang, news_article.body_tr) or ''

    schema = {
        '@context': 'https://schema.org',
        '@type': 'NewsArticle',
        'headline': news_article.meta_title or title,
        'name': title,
        'description': news_article.meta_description or excerpt[:160],
        'url': SITE_URL + '/news/' + news_article.slug,
        'inLanguage': 'tr' if lang == 'tr' else 'en',
        'isAccessibleForFree': True,
        'publisher': _build_organization_schema(),
    }
    if news_article.published_at:
        schema['datePublished'] = news_article.published_at.isoformat()
    if news_article.updated_at:
        schema['dateModified'] = news_article.updated_at.isoformat()
    if news_article.author:
        try:
            schema['author'] = _build_person_schema(news_article.author.doctor.user)
        except Exception:
            pass
    if news_article.featured_image:
        schema['image'] = {'@type': 'ImageObject', 'url': SITE_URL + news_article.featured_image.url, 'caption': news_article.featured_image_alt or title}
    if news_article.keywords:
        schema['keywords'] = news_article.keywords if isinstance(news_article.keywords, list) else [news_article.keywords]
    if news_article.source_urls:
        schema['citation'] = news_article.source_urls
    if body:
        schema['wordCount'] = len(body.split())
    review_s = _build_review_schema(news_article)
    if review_s:
        schema['review'] = review_s
    return schema
