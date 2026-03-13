"""
Kirik Link Yonetim API'leri.
Admin panelden kirik linkleri listele, tara, tamir et, yok say.
"""

from rest_framework import serializers, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django.utils import timezone

from apps.accounts.permissions import IsAdminUser, IsDoctor
from apps.common.models import BrokenLink, BrokenLinkScan


# ==================== SERIALIZERS ====================

class BrokenLinkSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    link_type_display = serializers.CharField(source='get_link_type_display', read_only=True)
    source_type_display = serializers.CharField(source='get_source_type_display', read_only=True)

    class Meta:
        model = BrokenLink
        fields = [
            'id', 'broken_url', 'http_status', 'error_message',
            'link_type', 'link_type_display',
            'source_type', 'source_type_display', 'source_id', 'source_title',
            'source_field', 'source_language',
            'status', 'status_display',
            'suggested_url', 'fix_notes',
            'fixed_at', 'check_count', 'last_checked',
            'created_at',
        ]
        read_only_fields = fields


class BrokenLinkScanSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = BrokenLinkScan
        fields = [
            'id', 'status', 'status_display',
            'total_links_checked', 'broken_links_found', 'auto_fixed_count',
            'duration_seconds', 'error_message', 'details',
            'created_at',
        ]
        read_only_fields = fields


class BrokenLinkStatsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    detected = serializers.IntegerField()
    auto_fixed = serializers.IntegerField()
    manually_fixed = serializers.IntegerField()
    ai_suggested = serializers.IntegerField()
    ignored = serializers.IntegerField()
    by_type = serializers.DictField()
    by_source = serializers.DictField()
    last_scan = BrokenLinkScanSerializer(allow_null=True)


class FixBrokenLinkSerializer(serializers.Serializer):
    new_url = serializers.URLField(max_length=2000)


class BulkActionSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.UUIDField(), min_length=1, max_length=50)
    action = serializers.ChoiceField(choices=['ignore', 'recheck'])


# ==================== VIEWS ====================

class BrokenLinkListView(generics.ListAPIView):
    """
    Kirik linkleri listele.
    Filtreler: status, link_type, source_type, search
    """
    permission_classes = [IsAuthenticated, IsDoctor]
    serializer_class = BrokenLinkSerializer

    def get_queryset(self):
        qs = BrokenLink.objects.all()

        # Filtreler
        link_status = self.request.query_params.get('status')
        if link_status:
            qs = qs.filter(status=link_status)

        link_type = self.request.query_params.get('link_type')
        if link_type:
            qs = qs.filter(link_type=link_type)

        source_type = self.request.query_params.get('source_type')
        if source_type:
            qs = qs.filter(source_type=source_type)

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(broken_url__icontains=search) |
                Q(source_title__icontains=search)
            )

        return qs


class BrokenLinkStatsView(APIView):
    """Kirik link istatistikleri."""
    permission_classes = [IsAuthenticated, IsDoctor]

    def get(self, request):
        qs = BrokenLink.objects.all()

        # Status dagilimi
        status_counts = qs.values('status').annotate(count=Count('id'))
        status_map = {s['status']: s['count'] for s in status_counts}

        # Tip dagilimi
        type_counts = qs.filter(status='detected').values('link_type').annotate(count=Count('id'))
        by_type = {t['link_type']: t['count'] for t in type_counts}

        # Kaynak dagilimi
        source_counts = qs.filter(status='detected').values('source_type').annotate(count=Count('id'))
        by_source = {s['source_type']: s['count'] for s in source_counts}

        # Son tarama
        last_scan = BrokenLinkScan.objects.first()

        data = {
            'total': qs.count(),
            'detected': status_map.get('detected', 0),
            'auto_fixed': status_map.get('auto_fixed', 0),
            'manually_fixed': status_map.get('manually_fixed', 0),
            'ai_suggested': status_map.get('ai_suggested', 0),
            'ignored': status_map.get('ignored', 0),
            'by_type': by_type,
            'by_source': by_source,
            'last_scan': BrokenLinkScanSerializer(last_scan).data if last_scan else None,
        }
        return Response(data)


