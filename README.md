# Telegram-бот

Простой Telegram-бот-викторина на Python.
Бот помогает пользователю пройти короткий тест и узнать своё тотемное животное из Московского зоопарка.

## Что умеет бот

* запускается командой `/start`;
* проводит пользователя через викторину;
* показывает результат по ответам пользователя;
* рассказывает о программе опеки Московского зоопарка;
* предлагает пройти викторину заново;
* позволяет оставить отзыв;
* даёт возможность связаться с сотрудником.

## Технологии

* Python 3
* aiogram 3
* python-dotenv

## Настройка

Создайте файл `.env` или передайте переменные окружения:

```env
TOKEN=ваш_токен_бота
ADMIN_CHAT_ID=ваш_telegram_id
```

## Установка и запуск

```bash
git clone [<ссылка_на_репозиторий>](https://github.com/SFsolovev/chatbot_HW)
cd tgbot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install aiogram python-dotenv
python bot.py
```

## Проверка работы
t.me/MoscowZoo_HW_bot

## Структура проекта

```text
tgbot/
├── bot.py
├── config.py
├── requirements.txt
└── README.md
```
