from django.apps import AppConfig


class IntegrationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "integration"

    def ready(self):
        import integration.signals  # noqa

        from integration import policies
        from integration.views import DeepLApiKeyViewSet

        for action, policy in policies.POLICIES.items():
            DeepLApiKeyViewSet.policies.register(action, policy)
