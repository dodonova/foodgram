from recipes.models import Recipe, RecipeIngredient, Ingredient, Tag, MeasurementUnit, RecipeTag
from users.models import User
from recipes.serializers import RecipeGETSerializer, RecipeCreateSerilalizer, RecipeIngredientGETSerializer

user = User(username='123', email='123@mail.fake', first_name='First', last_name='Last', password='12345', id=1)
units = MeasurementUnit(id=1, name='kg')
ing1= Ingredient(name='Water', id=1)
ing2= Ingredient(name='Salt', id=2)
tag1 = Tag(id=1, name='Tag1', slug='tag1', color='#AFFBB')
ing1.measurement_unit = units
ing2.measurement_unit = units
recipe = Recipe(id=1, name='My Recipe', text='My Text', author=user)

recipe_ing = RecipeIngredient(recipe=recipe, ingredient=ing1, amount=10)
recipe_ing2 = RecipeIngredient(recipe=recipe, ingredient=ing2, amount=10)
recipe_tag = RecipeTag(recipe=recipe, tag=tag1)

recipe_serializer = RecipeGETSerializer(recipe)
recipe_serializer.data