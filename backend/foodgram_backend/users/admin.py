from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


from users.models import User, Subscription


# Добавили CustomUserAdmin  чтобы пароль в админ-зоне
# можно было сбросить через специальную форму

class CustomUserAdmin(UserAdmin):
    model = User

admin.site.register(Subscription)
admin.site.register(User, CustomUserAdmin)
