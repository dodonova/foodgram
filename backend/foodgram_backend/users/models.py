from django.contrib.auth.models import AbstractUser
from django.db import models


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
    
    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


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
