from django.contrib import admin

from users.models import User, Subscription

admin.site.register(Subscription)
admin.site.register(User)