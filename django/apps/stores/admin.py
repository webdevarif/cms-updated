from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Store, StoreAPIKey, StoreMembership, StoreRole, StoreUserRole

User = get_user_model()


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "owner", "status", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["name", "owner__email"]
    readonly_fields = ["slug", "access_code", "created_at", "updated_at"]
    prepopulated_fields = {"slug": ("name",)}

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)


@admin.register(StoreMembership)
class StoreMembershipAdmin(admin.ModelAdmin):
    list_display = ["user", "store", "role", "joined_at"]
    list_filter = ["role", "joined_at"]
    search_fields = ["user__email", "store__name"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(store__owner=request.user)


@admin.register(StoreRole)
class StoreRoleAdmin(admin.ModelAdmin):
    list_display = ["name", "store", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name", "store__name"]
    readonly_fields = ["created_at", "updated_at"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(store__owner=request.user)


@admin.register(StoreUserRole)
class StoreUserRoleAdmin(admin.ModelAdmin):
    list_display = ["user", "store", "role", "assigned_at"]
    list_filter = ["assigned_at"]
    search_fields = ["user__email", "store__name", "role__name"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(store__owner=request.user)


@admin.register(StoreAPIKey)
class StoreAPIKeyAdmin(admin.ModelAdmin):
    list_display = ["name", "store", "created", "last_used_at"]
    list_filter = ["created", "last_used_at"]
    search_fields = ["name", "store__name"]
    readonly_fields = ["created"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(store__owner=request.user)
