from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from foodgram_backend.settings import MAX_INGREDIENTS_AMOUNT, MAX_PORTIONS


class ColorValidator(RegexValidator):
    regex = '^#[0-9a-fA-F]{6}$'
    message =_('Valid color should have the format #RRGGBB.')
    

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