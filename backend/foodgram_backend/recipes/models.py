from django.db import models

from users.models import User
from foodgram_backend.settings import (
    NAME_MAX_LENGTH,
    SLUG_MAX_LENGHT,
    DISPLAY_TEXT_MAX_LENGTH,
)
from recipes.validators import (
    validate_portions,
    validate_ingredients_amount
)


class SlugNameModel(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=NAME_MAX_LENGTH,
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True,
        max_length=SLUG_MAX_LENGHT,
    )

    class Meta:
        ordering = ('name', )
        abstract = True

    def __str__(self):
        return self.name[:DISPLAY_TEXT_MAX_LENGTH]


class Tag(SlugNameModel):
    color = models.SlugField(
        verbose_name='Цвет',
    )

    class Meta(SlugNameModel.Meta):
        verbose_name = 'тег',
        verbose_name_plural = 'Теги'


class MeasurementUnit(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=NAME_MAX_LENGTH,
        unique=True,
    )

    class Meta:
        verbose_name = 'единица измерения',
        verbose_name_plural = 'Единицы измерения'

    def __str__(self):
        return self.name[:DISPLAY_TEXT_MAX_LENGTH]


class Ingredient(SlugNameModel):
    default_measurement_unit = models.ForeignKey(
        MeasurementUnit,
        verbose_name='ед.измерения',
        blank=True,
        null=True,
        default=None,
        on_delete=models.SET_DEFAULT,
    )

    class Meta(SlugNameModel.Meta):
        verbose_name = 'ингредиент',
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name='название'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name="Время приготовления, мин"
    )
    # image = models.ImageField(
    #     upload_to='recipe_images/',
    #     verbose_name='изображение',
    #     null=True,
    #     default=None,
    # )
    text = models.TextField(
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        verbose_name='дата публикации',
        auto_now_add=True,
        db_index=True
    )
    portions = models.PositiveIntegerField(
        verbose_name='порции',
        validators=[validate_portions],
        default=1,
        blank=True,
    )

    class Meta:
        verbose_name = 'рецепт',
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name[:DISPLAY_TEXT_MAX_LENGTH]


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='ингредиент',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='рецепт',
        on_delete=models.CASCADE
    )
    amount = models.FloatField(
        verbose_name='количество',
        validators=[validate_ingredients_amount],
    )
    measurement_unit = models.ForeignKey(
        MeasurementUnit,
        verbose_name='ед.измерения',
        on_delete=models.SET_DEFAULT,
        blank=True,
        null=True,
        default=None
    )

    def save(self, *args, **kwargs):
        if not self.measurement_unit and self.ingredient.default_measurement_unit:
            self.measurement_unit = self.ingredient.default_measurement_unit
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'[:DISPLAY_TEXT_MAX_LENGTH]


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE
    )


class Favorites(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'избранное',
        verbose_name_plural = 'Избранные'
