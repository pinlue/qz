from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        import users.signals # noqa

        from users import policies
        from users.views import UserViewSet

        for action, policy in policies.POLICIES.items():
            UserViewSet.policies.register(action, policy)
