# Бот - ассистент

[![Python](https://img.shields.io/badge/-Python-464641?style=flat-square&logo=Python)](https://www.python.org/)
[![pytest](https://img.shields.io/badge/-pytest-464646?style=flat-square&logo=pytest)](https://docs.pytest.org/en/6.2.x/)

Яндекс Практикум. Спринт 7. Итоговый проект. Деплой бота - ассистента.

## Описание

Телеграм - бот обращается к API сервису Практикум.Домашка и узнаёт статус домашней работы: взята ли домашняя работа в ревью, проверена ли она, а если проверена — то принял её ревьюер или вернул на доработку.

Пример ответа бота - ассистента:

```python
{
   "homeworks":[
      {
         "id":123,
         "status":"approved",
         "homework_name":"egorcoders__homework_bot-master.zip",
         "reviewer_comment":"Всё нравится",
         "date_updated":"2021-12-14T14:40:57Z",
         "lesson_name":"Итоговый проект"
      }
   ],
   "current_date":1581804979
}
```

## Установка

Клонировать репозиторий:

```python
git clone https://github.com/egorcoders/homework_bot.git
```

Перейти в папку с проектом:

```python
cd homework_bot/
```

Установить виртуальное окружение для проекта:

```python
python -m venv venv
```

Активировать виртуальное окружение для проекта:

```python
# для OS Lunix и MacOS
source venv/bin/activate

# для OS Windows
source venv/Scripts/activate
```

Установить зависимости:

```python
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

Выполнить миграции на уровне проекта:

```python
cd yatube
python3 manage.py makemigrations
python3 manage.py migrate
```

Зарегистрировать чат-бота в Телеграм

Создать в корневой директории файл .env для хранения переменных окружения

```python
PRAKTIKUM_TOKEN = 'xxx'
TELEGRAM_TOKEN = 'xxx'
TELEGRAM_CHAT_ID = 'xxx'
```

Запустить проект локально:

```python
# для OS Lunix и MacOS
python homework_bot.py

# для OS Windows
python3 homework_bot.py
```
