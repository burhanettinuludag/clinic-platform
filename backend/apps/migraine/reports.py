"""
PDF Report Generation for Migraine Data
"""
import io
from datetime import datetime, timedelta
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak
)
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart


class MigraineReportGenerator:
    """Migren raporu PDF oluşturucu"""

    def __init__(self, user, start_date=None, end_date=None):
        self.user = user
        self.end_date = end_date or timezone.now().date()
        self.start_date = start_date or (self.end_date - timedelta(days=30))
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Özel stiller oluştur"""
        self.styles.add(ParagraphStyle(
            name='TurkishTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
        ))
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#4A5568'),
            spaceBefore=20,
            spaceAfter=10,
        ))
        self.styles.add(ParagraphStyle(
            name='BodyTurkish',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
        ))

    def generate(self):
        """PDF raporu oluştur ve bytes olarak döndür"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        story = []

        # Başlık
        story.append(Paragraph("Migren Takip Raporu", self.styles['TurkishTitle']))
        story.append(Paragraph(
            f"Hasta: {self.user.first_name} {self.user.last_name}",
            self.styles['BodyTurkish']
        ))
        story.append(Paragraph(
            f"Rapor Tarihi: {timezone.now().strftime('%d.%m.%Y')}",
            self.styles['BodyTurkish']
        ))
        story.append(Paragraph(
            f"Dönem: {self.start_date.strftime('%d.%m.%Y')} - {self.end_date.strftime('%d.%m.%Y')}",
            self.styles['BodyTurkish']
        ))
        story.append(Spacer(1, 20))

        # İstatistikler
        story.extend(self._build_statistics_section())

        # Atak listesi
        story.extend(self._build_attacks_section())

        # Tetikleyici analizi
        story.extend(self._build_triggers_section())

        # Öneriler
        story.extend(self._build_recommendations_section())

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def _get_attacks(self):
        """Dönem içindeki atakları getir"""
        from .models import MigraineAttack
        return MigraineAttack.objects.filter(
            patient=self.user,
            start_datetime__date__gte=self.start_date,
            start_datetime__date__lte=self.end_date
        ).order_by('-start_datetime')

    def _build_statistics_section(self):
        """İstatistik bölümü"""
        attacks = self._get_attacks()
        elements = []

        elements.append(Paragraph("Özet İstatistikler", self.styles['SectionHeader']))

        total_attacks = attacks.count()
        avg_intensity = attacks.aggregate(
            avg=models.Avg('intensity')
        )['avg'] or 0
        avg_duration = attacks.exclude(
            duration_minutes__isnull=True
        ).aggregate(
            avg=models.Avg('duration_minutes')
        )['avg'] or 0

        aura_count = attacks.filter(has_aura=True).count()
        aura_percentage = (aura_count / total_attacks * 100) if total_attacks > 0 else 0

        # İstatistik tablosu
        data = [
            ['Metrik', 'Değer'],
            ['Toplam Atak Sayısı', str(total_attacks)],
            ['Ortalama Şiddet', f'{avg_intensity:.1f} / 10'],
            ['Ortalama Süre', f'{avg_duration:.0f} dakika'],
            ['Aura Oranı', f'%{aura_percentage:.1f}'],
        ]

        table = Table(data, colWidths=[8*cm, 6*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4A5568')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F7FAFC')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7FAFC')]),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 20))

        return elements

    def _build_attacks_section(self):
        """Atak listesi bölümü"""
        attacks = self._get_attacks()[:20]  # Son 20 atak
        elements = []

        elements.append(Paragraph("Son Ataklar", self.styles['SectionHeader']))

        if not attacks:
            elements.append(Paragraph(
                "Bu dönemde kayıtlı atak bulunmamaktadır.",
                self.styles['BodyTurkish']
            ))
            return elements

        data = [['Tarih', 'Şiddet', 'Süre', 'Lokasyon', 'Aura']]

        location_map = {
            'left': 'Sol',
            'right': 'Sağ',
            'bilateral': 'İki Taraflı',
            'frontal': 'Ön',
            'occipital': 'Arka',
            'other': 'Diğer',
        }

        for attack in attacks:
            duration = f"{attack.duration_minutes} dk" if attack.duration_minutes else "-"
            location = location_map.get(attack.pain_location, attack.pain_location)
            aura = "Evet" if attack.has_aura else "Hayır"

            data.append([
                attack.start_datetime.strftime('%d.%m.%Y %H:%M'),
                f'{attack.intensity}/10',
                duration,
                location,
                aura,
            ])

        table = Table(data, colWidths=[4*cm, 2*cm, 2.5*cm, 3*cm, 2*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E53E3E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FFF5F5')]),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 20))

        return elements

    def _build_triggers_section(self):
        """Tetikleyici analizi bölümü"""
        from django.db.models import Count
        attacks = self._get_attacks()
        elements = []

        elements.append(Paragraph("Tetikleyici Analizi", self.styles['SectionHeader']))

        # En sık tetikleyiciler
        trigger_counts = attacks.values(
            'triggers_identified__name_tr'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        if not trigger_counts or not trigger_counts[0].get('triggers_identified__name_tr'):
            elements.append(Paragraph(
                "Yeterli tetikleyici verisi bulunmamaktadır.",
                self.styles['BodyTurkish']
            ))
            return elements

        data = [['Tetikleyici', 'Atak Sayısı']]
        for tc in trigger_counts:
            if tc.get('triggers_identified__name_tr'):
                data.append([tc['triggers_identified__name_tr'], str(tc['count'])])

        if len(data) > 1:
            table = Table(data, colWidths=[10*cm, 4*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#DD6B20')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FFFAF0')]),
            ]))
            elements.append(table)

        elements.append(Spacer(1, 20))
        return elements

    def _build_recommendations_section(self):
        """Öneriler bölümü"""
        elements = []
        elements.append(Paragraph("Öneriler", self.styles['SectionHeader']))

        recommendations = [
            "Bu raporu doktorunuzla paylaşarak tedavi planınızı gözden geçirebilirsiniz.",
            "Tetikleyicilerinizi takip etmeye devam edin.",
            "Düzenli uyku ve su tüketimi migren sıklığını azaltabilir.",
            "Stres yönetimi teknikleri (nefes egzersizleri, meditasyon) faydalı olabilir.",
        ]

        for rec in recommendations:
            elements.append(Paragraph(f"• {rec}", self.styles['BodyTurkish']))
            elements.append(Spacer(1, 5))

        elements.append(Spacer(1, 30))
        elements.append(Paragraph(
            "Bu rapor bilgilendirme amaçlıdır ve tıbbi tavsiye niteliği taşımaz.",
            ParagraphStyle(
                name='Disclaimer',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.gray,
            )
        ))

        return elements


# Import için gerekli
from django.db import models
