from django.db import models
from foodgram_backend.settings import (DISPLAY_TEXT_MAX_LENGTH,
                                       NAME_MAX_LENGTH, SLUG_MAX_LENGHT)
from foodgram_backend.translat_dict import get_name as _
from users.models import User

from recipes.validators import (ColorValidator, validate_cooking_time,
                                validate_ingredients_amount, validate_portions)


class Tag(models.Model):
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=NAME_MAX_LENGTH,
    )
    slug = models.SlugField(
        verbose_name=_('Slug'),
        unique=True,
        max_length=SLUG_MAX_LENGHT,
    )
    color = models.CharField(
        verbose_name=_('Color'),
        max_length=16,
        validators=[ColorValidator()]
    )

    class Meta:
        verbose_name = _('tag')
        verbose_name_plural = _('Tags')
        ordering = ('name', )

    def __str__(self):
        return self.name[:DISPLAY_TEXT_MAX_LENGTH]


class MeasurementUnit(models.Model):
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=NAME_MAX_LENGTH,
        unique=True,
    )

    class Meta:
        verbose_name = _('measurement unit'),
        verbose_name_plural = _('Measurement Units')
        ordering = ('name', )

    def __str__(self):
        return self.name[:DISPLAY_TEXT_MAX_LENGTH]


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=NAME_MAX_LENGTH,
    )
    measurement_unit = models.ForeignKey(
        MeasurementUnit,
        related_name='measurement_unit',
        verbose_name=_('measurement unit'),
        blank=True, null=True, default=None,
        on_delete=models.SET_DEFAULT,
    )

    class Meta:
        verbose_name = _('ingredient'),
        verbose_name_plural = _('Ingredients')
        ordering = ('name', )

    def __str__(self):
        return self.name[:DISPLAY_TEXT_MAX_LENGTH]


class Recipe(models.Model):
    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name=_('name')
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name=_('author'), related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag, through='RecipeTag',
        verbose_name=_('Tag'), related_name='tags'
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient',
        verbose_name=_('Ingredient')
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name=_('Cooking time'),
        validators=[validate_cooking_time]
    )
    image = models.ImageField(
        upload_to='recipe_images/',
        verbose_name=_('image'),
        null=True, default=None,
    )
    text = models.TextField(
        verbose_name=_('Text')
    )
    pub_date = models.DateTimeField(
        verbose_name=_('publication date'),
        auto_now_add=True, db_index=True
    )
    portions = models.PositiveIntegerField(
        verbose_name=_('portions'),
        validators=[validate_portions],
        default=1, blank=True,
    )

    class Meta:
        verbose_name = _('recipe'),
        verbose_name_plural = _('Recipes')
        ordering = ('-pub_date', )

    def __str__(self):
        return self.name[:DISPLAY_TEXT_MAX_LENGTH]


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name=_('ingredient'),
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name=_('recipe'),
        related_name='recipe_ingredients',
        on_delete=models.CASCADE
    )
    amount = models.FloatField(
        verbose_name=_('amount'),
        validators=[validate_ingredients_amount],
    )
    measurement_unit = models.ForeignKey(
        MeasurementUnit,
        verbose_name=_('measurement unit'),
        related_name='recipe_ingredients',
        on_delete=models.SET_DEFAULT,
        blank=True, null=True, default=None
    )

    class Meta:
        unique_together = ('ingredient', 'recipe')

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'[:DISPLAY_TEXT_MAX_LENGTH]

    def save(self, *args, **kwargs):
        if not self.measurement_unit:
            self.measurement_unit = self.ingredient.measurement_unit
        super().save(*args, **kwargs)


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.recipe} {self.tag}'[:DISPLAY_TEXT_MAX_LENGTH]


class Favorites(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('favorite'),
        verbose_name_plural = _('Favorites')


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, verbose_name=_('user'),
                             on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, verbose_name=_('recipe'),
                               on_delete=models.CASCADE,
                               related_name='recipes')

    class Meta:
        verbose_name = _('shopping cart'),
        verbose_name_plural = _('Shopping Carts')
