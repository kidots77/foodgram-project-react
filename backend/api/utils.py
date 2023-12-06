from datetime import datetime


def make_shopping_list(ingredients, recipes):
    today = datetime.today()
    return '\n'.join([
        f'Дата: {today:%Y-%m-%d}\n',
        'Список покупок:\n',
        *[
            f'{i+1}.'
            f'{ingredient["ingredient__name"].capitalize()}'
            f'({ingredient["ingredient__measurement_unit"]}) -'
            f'{ingredient["amount"]}'
            for i, ingredient in enumerate(ingredients)
        ], 'Список рецептов:\n', *f'"- "{[recipe.name for recipe in recipes]}'
    ])
