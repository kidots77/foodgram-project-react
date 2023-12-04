from datetime import datetime


def make_shopping_list(ingredients, recipes):
    today = datetime.today()
    return '\n'.join([
        f'Дата: {today:%Y-%m-%d}',
        'Список покупок:',
        *[
            f'{i+1}.'
            f'{ingredient["ingredient__name"].capitalize()}'
            f'({ingredient["ingredient__measurement_unit"]}) -'
            f'{ingredient["amount"]}'
            for i, ingredient in enumerate(ingredients)
        ], 'Список рецептов:', *['- ' + recipe.name for recipe in recipes]
    ])
