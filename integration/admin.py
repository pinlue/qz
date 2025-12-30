from django import forms
from django.contrib import admin

from integration.models import DeepLApiKey


class DeepLApiKeyForm(forms.ModelForm):
    new_api_key = forms.CharField(
        label="Set new API Key",
        required=False,
        widget=forms.PasswordInput(render_value=True),
        help_text="Enter a new API key to replace the current one."
    )

    class Meta:
        model = DeepLApiKey
        fields = "__all__"

    def save(self, commit=True):
        instance = super().save(commit=False)
        new_key = self.cleaned_data.get("new_api_key")
        if new_key:
            instance.api_key = new_key
        if commit:
            instance.save()
        return instance


@admin.register(DeepLApiKey)
class DeepLApiKeyAdmin(admin.ModelAdmin):
    form = DeepLApiKeyForm

    list_display = ("user", "status", "api_key_display")
    list_filter = ("status",)
    search_fields = ("user__username", "user__email")
    readonly_fields = ("api_key_display",)

    def api_key_display(self, obj):
        try:
            return obj.api_key
        except Exception:
            return "Invalid / not set"
    api_key_display.short_description = "API Key"
