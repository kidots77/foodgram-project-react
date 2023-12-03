from datetime import datetime


def send_message(ingredients, recipes):
    today = datetime.today()
    shopping_list = (
        f'Дата: {today:%Y-%m-%d}\n\n'
    )
    for index, ingredient in enumerate(ingredients, start=1):
        formatted_ingredient_name = ingredient["ingredient__name"].capitalize()
        shopping_list += (
            f'{index}. {formatted_ingredient_name} '
            f'({ingredient["ingredient__measurement_unit"]})'
            f' - {ingredient["amount"]}\n'
        )

    shopping_list += '\nСписок рецептов:\n'
    for recipe in recipes:
        shopping_list += f'- {recipe.name}\n'

    return shopping_list
