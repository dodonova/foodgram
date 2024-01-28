from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import Subscription, User


class CustomUserAdmin(UserAdmin):
    model = User


admin.site.register(Subscription)
admin.site.register(User, CustomUserAdmin)
