from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import Subscription, User


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'first_name', 'last_name',
                    'id', 'is_admin')


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following')
    list_filter = ('follower', 'following')


admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(User, CustomUserAdmin)
