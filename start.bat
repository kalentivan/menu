@echo off

if exist venv\Scripts\activate.bat (
    echo [INFO] Virtual environment already exists.
) else (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        exit /b 1
    )
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo Running migrations...
python manage.py migrate

echo Loading fixtures...
python manage.py loaddata tree_menu/fixtures/menu_data.json

echo Starting server...
python manage.py runserver
