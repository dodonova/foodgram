from django.core.exceptions import ValidationError


def validate_subscription(value):
    if value.follower == value.following:
        raise ValidationError(_('User can not create self subscription.'))
