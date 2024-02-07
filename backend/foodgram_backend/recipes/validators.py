from django.core.exceptions import ValidationError, BadRequest
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
    amount_num = float(amount)
    if amount_num > MAX_INGREDIENTS_AMOUNT or amount_num <= 0:
        raise BadRequest((f"ingredients amount must be "
                          f"from 0 to {MAX_INGREDIENTS_AMOUNT}"))


def validate_tags_data(request):
    tags = request.data.get('tags', [])
    if not tags:
        raise BadRequest("Tags list cannot be empty.")


def validate_ingredients_data(request):
    ingredients = request.data.get('ingredients', [])
    if not ingredients:
        raise BadRequest("Ingredients list cannot be empty.")
