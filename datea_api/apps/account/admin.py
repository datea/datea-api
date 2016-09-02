# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from account.models import User, ClientDomain
from account.forms import CustomUserChangeForm, CustomUserCreationForm

from tastypie.admin import ApiKeyInline
from tastypie.models import ApiAccess, ApiKey

admin.site.unregister(ApiKey)
admin.site.register(ApiKey)
#admin.site.unregister(ApiAccess)
admin.site.register(ApiAccess)

class CustomUserAdmin(UserAdmin):

    add_form_template = 'admin/auth/user/add_form.html'
    change_user_password_template = None
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('full_name', 'email', 'message', 'image', 'bg_image')}),
        ('Permissions', {'fields': ('status', 'is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2')}
        ),
    )
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = ('username', 'email', 'full_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'full_name', 'email')
    ordering = ('-created','username','email', 'full_name', 'last_login')
    filter_horizontal = ('groups', 'user_permissions',)
    list_display = ('username', 'full_name', 'email', 'created', 'last_login')

    inlines = UserAdmin.inlines + [ApiKeyInline]

admin.site.register(User, CustomUserAdmin)


class DomainAdmin(admin.ModelAdmin):
    pass

admin.site.register(ClientDomain, DomainAdmin)
