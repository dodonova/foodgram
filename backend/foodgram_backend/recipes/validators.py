from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from foodgram_backend.settings import (
    MAX_PORTIONS,
    MAX_INGREDIENTS_AMOUNT
)


def validate_portions(portions):
    if portions > MAX_PORTIONS:
        raise ValidationError(
            _(f"%(portion)s must be from 1 to {MAX_PORTIONS}"),
            params={"portions": portions},
        )


def validate_ingredients_amount(amount):
     if amount > MAX_INGREDIENTS_AMOUNT or amount <= 0:
        raise ValidationError(
            _(f"ingredients amount must be from 0 to {MAX_INGREDIENTS_AMOUNT}"),
            params={"amount": amount},
        )
