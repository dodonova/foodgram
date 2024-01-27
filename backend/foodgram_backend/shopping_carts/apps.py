from django.apps import AppConfig

from foodgram_backend.translat_dict import get_name as _



class ShoppingCartsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shopping_carts'
    verbose_name = _('Shopping Carts')
