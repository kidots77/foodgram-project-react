# Foodgram 
![Main Foodgram workflow](https://github.com/kidots77/foodgram-project-react/actions/workflows/main.yml/badge.svg)
## Описание 

Проект Foodgram - это сервис для любителей готовить и/или вкусно покушать, поделиться своими рецептами и подсмотреть что-нибудь интересное у других пользователей.

## Доступный функционал 

Вы можете создавать свои рецепты блюд и просматривать рецепты других пользователей, а также добавлять понравившиеся вам рецепты в избранное и подписываться на авторов, блюда которых вам приглянулись. Также рецепты можно добавять в список покупок и получать(скачивать) список ингредиентов для приготовления того или иного блюда.

На главной странице сайта вы можете посмотреть рецепты других пользователей.

## Технологии 

- Python 3.11 

- Django 3.2 

- Django Rest Framework 3.12

- Djoser 2.1

- Python-dotenv 0.2


## Запуск проекта

- Склонируйте репозиторий: ``` git clone foodgram-project-react ```     

- Установите и активируйте виртуальное окружение: ``` python -m venv venv ``` | ``` source venv/Scripts/activate ```  

- Установите зависимости из файла requirements.txt: ``` pip install -r requirements.txt ``` 

- Перейдите в папку backend 

- Примените миграции: ``` python manage.py migrate ``` 

- Выполните команду: ``` python manage.py runserver ```

- По желанию можете воспользоваться заготовленными данными для тегов и ингредиентов с помощью команд: ``` python manage.py import_ingredients_data ``` и ``` python manage.py import_tags_data ```

- В проекте находится файл env.example с примерами данных


# Автор:  

[Михаил Волокжанин](https://github.com/kidots77) 