class BrokenLinkScanListView(generics.ListAPIView):
    """Gecmis tarama kayitlarini listele."""
    permission_classes = [IsAuthenticated, IsDoctor]
    serializer_class = BrokenLinkScanSerializer
    queryset = BrokenLinkScan.objects.all()


class TriggerScanView(APIView):
    """Elle tarama baslat."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        # Calisir durumda tarama var mi kontrol et
        running = BrokenLinkScan.objects.filter(status='running').exists()
        if running:
            return Response(
                {'error': 'Zaten devam eden bir tarama var. Lutfen tamamlanmasini bekleyin.'},
                status=status.HTTP_409_CONFLICT,
            )

        from apps.common.tasks import scan_broken_links
        task = scan_broken_links.delay()

        return Response({
            'message': 'Link taramasi baslatildi.',
            'task_id': str(task.id),
        }, status=status.HTTP_202_ACCEPTED)


class FixBrokenLinkView(APIView):
    """Tek bir kirik linki elle tamir et."""
    permission_classes = [IsAuthenticated, IsDoctor]

    def post(self, request, pk):
        try:
            bl = BrokenLink.objects.get(id=pk)
        except BrokenLink.DoesNotExist:
            return Response({'error': 'Kirik link bulunamadi.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = FixBrokenLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_url = serializer.validated_data['new_url']

        from apps.common.tasks import apply_fix_to_content
        success = apply_fix_to_content(
            bl.source_type, bl.source_id, bl.source_field,
            bl.broken_url, new_url,
        )

        if success:
            bl.status = 'manually_fixed'
            bl.suggested_url = new_url
            bl.fix_notes = f'Manuel tamir: {bl.broken_url} -> {new_url}'
            bl.fixed_at = timezone.now()
            bl.fixed_by = request.user
            bl.save()
            return Response(BrokenLinkSerializer(bl).data)
        else:
            return Response(
                {'error': 'Link icerikte bulunamadi. Icerik silinmis veya degismis olabilir.'},
                status=status.HTTP_400_BAD_REQUEST,
            )


class BulkBrokenLinkActionView(APIView):
    """Toplu islem: yok say veya tekrar kontrol et."""
    permission_classes = [IsAuthenticated, IsDoctor]

    def post(self, request):
        serializer = BulkActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ids = serializer.validated_data['ids']
        action = serializer.validated_data['action']

        links = BrokenLink.objects.filter(id__in=ids)
        count = links.count()

        if action == 'ignore':
            links.update(status='ignored', fix_notes='Admin tarafindan yok sayildi')
            return Response({'message': f'{count} link yok sayildi.', 'count': count})

        elif action == 'recheck':
            # Tekrar kontrol icin detected durumuna geri al
            links.update(status='detected', fix_notes='Tekrar kontrol icin isaretlendi')
            return Response({'message': f'{count} link tekrar kontrol icin isaretlendi.', 'count': count})

        return Response({'error': 'Gecersiz islem.'}, status=status.HTTP_400_BAD_REQUEST)


class RecheckBrokenLinkView(APIView):
    """Tek bir kirik linki tekrar kontrol et."""
    permission_classes = [IsAuthenticated, IsDoctor]

    def post(self, request, pk):
        try:
            bl = BrokenLink.objects.get(id=pk)
        except BrokenLink.DoesNotExist:
            return Response({'error': 'Kirik link bulunamadi.'}, status=status.HTTP_404_NOT_FOUND)

        from apps.common.tasks import check_url
        is_broken, http_status, error_msg = check_url(bl.broken_url)

        bl.http_status = http_status
        bl.error_message = error_msg
        bl.check_count += 1

        if not is_broken:
            bl.status = 'auto_fixed'
            bl.fix_notes = 'Tekrar kontrol: Link artik erisilebilir.'
            bl.fixed_at = timezone.now()

        bl.save()
        return Response(BrokenLinkSerializer(bl).data)
