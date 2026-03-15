# 🧠 Norosera — Claude Code Otomasyon Paketi

Norosera klinik platformu için tam kapsamlı Claude Code hooks, skills, commands ve agent yapılandırması.

## Hızlı Kurulum

```bash
bash install.sh /path/to/clinic-platform
```

## İçerik Haritası

### 📝 CLAUDE.md — Proje Kuralları
Claude Code'un her oturumda okuduğu ana kural dosyası. İçerir:
- Kritik kurallar (güvenlik, KVKK)
- Tech stack ve dizin yapısı
- Build/test/deploy komutları
- Claude'un sık yaptığı hataların düzeltmeleri

### 🪝 Hooks (6 adet) — Deterministik Kontrol

| Hook | Event | İşlev |
|------|-------|-------|
| `block-dangerous.sh` | PreToolUse | `rm -rf`, `git push -f`, `DROP TABLE` engeller |
| `check-secrets.sh` | PreToolUse | API key, KVKK verisi sızıntısını engeller |
| `auto-lint.sh` | PostToolUse | Dosya kaydedilince otomatik ruff/eslint çalıştırır |
| `verify-migration.sh` | PostToolUse | makemigrations sonrası doğrulama yapar |
| `load-context.sh` | SessionStart | Git durumu, pending migration, Docker durumu yükler |
| `notify-done.sh` | Stop | macOS/Linux masaüstü bildirimi gönderir |

**+ 1 Agent Hook (Stop event):**
Oturum bittiğinde sub-agent spawn eder → migration, permission, type check, KVKK, Türkçe kontrolleri yapar.

### 🎯 Skills (15 adet) — Otomatik Yetenek

| Skill | Tetikleyiciler |
|-------|---------------|
| `django-backend.md` | model, view, serializer, migration, API |
| `nextjs-frontend.md` | component, page, tailwind, typescript, UI |
| `security-kvkk.md` | güvenlik, hasta verisi, şifreleme, KVKK |
| `testing-qa.md` | test, coverage, QA, bug |
| `deployment-cicd.md` | deploy, docker, GitHub Actions, Vercel |
| `ai-agents.md` | agent, content agent, SEO agent |
| `social-media.md` | instagram, linkedin, sosyal medya |
| `code-review.md` | review, refactor, optimize, performans |
| `content-writing.md` | makale, blog yazısı (min. karakter zorunlu) |
| `seo-audit.md` | SEO, kırık link, meta tag, schema.org, sitemap |
| `performance.md` | Lighthouse, N+1, bundle size, görsel optimize |
| `accessibility.md` | WCAG, a11y, ARIA, alt text, erişilebilirlik |
| `database-monitoring.md` | yedekleme, log izleme, health check, uptime |
| `email-templates.md` | randevu mail, takip, hatırlatma şablonları |
| `medical-terminology.md` | tıbbi terim tutarlılığı, glossary |

### ⌨️ Slash Commands (12 adet)

| Komut | İşlev |
|-------|-------|
| `/test` | Backend + frontend testlerini paralel çalıştır |
| `/review` | Değişiklikleri güvenlik, KVKK, kalite açısından incele |
| `/deploy` | Production deploy öncesi tüm kontrolleri yap |
| `/commit` | Conventional commit mesajı oluştur ve commit'le |
| `/doc` | API, model, setup dokümantasyonunu otomatik üret |
| `/newapp <isim>` | Standartlara uygun yeni Django app oluştur |
| `/security` | Kapsamlı güvenlik taraması (dependency + code + KVKK) |
| `/seo` | Kapsamlı SEO denetimi (link, meta, schema, sitemap) |
| `/linkcheck` | Kırık linkleri tara ve düzelt |
| `/perf` | Frontend + backend performans denetimi |
| `/a11y` | WCAG 2.1 AA erişilebilirlik taraması |
| `/health` | Tüm sistem bileşenlerinin sağlık kontrolü |

## Mimari

```
Kullanıcı Input
     │
     ▼
┌─────────────────┐
│  SessionStart    │ → Git durumu, migration check, Docker status yükle
│  Hook            │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────┐
│  CLAUDE.md       │────→│  Skills       │ → Otomatik algıla & uygula
│  (Kurallar)      │     │  (7 adet)    │
└────────┬────────┘     └──────────────┘
         │
         ▼
┌─────────────────┐
│  Claude Code     │
│  Agent Loop      │
└────────┬────────┘
         │
    ┌────┼────┐
    ▼    ▼    ▼
┌──────┐┌──────┐┌──────┐
│PreUse││PostUs││ Stop  │
│Hooks ││Hooks ││ Hook  │
└──┬───┘└──┬───┘└──┬───┘
   │       │       │
   ▼       ▼       ▼
Block    Lint    Verify
Secrets  Format  & Notify
```

## Özelleştirme

### Yeni Hook Eklemek
`hooks/<event>/` dizinine `.sh` dosyası ekleyin, `.claude/settings.json`'a kaydedin.

### Yeni Skill Eklemek
`.claude/skills/` dizinine `.md` dosyası ekleyin. Claude otomatik algılar.

### Yeni Command Eklemek
`.claude/commands/` dizinine `.md` dosyası ekleyin. Terminal'de `/isim` ile çağırın.

## Gereksinimler

- Claude Code CLI (terminal) — kurulu ve authenticated
- macOS veya Linux
- Python 3.12+, Node.js 18+
- Git

---

*Norosera Nöroloji Kliniği — Prof. Dr. Burhanettin Uludağ*
*UlgarTech tarafından geliştirilmiştir.*
