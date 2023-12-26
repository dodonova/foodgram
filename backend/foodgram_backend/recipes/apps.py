from django.apps import AppConfig

from foodgram_backend.translat_dict import get_name as _


class RecipesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipes'
    verbose_name = _('Recipes')
