# Skill: Next.js Frontend — Norosera

## Trigger
frontend, next.js, react, component, page, tailwind, typescript, UI, sayfa, bileşen, arayüz

## Rules

### Page Creation (App Router)
All public pages MUST use SSR:
```typescript
// app/hizmetler/page.tsx
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Hizmetlerimiz | Norosera Nöroloji Kliniği",
  description: "Prof. Dr. Burhanettin Uludağ - Nöroloji ve Klinik Nörofizyoloji",
  openGraph: {
    title: "Hizmetlerimiz | Norosera",
    locale: "tr_TR",
  },
};

async function getServices() {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/services/`, {
    next: { revalidate: 3600 }, // ISR: 1 hour
  });
  if (!res.ok) throw new Error("Failed to fetch");
  return res.json();
}

export default async function HizmetlerPage() {
  const services = await getServices();
  return <ServiceList services={services} />;
}
```

### Component Pattern
```typescript
// components/ServiceCard.tsx
interface ServiceCardProps {
  title: string;
  description: string;
  icon: string;
  slug: string;
}

export function ServiceCard({ title, description, icon, slug }: ServiceCardProps) {
  return (
    <div className="rounded-2xl border border-gray-200 p-6 hover:shadow-lg transition-shadow">
      <h3 className="text-xl font-semibold text-gray-900">{title}</h3>
      <p className="mt-2 text-gray-600">{description}</p>
    </div>
  );
}
```

### API Client
Always use the centralized API client:
```typescript
// lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL;

export async function apiGet<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) {
    throw new Error(`API Error: ${res.status}`);
  }
  return res.json();
}
```

### Tailwind Conventions
- Primary color: `blue-600` / `blue-700` (medical professional theme)
- Use `rounded-2xl` for cards, `rounded-full` for avatars
- Spacing: `space-y-6` for sections, `gap-4` for grids
- Always mobile-first: default → `md:` → `lg:`
- Dark mode: NOT implemented yet — do not add dark mode classes

### SEO Requirements
Every public page MUST have:
1. `Metadata` export with Turkish title + description
2. OpenGraph tags with `locale: "tr_TR"`
3. Structured data (JSON-LD) for medical practice pages
4. `<h1>` tag present exactly once

### TypeScript Rules
- NEVER use `any` — define proper interfaces in `types/`
- Export all shared types from `types/index.ts`
- Use `z` (Zod) for runtime validation of API responses
- Prefer `interface` over `type` for object shapes

### Image Handling
```typescript
import Image from "next/image";

// Always use Next.js Image with explicit dimensions
<Image
  src="/images/clinic.jpg"
  alt="Norosera Nöroloji Kliniği"
  width={800}
  height={600}
  className="rounded-2xl"
  priority // for above-the-fold images
/>
```

### Contact Info (Hardcoded)
```
Adres: Ankara Caddesi No 243/2, Bornova, İzmir
Telefon: +90 532 382 90 31
Email: uludagburhan@yahoo.com
```
