# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import User
from .forms import CustomUserChangeForm, CustomUserCreationForm

from tastypie.admin import ApiKeyInline
from tastypie.models import ApiAccess, ApiKey

#admin.site.register(ApiKey)
#admin.site.register(ApiAccess)

class CustomUserAdmin(UserAdmin):

    add_form_template = 'admin/auth/user/add_form.html'
    change_user_password_template = None
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('full_name', 'email', 'message')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login',)}),
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
    ordering = ('username','created','last_login')
    filter_horizontal = ('groups', 'user_permissions',)

    inlines = UserAdmin.inlines + [ApiKeyInline]

admin.site.register(User, CustomUserAdmin)
