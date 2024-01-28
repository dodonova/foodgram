from django.apps import AppConfig
from foodgram_backend.translat_dict import get_name as _


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = _('Users')
