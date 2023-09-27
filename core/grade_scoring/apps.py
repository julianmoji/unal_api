from django.apps import AppConfig


class GradeScoringConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core.grade_scoring"

    def ready(self):
        from core.grade_scoring import signals
