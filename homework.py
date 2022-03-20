import logging
import os
import time
from pathlib import Path

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


class ServiceError(Exception):
    """Ошибка отсутствия доступа по заданному эндпойнту."""


class NetworkError(Exception):
    """Ошибка отсутствия сети."""


class EndpointError(Exception):
    """Ошибка, если эндпойнт не корректен."""


class MessageSendingError(Exception):
    """Ошибка отправки сообщения."""


class GlobalsError(Exception):
    """Ошибка, если есть пустые глобальные переменные."""


class DataTypeError(Exception):
    """Ошибка, если тип данных не dict."""


CONNECTION_ERROR = '{error}, {url}, {headers}, {params}'
SERVICE_REJECTION = '{code},'
WRONG_ENDPOINT = '{response_status}, {url}, {headers}, {params}'
WRONG_HOMEWORK_STATUS = '{}'
WRONG_DATA_TYPE = 'Неверный тип данных {type}, вместо "dict".'
HOMEWORK_STATUS = '{}'
STATUS_IS_CHANGED = '{verdict}, {homework}'
STATUS_IS_NOT_CHANGED = 'Статус не изменился, нет записей.'
FAILURE_TO_SEND_MESSAGE = '{error}, {message}'
GLOBAL_VARIABLE_IS_MISSING = 'Отсутствует глобальная переменная {}'
GLOBAL_VARIABLE_IS_EMPTY = 'Пустая глобальная переменная {}'
MESSAGE_IS_SENT = 'Сообщение {} отправлено'

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправляет сообщение пользователю в Телегу."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as error:
        raise MessageSendingError(FAILURE_TO_SEND_MESSAGE.format(
            error=error,
            message=message,
        ))
    else:
        logging.info(f'Message \'{message}\' is sent')


def get_api_answer(current_timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    all_params = dict(url=ENDPOINT, headers=headers, params=params)
    try:
        response = requests.get(**all_params)
    except telegram.error.TelegramError as error:
        raise telegram.TelegramError(CONNECTION_ERROR.format(
            error=error,
            **all_params,
        ))
    response_status = response.status_code
    if response_status != 200:
        raise EndpointError(WRONG_ENDPOINT.format(
            response_status=response_status,
            **all_params,
        ))
    return response.json()


def check_response(response):
    """
    Возвращает домашку, если есть.
    Проверяет валидность её статуса.
    """
    try:
        return response['homeworks'][0]
    except 'code' in response:
        raise ServiceError(SERVICE_REJECTION.format(
            code=response.get('code'),
        ))


def parse_status(homework):
    """Возвращает текст сообщения от ревьюера."""
    data_type = type(homework)
    if data_type != dict:
        raise DataTypeError(WRONG_DATA_TYPE.format(data_type))
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')

    if homework_status not in HOMEWORK_STATUSES:
        raise NameError(WRONG_HOMEWORK_STATUS.format(homework_status))

    verdict = HOMEWORK_STATUSES[homework_status]

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения."""
    for key in (
        'PRACTICUM_TOKEN',
        'TELEGRAM_TOKEN',
        'TELEGRAM_CHAT_ID',
        'ENDPOINT'
    ):
        if globals()[key] is None:
            logging.error(GLOBAL_VARIABLE_IS_MISSING.format(key))
            return False
        elif not globals()[key]:
            logging.error(GLOBAL_VARIABLE_IS_EMPTY.format(key))
            return False
    return True


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        raise GlobalsError('Ошибка глобальной переменной. Смотрите логи.')
    check_tokens()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            message = parse_status(homework)
            send_message(bot, message)
            print(response)
            current_timestamp = response.get('current_date')
            time.sleep(RETRY_TIME)

        except IndexError:
            message = 'Статус работы не изменился'
            send_message(bot, message)
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            time.sleep(RETRY_TIME)
        else:
            logging.info(MESSAGE_IS_SENT.format(message))


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s, %(message)s, %(lineno)d, %(name)s',
        filemode='w',
        filename=f'{Path(__file__).stem}.log',
        level=logging.INFO,
    )
    main()
