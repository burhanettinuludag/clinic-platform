"""
PDF Report Generation for Dementia Cognitive Data.
Follows the same pattern as apps.migraine.reports.MigraineReportGenerator.
"""
import io
from datetime import timedelta
from decimal import Decimal

from django.db.models import Avg, Count, Sum
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
)

from .models import (
    ExerciseSession,
    DailyAssessment,
    CaregiverNote,
    CognitiveScore,
    CognitiveScreening,
)


class DementiaReportGenerator:
    """Demans bilissel takip raporu PDF olusturucu."""

    def __init__(self, user, start_date=None, end_date=None):
        self.user = user
        self.end_date = end_date or timezone.now().date()
        self.start_date = start_date or (self.end_date - timedelta(days=30))
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Title'],
            fontSize=22,
            spaceAfter=20,
            textColor=colors.HexColor('#1A202C'),
        ))
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2D3748'),
            spaceBefore=20,
            spaceAfter=10,
            borderPadding=(0, 0, 3, 0),
        ))
        self.styles.add(ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
        ))
        self.styles.add(ParagraphStyle(
            name='SmallText',
            parent=self.styles['Normal'],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#718096'),
        ))
        self.styles.add(ParagraphStyle(
            name='Disclaimer',
            parent=self.styles['Normal'],
            fontSize=7,
            leading=9,
            textColor=colors.HexColor('#A0AEC0'),
            spaceBefore=20,
        ))

    def generate(self):
        """PDF raporu olustur ve bytes olarak dondur."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        story = []

        # 1. Baslik ve hasta bilgileri
        story.extend(self._build_header())

        # 2. Bilissel skor ozeti
        story.extend(self._build_cognitive_scores())

        # 3. Egzersiz istatistikleri
        story.extend(self._build_exercise_stats())

        # 4. Skor trendi (son 30 gun)
        story.extend(self._build_score_trend())

        # 5. Gunluk degerlendirme ozeti
        story.extend(self._build_assessment_summary())

        # 6. Guvenlik olaylari
        story.extend(self._build_safety_incidents())

        # 7. Bakici notlari (ciddi)
        story.extend(self._build_caregiver_notes())

        # 8. Tarama sonuclari
        story.extend(self._build_screening_results())

        # 9. Tibbi feragat
        story.extend(self._build_disclaimer())

        doc.build(story)
        buffer.seek(0)
        return buffer

    def _build_header(self):
        elements = []
        elements.append(Paragraph("Bilissel Takip Raporu", self.styles['ReportTitle']))
        elements.append(Paragraph(
            f"Hasta: {self.user.first_name} {self.user.last_name}",
            self.styles['BodyText'],
        ))
        elements.append(Paragraph(
            f"E-posta: {self.user.email}",
            self.styles['BodyText'],
        ))
        elements.append(Paragraph(
            f"Rapor Tarihi: {timezone.now().strftime('%d.%m.%Y')}",
            self.styles['BodyText'],
        ))
        elements.append(Paragraph(
            f"Donem: {self.start_date.strftime('%d.%m.%Y')} - {self.end_date.strftime('%d.%m.%Y')}",
            self.styles['BodyText'],
        ))
        elements.append(Spacer(1, 12))
        return elements

    def _build_cognitive_scores(self):
        elements = []
        elements.append(Paragraph("Bilissel Skor Ozeti", self.styles['SectionHeader']))

        scores = CognitiveScore.objects.filter(
            patient=self.user,
            score_date__gte=self.start_date,
            score_date__lte=self.end_date,
        ).order_by('-score_date')

        if not scores.exists():
            elements.append(Paragraph(
                "Bu donemde bilissel skor verisi bulunmamaktadir.",
                self.styles['BodyText'],
            ))
            elements.append(Spacer(1, 10))
            return elements

        latest = scores.first()
        avg_scores = scores.aggregate(
            avg_memory=Avg('memory_score'),
            avg_attention=Avg('attention_score'),
            avg_language=Avg('language_score'),
            avg_problem=Avg('problem_solving_score'),
            avg_orientation=Avg('orientation_score'),
            avg_overall=Avg('overall_score'),
        )

        data = [
            ['Alan', 'Son Skor', 'Ortalama'],
            ['Bellek', self._fmt(latest.memory_score), self._fmt(avg_scores['avg_memory'])],
            ['Dikkat', self._fmt(latest.attention_score), self._fmt(avg_scores['avg_attention'])],
            ['Dil', self._fmt(latest.language_score), self._fmt(avg_scores['avg_language'])],
            ['Problem Cozme', self._fmt(latest.problem_solving_score), self._fmt(avg_scores['avg_problem'])],
            ['Yonelim', self._fmt(latest.orientation_score), self._fmt(avg_scores['avg_orientation'])],
            ['Genel', self._fmt(latest.overall_score), self._fmt(avg_scores['avg_overall'])],
        ]

        table = Table(data, colWidths=[6 * cm, 4 * cm, 4 * cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EDF2F7')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#2D3748')),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7FAFC')]),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 10))
        return elements

    def _build_exercise_stats(self):
        elements = []
        elements.append(Paragraph("Egzersiz Istatistikleri", self.styles['SectionHeader']))

        sessions = ExerciseSession.objects.filter(
            patient=self.user,
            started_at__date__gte=self.start_date,
            started_at__date__lte=self.end_date,
        )

        total = sessions.count()
        if total == 0:
            elements.append(Paragraph(
                "Bu donemde egzersiz verisi bulunmamaktadir.",
                self.styles['BodyText'],
            ))
            elements.append(Spacer(1, 10))
            return elements

        agg = sessions.aggregate(
            avg_score=Avg('accuracy_percent'),
            total_duration=Sum('duration_seconds'),
        )

        days_in_period = max((self.end_date - self.start_date).days, 1)
        weeks = max(days_in_period / 7, 1)
        weekly_avg = round(total / weeks, 1)
        total_minutes = round((agg['total_duration'] or 0) / 60)

        # Type distribution
        type_dist = sessions.values('exercise__exercise_type').annotate(
            count=Count('id')
        ).order_by('-count')

        # Streak (at end_date going backwards)
        streak = 0
        check = self.end_date
        while check >= self.start_date:
            has = sessions.filter(started_at__date=check).exists()
            if has:
                streak += 1
                check -= timedelta(days=1)
            else:
                break

        stats_data = [
            ['Metrik', 'Deger'],
            ['Toplam Egzersiz', str(total)],
            ['Haftalik Ortalama', str(weekly_avg)],
            ['Ortalama Basari', f"{self._fmt(agg['avg_score'])}%"],
            ['Toplam Sure', f"{total_minutes} dakika"],
            ['Mevcut Seri', f"{streak} gun"],
        ]

        table = Table(stats_data, colWidths=[7 * cm, 7 * cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EDF2F7')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E0')),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 8))

        # Type breakdown
        if type_dist:
            type_labels = {
                'memory': 'Bellek', 'attention': 'Dikkat', 'language': 'Dil',
                'problem_solving': 'Problem Cozme', 'orientation': 'Yonelim',
                'calculation': 'Hesaplama',
            }
            type_data = [['Egzersiz Tipi', 'Sayi']]
            for td in type_dist:
                label = type_labels.get(td['exercise__exercise_type'], td['exercise__exercise_type'])
                type_data.append([label, str(td['count'])])

            t2 = Table(type_data, colWidths=[7 * cm, 7 * cm])
            t2.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EDF2F7')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E0')),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(t2)

        elements.append(Spacer(1, 10))
        return elements

    def _build_score_trend(self):
        elements = []
        elements.append(Paragraph("Skor Trendi", self.styles['SectionHeader']))

        scores = CognitiveScore.objects.filter(
            patient=self.user,
            score_date__gte=self.start_date,
            score_date__lte=self.end_date,
        ).order_by('score_date')

        if not scores.exists():
            elements.append(Paragraph(
                "Bu donemde skor trendi verisi bulunmamaktadir.",
                self.styles['BodyText'],
            ))
            elements.append(Spacer(1, 10))
            return elements

        data = [['Tarih', 'Genel Skor', 'Egzersiz Sayisi']]
        for s in scores[:30]:
            data.append([
                s.score_date.strftime('%d.%m.%Y'),
                self._fmt(s.overall_score),
                str(s.exercises_completed),
            ])

        table = Table(data, colWidths=[5 * cm, 4.5 * cm, 4.5 * cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EDF2F7')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7FAFC')]),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 10))
        return elements

    def _build_assessment_summary(self):
        elements = []
        elements.append(Paragraph("Gunluk Degerlendirme Ozeti", self.styles['SectionHeader']))

        assessments = DailyAssessment.objects.filter(
            patient=self.user,
            assessment_date__gte=self.start_date,
            assessment_date__lte=self.end_date,
        )

        if not assessments.exists():
            elements.append(Paragraph(
                "Bu donemde gunluk degerlendirme verisi bulunmamaktadir.",
                self.styles['BodyText'],
            ))
            elements.append(Spacer(1, 10))
            return elements

        agg = assessments.aggregate(
            avg_mood=Avg('mood_score'),
            avg_confusion=Avg('confusion_level'),
            avg_sleep=Avg('sleep_quality'),
            avg_agitation=Avg('agitation_level'),
        )

        data = [
            ['Metrik', 'Ortalama (1-5)'],
            ['Ruh Hali', self._fmt(agg['avg_mood'])],
            ['Karisiklik Duzeyi', self._fmt(agg['avg_confusion'])],
            ['Ajitasyon Duzeyi', self._fmt(agg['avg_agitation'])],
            ['Uyku Kalitesi', self._fmt(agg['avg_sleep'])],
        ]

        table = Table(data, colWidths=[7 * cm, 7 * cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EDF2F7')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E0')),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 10))
        return elements

    def _build_safety_incidents(self):
        elements = []
        elements.append(Paragraph("Guvenlik Olaylari", self.styles['SectionHeader']))

        assessments = DailyAssessment.objects.filter(
            patient=self.user,
            assessment_date__gte=self.start_date,
            assessment_date__lte=self.end_date,
        )

        falls = assessments.filter(fall_occurred=True).count()
        wandering = assessments.filter(wandering_occurred=True).count()
        medication = assessments.filter(medication_missed=True).count()

        if falls == 0 and wandering == 0 and medication == 0:
            elements.append(Paragraph(
                "Bu donemde guvenlik olayi kaydedilmemistir.",
                self.styles['BodyText'],
            ))
        else:
            data = [
                ['Olay Tipi', 'Sayi'],
                ['Dusme', str(falls)],
                ['Kaybolma/Gezinme', str(wandering)],
                ['Ilac Atlama', str(medication)],
            ]

            table = Table(data, colWidths=[7 * cm, 7 * cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FED7D7')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#FEB2B2')),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            elements.append(table)

        elements.append(Spacer(1, 10))
        return elements

    def _build_caregiver_notes(self):
        elements = []
        elements.append(Paragraph("Onemli Bakici Notlari", self.styles['SectionHeader']))

        notes = CaregiverNote.objects.filter(
            patient=self.user,
            severity__gte=2,
            created_at__date__gte=self.start_date,
            created_at__date__lte=self.end_date,
        ).order_by('-created_at')[:10]

        if not notes.exists():
            elements.append(Paragraph(
                "Bu donemde onemli bakici notu bulunmamaktadir.",
                self.styles['BodyText'],
            ))
        else:
            data = [['Tarih', 'Tur', 'Baslik']]
            for note in notes:
                data.append([
                    note.created_at.strftime('%d.%m.%Y'),
                    note.get_note_type_display(),
                    note.title[:50],
                ])

            table = Table(data, colWidths=[3.5 * cm, 3.5 * cm, 7 * cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EDF2F7')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7FAFC')]),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            elements.append(table)

        elements.append(Spacer(1, 10))
        return elements

    def _build_screening_results(self):
        elements = []
        elements.append(Paragraph("Tarama Sonuclari", self.styles['SectionHeader']))

        screening = CognitiveScreening.objects.filter(
            patient=self.user,
        ).first()

        if not screening:
            elements.append(Paragraph(
                "Henuz bilissel tarama yapilmamistir.",
                self.styles['BodyText'],
            ))
        else:
            code, label = screening.get_interpretation()
            elements.append(Paragraph(
                f"Son Tarama Tarihi: {screening.assessment_date.strftime('%d.%m.%Y')}",
                self.styles['BodyText'],
            ))
            elements.append(Paragraph(
                f"Toplam Skor: {screening.total_score}%",
                self.styles['BodyText'],
            ))
            elements.append(Paragraph(
                f"Yorum: {label}",
                self.styles['BodyText'],
            ))

            domain_scores = screening.get_domain_scores()
            data = [['Alan', 'Skor', 'Maks']]
            for key, val in domain_scores.items():
                data.append([val['label'], str(int(val['score'])), str(val['max'])])

            table = Table(data, colWidths=[5 * cm, 4.5 * cm, 4.5 * cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EDF2F7')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E0')),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            elements.append(Spacer(1, 5))
            elements.append(table)

        elements.append(Spacer(1, 10))
        return elements

    def _build_disclaimer(self):
        elements = []
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(
            "TIBBI FERAGAT: Bu rapor bilgilendirme amaciyla olusturulmustur ve tibbi teshis "
            "veya tedavi yerine gecmez. Raporun yorumlanmasi ve tedavi kararlari icin mutlaka "
            "bir uzman hekime basvurunuz. Norosera platformu, bu rapordaki verilerin dogrulugu "
            "veya eksiksizligi konusunda garanti vermez. Rapor otomatik olarak hesaplanan "
            "verilerden olusturulmustur.",
            self.styles['Disclaimer'],
        ))
        elements.append(Paragraph(
            f"Olusturma Tarihi: {timezone.now().strftime('%d.%m.%Y %H:%M')} | Norosera Bilissel Saglik Platformu",
            self.styles['Disclaimer'],
        ))
        return elements

    @staticmethod
    def _fmt(value):
        """Format a Decimal/float value for display."""
        if value is None:
            return '-'
        if isinstance(value, Decimal):
            return str(round(float(value), 1))
        return str(round(float(value), 1))
