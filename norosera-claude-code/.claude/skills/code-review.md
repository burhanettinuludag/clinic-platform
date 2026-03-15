# Skill: Kod Review & Refactoring — Norosera

## Trigger
review, refactor, optimize, temizle, clean, düzenle, performans, code smell

## Rules

### Code Smell Detection
Aşağıdaki pattern'leri tespit et ve düzelt:

#### Python/Django
- `except Exception: pass` → Specific exception + logging
- `queryset.all()` in loops → `select_related()` / `prefetch_related()`
- N+1 queries → `annotate()` / `aggregate()`
- `len(queryset)` → `queryset.count()`
- `if queryset:` → `if queryset.exists()`
- Business logic in views → Move to model methods or services
- Fat views → Extract to service layer: `apps/<app>/services.py`

#### TypeScript/React
- `useEffect` with missing dependencies
- Props drilling > 3 levels → Context or Zustand
- Inline styles → Tailwind classes
- `any` type → Proper interface
- Large components (>200 lines) → Split into smaller components
- API calls in components → Custom hooks in `hooks/`

### Refactoring Pattern
```
1. Testlerin geçtiğini doğrula
2. Refactoring yap
3. Testlerin hâlâ geçtiğini doğrula
4. Yeni testler ekle (gerekirse)
5. Commit
```

### Performance Checklist
- Django: `django-debug-toolbar` ile N+1 query kontrolü
- Django: `EXPLAIN ANALYZE` ile yavaş query'leri tespit
- Next.js: `next build` → bundle size analizi
- Next.js: Lighthouse score > 90
- Images: WebP format, lazy loading, proper sizing
- API: Pagination zorunlu (max 50/page)
- Celery: Long-running tasks async'e taşınmış mı
