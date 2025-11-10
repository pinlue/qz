from django.apps import AppConfig


class CardsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cards"

    def ready(self):
        from cards import policies
        from cards.views import CardViewSet

        for action, policy in policies.POLICIES.items():
            CardViewSet.policies.register(action, policy)
