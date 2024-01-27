from foodgram_backend.settings import LANGUAGE_CODE


def get_name(name, language=LANGUAGE_CODE):
    if name in TRANSLATE:
        if language in TRANSLATE[name]:
            return TRANSLATE[name][language]
    return name


TRANSLATE = {
    'Name': {
        'ru': 'Название'
    },
    'name': {
        'ru': 'название'
    },
    'Slug': {
        'ru': 'Слаг'
    },
    'Color': {
        'ru': 'Цвет'
    },
    'tag': {
        'ru': 'тег'
    },
    'Tags': {
        'ru': 'Теги'
    },
    'measurement unit': {
        'ru': 'ед. измерения'
    },
    'Measurement Unit': {
        'ru': 'Единица измерения'
    },
    'Measurement Units': {
        'ru': 'Единицы измерения'
    },
    'ingredient': {
        'ru': 'ингредиент'
    },
    'Ingredient': {
        'ru': 'Ингредиент'
    },
    'Ingredients': {
        'ru': 'Ингредиенты'
    },
    'author': {
        'ru': 'автор'
    },
    'Cooking time': {
        'ru': 'Время приготовления, мин'
    },
    'image': {
        'ru': 'изображение'
    },
    'Text': {
        'ru': 'Текст'
    },
    'publication date': {
        'ru': 'дата публикации'
    },
    'portions': {
        'ru': 'порции'
    },
    'recipe': {
        'ru': 'рецепт'
    },
    'Recipes': {
        'ru': 'Рецепты'
    },
    'amount': {
        'ru': 'количество'
    },
    'Amount': {
        'ru': 'Количество'
    },
    'Favorites': {
        'ru': 'Избранные'
    },
    'favorite': {
        'ru': 'избранное'
    },
    'groups': {
        'ru': 'группы'
    },
    'user permissions': {
        'ru': 'разрешения пользователя'
    },
    'subscriptions': {
        'ru': 'подписки'
    },
    'user': {
        'ru': 'пользователь'
    },
    'Users': {
        'ru': 'Пользователи'
    },
    'follower': {
        'ru': 'кто подписан'
    },
    'following': {
        'ru': 'на кого подписан'
    },
    'subscription': {
        'ru': 'подписка'
    },
    'Subscriptions': {
        'ru': 'Подписки'
    },
    'shopping cart': {
        'ru': 'список покупок'
    },
    'Shopping Carts': {
        'ru': 'Списки покупок'
    },
}