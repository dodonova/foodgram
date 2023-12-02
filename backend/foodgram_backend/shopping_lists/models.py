from django.db import models

from users.models import User
from recipes.models import Recipe


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='пользователь',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='рецепт',
        on_delete=models.CASCADE
    )
