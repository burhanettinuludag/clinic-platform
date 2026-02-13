import json
import logging
from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django import forms

logger = logging.getLogger(__name__)

class PipelineForm(forms.Form):
    PIPELINE_CHOICES = [
        ('full_content_v5', 'Tam Icerik Uretimi (v5)'),
        ('news_pipeline', 'Haber Icerigi'),
        ('quality_check', 'Kalite Kontrol'),
        ('seo_optimize', 'SEO Optimizasyonu'),
    ]
    pipeline = forms.ChoiceField(choices=PIPELINE_CHOICES, label="Pipeline")
    topic = forms.CharField(max_length=300, label="Konu", help_text="Ornek: Parkinson Hastaligi")
    language = forms.ChoiceField(choices=[("tr", "Turkce"), ("en", "English")], initial="tr", label="Dil")

def pipeline_run_view(request):
    if not request.user.is_staff:
        return redirect("/admin/")
    result = None
    if request.method == "POST":
        form = PipelineForm(request.POST)
        if form.is_valid():
            import services.agents
            from services.orchestrator import orchestrator
            try:
                result = orchestrator.run_chain(
                    form.cleaned_data["pipeline"],
                    input_data={"topic": form.cleaned_data["topic"], "language": form.cleaned_data["language"], "existing_pages": [], "existing_products": []},
                    triggered_by=request.user,
                )
                if result.success:
                    messages.success(request, f"Pipeline basarili! Sure: {result.total_duration_ms}ms")
                else:
                    messages.warning(request, f"Pipeline hatali: {result.steps_failed}")
            except Exception as e:
                messages.error(request, f"Hata: {str(e)}")
    else:
        form = PipelineForm()
    return render(request, "admin/pipeline_run.html", {"form": form, "result": result, "title": "Pipeline Calistir"})
