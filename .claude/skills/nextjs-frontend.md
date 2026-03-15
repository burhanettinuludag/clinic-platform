# Next.js Frontend Skill

## Triggers
frontend, next.js, react, component, page, tailwind, typescript, UI, hook, layout

## Rules

### Tech Stack
- Next.js 16.1.5, React 19, TypeScript 5.9, Tailwind CSS 4
- i18n: next-intl 4.7 (locales: `tr` default, `en`)
- State: React Query 5 (@tanstack/react-query) + AuthContext + CartContext

### Page Pattern
Route pattern: `src/app/[locale]/section/page.tsx`
```typescript
import { useTranslations } from 'next-intl';

export default function MyPage() {
  const t = useTranslations('section');
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-teal-800">{t('title')}</h1>
    </div>
  );
}
```

### Color Theme
- Primary: **teal** (#0d9488 family) — medical theme
- Secondary: **indigo** (#6366f1 family)
- Font: Inter
- Custom classes: `.card-medical`, `.btn-primary`, `.text-gradient`

Do NOT use blue as primary. Always use teal for primary actions/branding.

### API Client
Use the centralized Axios instance at `src/lib/api.ts`:
```typescript
import api from '@/lib/api';
const { data } = await api.get('/doctor/patients/');
```
- Request interceptor: adds Bearer token + Accept-Language
- Response interceptor: auto-refresh on 401, toast errors
- Base URL: `NEXT_PUBLIC_API_URL` or `http://localhost:8000/api/v1`

### Custom Hooks (13 total)
Located in `src/hooks/`:
- `usePatientData`, `useDoctorData`, `useAuthorData`, `useCaregiverData`
- `useChatData`, `useMarketingData`, `useSocialData`
- `useSiteData`, `useSiteAdmin`, `useEditorData`
- `useStoreData`, `useNotifications`

Use existing hooks instead of creating new API calls.

### Types
All in `src/lib/types/`:
- `user.ts` — UserRole, User, AuthTokens
- `patient.ts` — DiseaseModule, MigraineAttack, SeizureEvent
- `doctor.ts` — DoctorPatient, DashboardStats
- `content.ts` — Article, EducationItem, Notification
- `chat.ts` — ChatSession, ChatMessage
- `store.ts` — Product, Order, License

### i18n
- Translations: `messages/tr.json`, `messages/en.json`
- Always add both TR and EN translations when creating new pages
- Use `useTranslations('namespace')` hook

### Middleware Auth
- Tokens in cookies: `access_token`, `refresh_token`, `user_role`
- Route protection in `src/middleware.ts`:
  - `/patient/*` → patient, doctor, admin
  - `/doctor/*` → doctor, admin
  - `/doctor/site-settings` → admin only
  - `/caregiver/*` → caregiver, admin

### Component Organization
```
src/components/
├── layout/     # Header, Footer
├── common/     # Toast, Skeleton, LoadingSpinner, Breadcrumb
├── patient/    # MigraineChart, SeizureChart, WeatherWidget
├── dementia/   # 15+ cognitive game components
├── chat/       # ChatBubble, ChatInput, MessageList
├── news/       # NewsMagazine
└── providers/  # QueryProvider
```

### TypeScript Rules
- NEVER use `any` type — use proper interfaces from `src/lib/types/`
- All component props must have TypeScript interfaces
