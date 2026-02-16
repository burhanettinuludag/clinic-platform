"""
Seed social media data for development/testing.

Usage: python manage.py seed_social
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.social.models import SocialAccount, SocialCampaign, SocialPost, PublishLog

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed social media test data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding social media data...')

        # Get or create doctor user
        doctor = User.objects.filter(role='doctor').first()
        if not doctor:
            doctor = User.objects.filter(is_superuser=True).first()
        if not doctor:
            self.stdout.write(self.style.ERROR('No doctor or superuser found. Create one first.'))
            return

        # 1. Social Accounts
        ig_account, _ = SocialAccount.objects.get_or_create(
            platform='instagram',
            account_id='norosera_ig_001',
            defaults={
                'account_name': 'norosera.clinic',
                'access_token': 'demo_token_instagram',
                'token_expires_at': timezone.now() + timedelta(days=55),
                'page_id': '123456789',
                'status': 'active',
                'connected_by': doctor,
                'followers_count': 4500,
                'total_posts_published': 120,
            },
        )

        li_account, _ = SocialAccount.objects.get_or_create(
            platform='linkedin',
            account_id='norosera_li_001',
            defaults={
                'account_name': 'Norosera Klinik',
                'access_token': 'demo_token_linkedin',
                'token_expires_at': timezone.now() + timedelta(days=45),
                'organization_urn': 'urn:li:organization:98765',
                'status': 'active',
                'connected_by': doctor,
                'followers_count': 1200,
                'total_posts_published': 45,
            },
        )

        self.stdout.write(f'  Accounts: {ig_account.account_name}, {li_account.account_name}')

        # 2. Campaigns
        campaign1, created1 = SocialCampaign.objects.get_or_create(
            title='Migren Farkindalik Haftasi',
            defaults={
                'theme': 'Migren tetikleyicileri ve onleme yontemleri',
                'description': 'Haftalik migren bilinclendirme kampanyasi',
                'platforms': ['instagram', 'linkedin'],
                'posts_per_platform': 3,
                'language': 'tr',
                'tone': 'educational',
                'target_audience': 'patients',
                'week_start': timezone.now().date() + timedelta(days=7),
                'status': 'review',
                'created_by': doctor,
                'total_tokens': 4500,
                'content_output': {
                    'instagram_posts': [
                        {'text': 'Migren tetikleyicileri arasinda stres, uyku bozuklugu ve beslenme duzensizligi yer alir.', 'hashtags': ['#migren', '#norosera', '#saglik'], 'suggested_format': 'carousel'},
                        {'text': 'Duzensiz uyku migren ataklarini tetikleyebilir. Her gece ayni saatte yatmaya ozen gosterin.', 'hashtags': ['#uyku', '#migren', '#saglikliYasam'], 'suggested_format': 'single'},
                        {'text': 'Migren gunlugu tutmak, tetikleyicilerinizi tanimlamaniza yardimci olur.', 'hashtags': ['#migrenGunlugu', '#norosera'], 'suggested_format': 'single'},
                    ],
                    'linkedin_posts': [
                        {'text_tr': 'Migren, dunya genelinde 1 milyardan fazla insani etkileyen norolojik bir hastaliktir.', 'text_en': 'Migraine affects over 1 billion people worldwide.', 'hashtags': ['#migraine', '#neurology', '#healthcare']},
                        {'text_tr': 'Isyerinde migren yonetimi: calisanlarin %40\'i migren nedeniyle uretkenlik kaybi yasadiklarini bildiriyor.', 'hashtags': ['#migraine', '#workplace', '#health']},
                    ],
                },
            },
        )

        campaign2, created2 = SocialCampaign.objects.get_or_create(
            title='Noroloji Ipuclari',
            defaults={
                'theme': 'Beyin sagligi icin gunluk ipuclari',
                'platforms': ['instagram'],
                'posts_per_platform': 5,
                'language': 'tr',
                'tone': 'motivational',
                'target_audience': 'general',
                'week_start': timezone.now().date() + timedelta(days=14),
                'status': 'draft',
                'created_by': doctor,
            },
        )

        self.stdout.write(f'  Campaigns: {campaign1.title}, {campaign2.title}')

        # 3. Posts
        now = timezone.now()
        posts_data = [
            # Published posts
            {'campaign': campaign1, 'platform': 'instagram', 'post_format': 'carousel', 'caption_tr': 'Migren tetikleyicileri: stres, uyku bozuklugu, beslenme duzensizligi.', 'hashtags': ['#migren', '#norosera', '#saglik'], 'status': 'published', 'social_account': ig_account, 'published_at': now - timedelta(days=3), 'scheduled_at': now - timedelta(days=3), 'platform_post_id': 'ig_post_001', 'platform_url': 'https://www.instagram.com/p/demo1/'},
            {'campaign': campaign1, 'platform': 'linkedin', 'post_format': 'single_image', 'caption_tr': 'Migren 1 milyardan fazla insani etkiliyor.', 'hashtags': ['#migraine', '#neurology'], 'status': 'published', 'social_account': li_account, 'published_at': now - timedelta(days=2), 'scheduled_at': now - timedelta(days=2), 'platform_post_id': 'li_post_001', 'platform_url': 'https://www.linkedin.com/feed/update/demo1/'},

            # Review posts
            {'campaign': campaign1, 'platform': 'instagram', 'post_format': 'single_image', 'caption_tr': 'Duzensiz uyku migren ataklarini tetikleyebilir.', 'hashtags': ['#uyku', '#migren'], 'status': 'review', 'scheduled_at': now + timedelta(days=1)},
            {'campaign': campaign1, 'platform': 'instagram', 'post_format': 'single_image', 'caption_tr': 'Migren gunlugu tutmak tetikleyicilerinizi tanimlamaya yardimci olur.', 'hashtags': ['#migrenGunlugu'], 'status': 'review', 'scheduled_at': now + timedelta(days=2)},
            {'campaign': campaign1, 'platform': 'linkedin', 'post_format': 'text_only', 'caption_tr': 'Isyerinde migren yonetimi hakkinda.', 'hashtags': ['#workplace', '#health'], 'status': 'review', 'scheduled_at': now + timedelta(days=3)},

            # Scheduled posts
            {'campaign': campaign1, 'platform': 'instagram', 'post_format': 'carousel', 'caption_tr': 'Besin alerjileri ve migren baglantisi.', 'hashtags': ['#beslenme', '#migren'], 'status': 'scheduled', 'social_account': ig_account, 'scheduled_at': now + timedelta(days=5)},

            # Failed post
            {'campaign': campaign1, 'platform': 'instagram', 'post_format': 'single_image', 'caption_tr': 'Mevsim degisiklikleri ve migren.', 'status': 'failed', 'social_account': ig_account, 'publish_error': 'Token expired', 'scheduled_at': now - timedelta(hours=6)},
        ]

        post_count = 0
        for pd in posts_data:
            _, created = SocialPost.objects.get_or_create(
                caption_tr=pd['caption_tr'],
                defaults={
                    **{k: v for k, v in pd.items() if k != 'caption_tr'},
                    'created_by': doctor,
                    'ai_generated': True,
                },
            )
            if created:
                post_count += 1

        self.stdout.write(f'  Posts: {post_count} created')

        # 4. Publish Logs
        published_posts = SocialPost.objects.filter(status='published')
        for pp in published_posts:
            PublishLog.objects.get_or_create(
                post=pp,
                action='publish',
                defaults={
                    'success': True,
                    'response_data': {'status_code': 200, 'post_id': pp.platform_post_id},
                },
            )

        failed_posts = SocialPost.objects.filter(status='failed')
        for fp in failed_posts:
            PublishLog.objects.get_or_create(
                post=fp,
                action='publish',
                defaults={
                    'success': False,
                    'error_message': fp.publish_error,
                },
            )

        self.stdout.write(self.style.SUCCESS('Social media seed data created successfully!'))
        self.stdout.write(f'  Summary: {SocialAccount.objects.count()} accounts, {SocialCampaign.objects.count()} campaigns, {SocialPost.objects.count()} posts')
