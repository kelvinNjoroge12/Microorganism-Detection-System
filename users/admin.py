from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_admin', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    list_filter = ('is_admin', 'is_staff', 'is_superuser')

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'profile_pic', 'phone')}),
        ('Permissions', {'fields': ('is_admin', 'is_staff', 'is_superuser', 'user_permissions', 'groups')}),
    )

    def get_prediction_count(self, obj):
        return obj.prediction_set.count()
    get_prediction_count.short_description = 'Predictions'

admin.site.register(User, CustomUserAdmin)

