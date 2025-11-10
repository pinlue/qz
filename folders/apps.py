from django.apps import AppConfig


class FoldersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "folders"

    def ready(self):
        from folders import policies
        from folders.views import FolderViewSet

        for action, policy in policies.POLICIES.items():
            FolderViewSet.policies.register(action, policy)
