from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram_backend.settings import (
    USERNAME_MAX_LENTH,
    EMAIL_MAX_LENGTH,
    PASSWORD_MAX_LENGTH
)


class User(AbstractUser):
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='user_groups',
        verbose_name='группы',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='user_permissions',
        verbose_name='разрешения пользователя',
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
    password = models.CharField(
        max_length=PASSWORD_MAX_LENGTH,
        blank=False
    )
    subscriptions = models.ManyToManyField(
        'self',
        through='Subscription',
        symmetrical=False,
        related_name='followings',
        verbose_name='подписки',
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'password', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

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
        verbose_name='кто подписан',
        related_name='following_set',
        on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        User,
        verbose_name='на кого подписан',
        related_name='followers_set',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
