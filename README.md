markdown
# Лабораторная работа №10: REST API + SPA + плановые задачи

Этот проект объединяет:
- REST API на FastAPI (in‑memory словари + PostgreSQL)
- Одностраничное приложение (SPA) на чистом JavaScript
- Плановую задачу (APScheduler) для автоматической очистки старых книг

## Функционал

### 1. Работа с книгами (PostgreSQL, лаб.4)
- Добавление, просмотр, редактирование, удаление книг
- Поиск по названию
- **Плановая задача**: каждую ночь в 3:00 удаляются книги, добавленные более 30 дней назад

### 2. Работа с фильмами (in‑memory, лаб.3)
- Добавление, просмотр, редактирование, удаление фильмов по строковому ключу
- Данные хранятся в оперативной памяти (теряются при перезапуске сервера)

### 3. SPA на чистом HTML/CSS/JS
- Две вкладки: «Книги (БД)» и «Фильмы (In‑Memory)»
- Формы добавления/редактирования
- Поиск книг
- Всплывающие уведомления

## Технологии
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, APScheduler, Uvicorn
- **Frontend**: HTML5, CSS3, Vanilla JS
- **База данных**: PostgreSQL

## Требования
- Python 3.8+
- PostgreSQL (установлен и запущен)
- Git

## Установка и запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/fukliric/10_laba_Na_Base_8.git
cd 10_laba_Na_Base_8
2. Создание и активация виртуального окружения
bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
3. Установка зависимостей
bash
pip install -r requirements.txt
4. Настройка базы данных
Создайте базу данных PostgreSQL с именем bookdb

Отредактируйте файл .env (пример ниже):

text
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=ваш_пароль
DB_NAME=bookdb
5. Запуск бэкенда (FastAPI)
bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
API будет доступно: http://localhost:8000
Документация: http://localhost:8000/docs

6. Запуск фронтенда (SPA)
В отдельном терминале выполните:

bash
python -m http.server 8080
Откройте в браузере: http://localhost:8080

Плановые задачи
Задача cleanup_old_books запускается каждый день в 3:00.

Удаляет книги, у которых created_at старше 30 дней.

Логи выводятся в консоль сервера.

Для тестирования измените интервал в файле scheduler.py (например, timedelta(minutes=1) и CronTrigger на IntervalTrigger(seconds=30)).

Структура проекта
text
10_laba_Na_Base_8/
├── main.py              # FastAPI + lifespan + планировщик
├── database.py          # Подключение к PostgreSQL
├── models.py            # ORM модель BookDB (с полем created_at)
├── schemas.py           # Pydantic схемы
├── crud.py              # CRUD операции
├── scheduler.py         # Планировщик APScheduler
├── .env                 # Переменные окружения (не публикуется)
├── requirements.txt     # Зависимости
├── index.html           # SPA фронтенд
├── .gitignore
└── README.md
Возможные проблемы и решения
Ошибка 500 / столбец books.created_at не существует
Выполните SQL-запрос: ALTER TABLE books ADD COLUMN created_at TIMESTAMP;

Или удалите таблицу и перезапустите сервер (данные будут потеряны).

ModuleNotFoundError: No module named 'apscheduler'
Активируйте виртуальное окружение и выполните pip install apscheduler.