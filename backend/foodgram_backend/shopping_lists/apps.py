from django.apps import AppConfig

from foodgram_backend.translat_dict import get_name as _



class ShoppingListsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shopping_lists'
    verbose_name = _('Shopping Lists')
