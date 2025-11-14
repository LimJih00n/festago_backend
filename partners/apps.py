from django.apps import AppConfig


class PartnersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'partners'

    def ready(self):
        """앱 준비 완료 시 signals 등록"""
        import partners.signals  # noqa
