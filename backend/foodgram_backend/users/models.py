from django.contrib.auth.models import AbstractUser
from django.db import models
from foodgram_backend.settings import (EMAIL_MAX_LENGTH, LANGUAGE_CODE,
                                       NAME_MAX_LENGTH, PASSWORD_MAX_LENGTH,
                                       USERNAME_MAX_LENTH)
from foodgram_backend.translat_dict import get_name as _


class User(AbstractUser):
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='user_groups',
        verbose_name=_('groups'),
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='user_permissions',
        verbose_name=_('user permissions'),
        blank=True,
        help_text='Specific permissions for this user.',
    )
    username = models.CharField(
        max_length=USERNAME_MAX_LENTH,
        unique=True,
        blank=False
    )
    email = models.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
        blank=False
    )
    subscriptions = models.ManyToManyField(
        'self',
        through='Subscription',
        symmetrical=False,
        related_name='followings',
        verbose_name=_('subscriptions'),
        blank=True
    )
    first_name = models.CharField(max_length=USERNAME_MAX_LENTH)
    last_name = models.CharField(max_length=USERNAME_MAX_LENTH)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'password', 'first_name', 'last_name')

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return (
            self.is_staff
            or self.is_superuser
        )


class Subscription(models.Model):
    follower = models.ForeignKey(
        User,
        verbose_name=_('follower'),
        related_name='following_set',
        on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        User,
        verbose_name=_('following'),
        related_name='followers_set',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _('subscription')
        verbose_name_plural = _('Subscriptions')
