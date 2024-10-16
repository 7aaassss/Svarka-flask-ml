# Svarrrka
Простая реализация сервиса для взаимодействия с моделью компьютерного зрения - детекция дефектов сварочных швов.

## Установка на локальном устройстве
1. Клонирование репозитория

   ```git clone https://github.com/7aaassss/pet-app```
   
2. Переход в директорию проекта

   ```cd pet-app```
   
3. Создание виртуального окружения
   
   ```python -m venv venv```
   
4. Активация виртуального окружения Windows 11
   
   ```.\venv\Scripts\Activate.ps1```
   
5. Установка зависимостей
   
   ```pip install -r requirements.txt```
   
6. Создание базы данных: установите переменные окружения которые описаны в файле .env.example
    
   ```flask db init```
   
   ```flask db migrate -m 'Initial migrate'```
   
   ```flask db upgrade```
   
7. Установка приложения
    
   ```set FLASK_APP=app.py```
   
8. Запуск приложения
    
   ```flask run```
   
9. Для перехода в приложение перейдите по пути http://127.0.0.1:5000

## Запуск на сервере
1. Клонируйте репозиторий

   ```git clone https://github.com/7aaassss/pet-app```

2. Переход в директорию проекта

   ```cd pet-app```

3. Запуск контейнера с базой данных

   ```sudo docker compose  up -d flask_db```

4. Создание таблиц и отношений

   ```flask db init```
   
   ```flask db migrate -m 'Initial migrate'```
   
   ```flask db upgrade```

5. Создание и запуск контейнера с приложением

   ```sudo docker compose build``

   ```docker compose up flask_app```

6.Если Вы запускаете приложение локально, то оно будет доступно по адресу http://127.0.0.1:8000

7. Если Вы задеплоили приложение на сервер, то оно будет доступно по адресу http://<ip-адрес сервера>:8000
! Важно открыть порт на сервере

```sudo ufw allow 5432```

```sudo ufw allow 8000```
