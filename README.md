

# Клонировать репозиторий
```
git clone https://github.com/Edipool/chatbot_support_for_X5.git
```

# Установить зависимости
```
poetry install
```

# Активировать виртуальное окружение (если надо)
```
poetry shell
```

# Установить pre-commit хуки
```
poetry run pre-commit install
```

# Запустить проект
## Запустить lessen_1
```
python lessen_1/exercise_1.py
```
Откройте терминал и введите следующие команды:
```
curl "http://localhost:8000/factorial?number=5"
curl "http://localhost:8000/fibonacci?index=5"
curl "http://localhost:8000/mean?numbers=1,2,3,4,5"
```
