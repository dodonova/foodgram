# from django.db import models

# from foodgram_backend.settings import (
#     LANGUAGE_CODE,
# )
# from foodgram_backend.translat_dict import get_name as _
# from recipes.models import Recipe
# from users.models import User


# class ShoppingList(models.Model):
#     user = models.ForeignKey(
#         User,
#         verbose_name=_('user'),
#         on_delete=models.CASCADE
#     )
#     recipe = models.ForeignKey(
#         Recipe,
#         verbose_name=_('recipe'),
#         on_delete=models.CASCADE
#     )

#     class Meta:
#         verbose_name = _('shopping list'),
#         verbose_name_plural = _('Shopping Lists')