from datetime import datetime


def make_shopping_list(ingredients, recipes):
    today = datetime.today()
    shopping_list = [
        f'Дата: {today:%Y-%m-%d}',
        'Закупочный список:',
        *[
            f'{i+1}.'
            f'{ingredient["ingredient__name"].capitalize()}'
            f'({ingredient["ingredient__measurement_unit"]}) -'
            f'{ingredient["amount"]}'
            for i, ingredient in enumerate(ingredients)
        ], 'Список рецептов:', *['- ' + recipe.name for recipe in recipes]
    ]
    return '\n'.join(shopping_list)
