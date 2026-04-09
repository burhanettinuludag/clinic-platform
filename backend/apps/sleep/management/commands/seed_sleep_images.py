"""
Uyku makalelerine Unsplash'tan telif-free cover görselleri ekler.
Unsplash License: Ücretsiz, atıf gerektirmez, ticari kullanıma uygun.
"""
from django.core.management.base import BaseCommand
from apps.sleep.models import SleepArticle


# Unsplash photo URLs - 800x450 boyutunda (16:9 oran)
ARTICLE_IMAGES = {
    # Uyku Hijyeni
    'uyku-hijyeni-nedir': 'https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?w=800&h=450&fit=crop',  # peaceful bedroom
    'uyku-hijyeni-kurallari': 'https://images.unsplash.com/photo-1540518614846-7eded433c457?w=800&h=450&fit=crop',  # cozy bed
    'ideal-yatak-odasi-nasil-olmali': 'https://images.unsplash.com/photo-1616594039964-ae9021a400a0?w=800&h=450&fit=crop',  # modern bedroom
    'mavi-isik-ve-ekranlar-uyku-dusmani': 'https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=800&h=450&fit=crop',  # smartphone screen blue light
    'uyku-ve-beslenme-iliskisi': 'https://images.unsplash.com/photo-1490818387583-1baba5e638af?w=800&h=450&fit=crop',  # healthy food
    'egzersiz-ve-uyku-kalitesi': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&h=450&fit=crop',  # yoga/exercise
    'stres-kaygi-ve-uykusuzluk': 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=800&h=450&fit=crop',  # meditation

    # Uyku Sağlığı (Genel)
    'kac-saat-uyumalisiniz': 'https://images.unsplash.com/photo-1531353826977-0941b4779a1c?w=800&h=450&fit=crop',  # alarm clock bed
    'sirkadiyen-ritim-biyolojik-saat': 'https://images.unsplash.com/photo-1495364141860-b0d03eccd065?w=800&h=450&fit=crop',  # clock sunrise
    'uyku-evreleri-rem-nrem': 'https://images.unsplash.com/photo-1520206183501-b80df61043c2?w=800&h=450&fit=crop',  # sleeping peacefully
    'uyku-evreleri-ve-fizyolojisi': 'https://images.unsplash.com/photo-1520206183501-b80df61043c2?w=800&h=450&fit=crop',  # sleeping

    # Uyku Bozuklukları
    'insomnia-uykusuzluk-nedir': 'https://images.unsplash.com/photo-1515894203077-9cd36032142f?w=800&h=450&fit=crop',  # can't sleep
    'uyku-apnesi-sendromu': 'https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=800&h=450&fit=crop',  # medical/healthcare
    'uyku-apnesi-belirtileri-tedavisi': 'https://images.unsplash.com/photo-1631815588090-d4bfec5b1ccb?w=800&h=450&fit=crop',  # medical equipment
    'parasomniler': 'https://images.unsplash.com/photo-1519003300449-424ad0405076?w=800&h=450&fit=crop',  # person walking at night / sleepwalking
    'huzursuz-bacak-sendromu': 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=800&h=450&fit=crop',  # legs resting in bed

    # Tanı Yöntemleri
    'polisomnografi-uyku-testi': 'https://images.unsplash.com/photo-1551076805-e1869033e561?w=800&h=450&fit=crop',  # medical lab
    'uyku-gunlugu-nasil-tutulur': 'https://images.unsplash.com/photo-1517842645767-c639042777db?w=800&h=450&fit=crop',  # journal writing
    'uyku-testi-polisomnografi-nedir': 'https://images.unsplash.com/photo-1551076805-e1869033e561?w=800&h=450&fit=crop',  # medical lab/equipment

    # Hastalıkta Uyku
    'migrende-uyku-bozukluklari': 'https://images.unsplash.com/photo-1616012480717-fd9867059ca0?w=800&h=450&fit=crop',  # headache
    'alzheimer-hastaliginda-uyku': 'https://images.unsplash.com/photo-1559757175-5700dde675bc?w=800&h=450&fit=crop',  # elderly care
    'parkinson-hastaliginda-uyku': 'https://images.unsplash.com/photo-1559757175-5700dde675bc?w=800&h=450&fit=crop',  # elderly
    'diyabette-uyku-bozukluklari': 'https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=800&h=450&fit=crop',  # health
    'adhd-ve-uyku': 'https://images.unsplash.com/photo-1503454537195-1dcabb73ffb9?w=800&h=450&fit=crop',  # child
    'epilepside-uyku-iliskisi': 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=800&h=450&fit=crop',  # brain/neurology

    # Ek makaleler (v2)
    'uyku-teroru-gece-dehseti': 'https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?w=800&h=450&fit=crop',  # child sleeping
    'rem-uyku-davraris-bozuklugu': 'https://images.unsplash.com/photo-1520206183501-b80df61043c2?w=800&h=450&fit=crop',  # person sleeping
    'uyurgezerlik-somnambulizm': 'https://images.unsplash.com/photo-1519003300449-424ad0405076?w=800&h=450&fit=crop',  # walking at night
    'enurezis-nokturna-gece-islatmasi': 'https://images.unsplash.com/photo-1503454537195-1dcabb73ffb9?w=800&h=450&fit=crop',  # child
    'parkinson-hastaliginda-uyku-bozukluklari-detayli': 'https://images.unsplash.com/photo-1559757175-5700dde675bc?w=800&h=450&fit=crop',  # elderly care
    'gebelikte-uyku-bozukluklari': 'https://images.unsplash.com/photo-1544126592-807ade215a0b?w=800&h=450&fit=crop',  # pregnancy
}


class Command(BaseCommand):
    help = 'Uyku makalelerine Unsplash cover görselleri ekler'

    def handle(self, *args, **options):
        updated = 0
        for slug, url in ARTICLE_IMAGES.items():
            count = SleepArticle.objects.filter(slug=slug).update(cover_image_url=url)
            if count:
                updated += count

        self.stdout.write(self.style.SUCCESS(f'{updated} makaleye cover görseli eklendi.'))
