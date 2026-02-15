from django.core.management.base import BaseCommand
from apps.common.models import SiteConfig, FeatureFlag, SocialLink


class Command(BaseCommand):
    help = 'Varsayilan SiteConfig, FeatureFlag ve SocialLink degerlerini yukler.'

    def handle(self, *args, **options):
        # ==================
        # SiteConfig
        # ==================
        configs = [
            {
                'key': 'site_name',
                'label': 'Site Adi',
                'value': 'Norosera',
                'value_type': 'string',
                'category': 'general',
                'is_public': True,
                'description': 'Sitenin adi',
            },
            {
                'key': 'site_description',
                'label': 'Site Aciklamasi',
                'value': 'Norolojik hastaliklar icin dijital saglik platformu',
                'value_type': 'string',
                'category': 'general',
                'is_public': True,
                'description': 'Sitenin kisa aciklamasi',
            },
            {
                'key': 'contact_email',
                'label': 'Iletisim Email',
                'value': 'info@norosera.com',
                'value_type': 'string',
                'category': 'contact',
                'is_public': True,
                'description': 'Iletisim email adresi',
            },
            {
                'key': 'contact_phone',
                'label': 'Iletisim Telefon',
                'value': '',
                'value_type': 'string',
                'category': 'contact',
                'is_public': True,
                'description': 'Iletisim telefon numarasi',
            },
            {
                'key': 'contact_address',
                'label': 'Iletisim Adres',
                'value': '',
                'value_type': 'string',
                'category': 'contact',
                'is_public': True,
                'description': 'Iletisim adresi',
            },
            {
                'key': 'footer_text_tr',
                'label': 'Footer Metni (TR)',
                'value': '\u00a9 2026 Norosera. Tum haklari saklidir.',
                'value_type': 'string',
                'category': 'footer',
                'is_public': True,
                'description': 'Footer alt metin (Turkce)',
            },
            {
                'key': 'footer_text_en',
                'label': 'Footer Metni (EN)',
                'value': '\u00a9 2026 Norosera. All rights reserved.',
                'value_type': 'string',
                'category': 'footer',
                'is_public': True,
                'description': 'Footer alt metin (Ingilizce)',
            },
            {
                'key': 'google_analytics_id',
                'label': 'Google Analytics ID',
                'value': '',
                'value_type': 'string',
                'category': 'seo',
                'is_public': False,
                'description': 'GA tracking ID (G-XXXXXXXXXX)',
            },
            {
                'key': 'maintenance_mode',
                'label': 'Bakim Modu',
                'value': 'false',
                'value_type': 'boolean',
                'category': 'general',
                'is_public': True,
                'description': 'Site bakim modunda mi?',
            },
        ]

        created_configs = 0
        for cfg in configs:
            _, created = SiteConfig.objects.update_or_create(
                key=cfg['key'],
                defaults=cfg,
            )
            if created:
                created_configs += 1

        self.stdout.write(f'SiteConfig: {created_configs} yeni, {len(configs) - created_configs} guncellendi.')

        # ==================
        # FeatureFlags
        # ==================
        flags = [
            {'key': 'migraine_module', 'label': 'Migren Modulu', 'is_enabled': True, 'description': 'Migren takip modulu'},
            {'key': 'epilepsy_module', 'label': 'Epilepsi Modulu', 'is_enabled': True, 'description': 'Epilepsi takip modulu'},
            {'key': 'dementia_module', 'label': 'Demans Modulu', 'is_enabled': True, 'description': 'Demans takip modulu'},
            {'key': 'wellness_module', 'label': 'Wellness Modulu', 'is_enabled': True, 'description': 'Saglik ve wellness takibi'},
            {'key': 'store_module', 'label': 'Magaza Modulu', 'is_enabled': False, 'description': 'Urun magazasi'},
            {'key': 'payment_module', 'label': 'Odeme Modulu', 'is_enabled': False, 'description': 'Odeme sistemi'},
            {'key': 'ai_content_pipeline', 'label': 'AI Icerik Pipeline', 'is_enabled': True, 'description': 'Yapay zeka icerik uretimi'},
            {'key': 'gamification', 'label': 'Gamification', 'is_enabled': True, 'description': 'Oyunlastirma sistemi'},
            {'key': 'agent_marketing_content', 'label': 'Marketing Icerik Agent', 'is_enabled': True, 'description': 'Sosyal medya post uretimi'},
            {'key': 'agent_visual_brief', 'label': 'Gorsel Brief Agent', 'is_enabled': True, 'description': 'Tasarim brief uretimi'},
            {'key': 'agent_scheduling', 'label': 'Zamanlama Agent', 'is_enabled': True, 'description': 'Haftalik yayin plani'},
        ]

        created_flags = 0
        for flag in flags:
            _, created = FeatureFlag.objects.update_or_create(
                key=flag['key'],
                defaults=flag,
            )
            if created:
                created_flags += 1

        self.stdout.write(f'FeatureFlag: {created_flags} yeni, {len(flags) - created_flags} guncellendi.')

        # ==================
        # SocialLinks
        # ==================
        socials = [
            {'platform': 'twitter', 'url': 'https://twitter.com/norosera', 'is_active': False, 'order': 1},
            {'platform': 'linkedin', 'url': 'https://linkedin.com/company/norosera', 'is_active': False, 'order': 2},
            {'platform': 'instagram', 'url': 'https://instagram.com/norosera', 'is_active': False, 'order': 3},
            {'platform': 'youtube', 'url': 'https://youtube.com/@norosera', 'is_active': False, 'order': 4},
        ]

        created_socials = 0
        for social in socials:
            _, created = SocialLink.objects.update_or_create(
                platform=social['platform'],
                defaults=social,
            )
            if created:
                created_socials += 1

        self.stdout.write(f'SocialLink: {created_socials} yeni, {len(socials) - created_socials} guncellendi.')

        self.stdout.write(self.style.SUCCESS('Seed data basariyla yuklendi!'))
