"""
Admin configuration pour le modèle User
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserRole


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Configuration admin pour le modèle User personnalisé"""
    list_display = ('email', 'role', 'is_active', 'is_staff', 'date_joined', 'last_login')
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('email',)
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_active', 'is_staff'),
        }),
    )
    
    filter_horizontal = ('groups', 'user_permissions',)
