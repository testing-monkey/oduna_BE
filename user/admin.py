from django import forms
from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "last_name",
        "email",
        "upper_first_name",
        "is_active",
        "is_verified",
    )  # "show_orders")
    list_filter = (
        "created_at",
        "first_name",
    )
    search_fields = ("last_name", "first_name")
    readonly_fields = [
        "date_joined",
        "is_superuser",
        "is_staff",
        "created_at",
        "updated_at",
        "is_verified",
        "user_type",
        "email",
        "active",
        "is_active",
        "groups",
        "last_login",
    ]
    actions = [
        "activate_users",
    ]

    def activate_users(self, request, queryset):
        assert request.user.has_perm("auth.change_user") and request.user.is_superuser
        cnt = queryset.filter(is_active=False).update(is_active=True)
        self.message_user(request, "Activated {} users.".format(cnt))

    activate_users.short_description = "Activate Users"  # type: ignore

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.has_perm("auth.change_user"):
            del actions["activate_users"]
        return actions

    @admin.display(description="First Name")
    def upper_first_name(self, obj):
        return f"{obj.first_name}".upper()

    def clean_first_name(self):
        if self.cleaned_data["first_name"] == " ":
            raise forms.ValidationError("This fields must is valid")

        return self.cleaned_data["first_name"]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["first_name"].label = "First Name (e.g philip):"
        return form


models = [{"model": User, "resource": [UserAdmin]}]
# Register your models here.
for model in models:
    admin.site.register(model["model"], *model["resource"])
