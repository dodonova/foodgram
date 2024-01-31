from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from foodgram_backend.settings import (MAX_COOKING_TIME,
                                       MAX_INGREDIENTS_AMOUNT, MAX_PORTIONS)


class ColorValidator(RegexValidator):
    regex = '^#[0-9a-fA-F]{6}$'
    message = ('Valid color should have the format #RRGGBB.')


def validate_portions(portions):
    if portions > MAX_PORTIONS:
        raise ValidationError(
            _(f"%(portion)s must be from 1 to {MAX_PORTIONS}"),
            params={"portions": portions},
        )


def validate_cooking_time(cooking_time):
    if cooking_time < 1 or cooking_time > MAX_COOKING_TIME:
        raise ValidationError(
            _(f"%Cooking_time must be from 1 to {MAX_COOKING_TIME}"),
            params={"cooking_time": cooking_time},
        )


def validate_ingredients_amount(amount):
    if amount > MAX_INGREDIENTS_AMOUNT or amount <= 0:
        raise ValidationError(
            _((f"ingredients amount must be "
               f"from 0 to {MAX_INGREDIENTS_AMOUNT}")),
            params={"amount": amount},
        )

def validate_recipe_data(request):
    ingredients = request.data.get('ingredients', [])
    tags = request.data.get('tags', [])
    if not ingredients or not tags:
        return False
    return True
