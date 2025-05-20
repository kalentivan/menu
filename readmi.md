# Меню

# Команды
```shell
python -m venv venv 
```
```shell
venv/scripts/activate 
```
```shell
pip install -r requirements.txt
``` 
```shell
python manage.py migrate 
```
```shell
python manage.py loaddata tree_menu/fixtures/menu_data.json 
```
```shell
python manage.py runserver
```

# Для запуска
1. Создать БД для работы
2. Прописать в .env
3. Выполнить установку.

* SECRET_KEY=""
* DB_NAME=""
* DB_USER=""
* DB_PASSWORD=""
* DB_HOST=""
* DB_PORT=""