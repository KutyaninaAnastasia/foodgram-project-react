# Foodgram - Продуктовый помощник

![example workflow](https://github.com/KutyaninaAnastasia/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)  

## Описание проекта
«Продуктовый помощник»(Foodgram) это проект, где пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов.
 
Сервис «Список покупок» позволяет пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд.
Пользователь может скачать список и получить файл с суммированным перечнем и количеством необходимых ингредиентов для всех рецептов, сохранённых в «Списке покупок».

Проект доступен по ссылке: [Продуктовый помощник](http://51.250.103.170)

## Запуск проекта с помощью Docker

* Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/KutyaninaAnastasia/foodgram-project-react.git
cd foodgram-project-react
```

* Cоздать и активировать виртуальное окружение:

```
python -m venv env
source env/bin/activate
```

* Cоздать в директории `/infra/` файл .env(шаблон заполнения):

```
SECRET_KEY=секретный ключ django
(Чтобы получить- ввести:  python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())' )
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

* Запустите docker compose:
```
docker-compose up -d --build
```  

* Выполнить по очереди команды:
```
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py load_ingredients
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic --no-input 
```
*Чтобы остановить контенеры, выполнить команду:
```
docker-compose down -v
```

