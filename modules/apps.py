from django.apps import AppConfig


class ModulesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "modules"

    def ready(self):
        from modules import policies
        from modules.views import ModuleViewSet

        for action, policy in policies.POLICIES.items():
            ModuleViewSet.policies.register(action, policy)