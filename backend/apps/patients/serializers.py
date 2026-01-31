from rest_framework import serializers
from .models import DiseaseModule, PatientModule, TaskTemplate, TaskCompletion


class DiseaseModuleSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = DiseaseModule
        fields = [
            'id', 'slug', 'disease_type', 'name', 'name_tr', 'name_en',
            'description', 'description_tr', 'description_en',
            'icon', 'is_active', 'order',
        ]

    def _get_lang(self):
        request = self.context.get('request')
        if request and hasattr(request, 'headers'):
            return request.headers.get('Accept-Language', 'tr')[:2]
        return 'tr'

    def get_name(self, obj):
        return getattr(obj, f'name_{self._get_lang()}', obj.name_tr)

    def get_description(self, obj):
        return getattr(obj, f'description_{self._get_lang()}', obj.description_tr)


class PatientModuleSerializer(serializers.ModelSerializer):
    disease_module_detail = DiseaseModuleSerializer(source='disease_module', read_only=True)
    disease_module = serializers.PrimaryKeyRelatedField(
        queryset=DiseaseModule.objects.filter(is_active=True)
    )

    class Meta:
        model = PatientModule
        fields = ['id', 'disease_module', 'disease_module_detail', 'enrolled_at', 'is_active']
        read_only_fields = ['enrolled_at']


class TaskTemplateSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = TaskTemplate
        fields = [
            'id', 'disease_module', 'title', 'title_tr', 'title_en',
            'description', 'description_tr', 'description_en',
            'task_type', 'frequency', 'points', 'order', 'is_active', 'metadata',
        ]

    def _get_lang(self):
        request = self.context.get('request')
        if request and hasattr(request, 'headers'):
            return request.headers.get('Accept-Language', 'tr')[:2]
        return 'tr'

    def get_title(self, obj):
        return getattr(obj, f'title_{self._get_lang()}', obj.title_tr)

    def get_description(self, obj):
        return getattr(obj, f'description_{self._get_lang()}', obj.description_tr)


class TaskCompletionSerializer(serializers.ModelSerializer):
    task_template_detail = TaskTemplateSerializer(source='task_template', read_only=True)

    class Meta:
        model = TaskCompletion
        fields = ['id', 'task_template', 'task_template_detail', 'completed_date', 'response_data', 'notes']

    def validate(self, data):
        request = self.context.get('request')
        if request and request.user:
            task = data.get('task_template')
            if task:
                enrolled = request.user.enrolled_modules.filter(
                    disease_module=task.disease_module, is_active=True
                ).exists()
                if not enrolled:
                    raise serializers.ValidationError(
                        "You are not enrolled in this module."
                    )
        return data
