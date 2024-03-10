import logging  # Выводим лог на консоль и в файл
from datetime import datetime  # Дата и время
from math import log10

from TinkoffPy import TinkoffPy  # Работа с Tinkoff Invest API из Python


if __name__ == '__main__':  # Точка входа при запуске этого скрипта
    logger = logging.getLogger('TinkoffPy.Ticker')  # Будем вести лог
    tp_provider = TinkoffPy()  # Подключаемся к торговому счету

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Формат сообщения
                        datefmt='%d.%m.%Y %H:%M:%S',  # Формат даты
                        level=logging.DEBUG,  # Уровень логируемых событий NOTSET/DEBUG/INFO/WARNING/ERROR/CRITICAL
                        handlers=[logging.FileHandler('Connect.log'), logging.StreamHandler()])  # Лог записываем в файл и выводим на консоль
    logging.Formatter.converter = lambda *args: datetime.now(tz=tp_provider.tz_msk).timetuple()  # В логе время указываем по МСК

    datanames = ('TQBR.SBER', 'TQBR.VTBR', 'SPBFUT.SiH4', 'SPBFUT.RIH4')  # Кортеж тикеров

    for dataname in datanames:  # Пробегаемся по всем тикерам
        class_code, security_code = tp_provider.dataname_to_class_code_symbol(dataname)  # Код режима торгов и тикер
        si = tp_provider.get_symbol_info(class_code, security_code)
        if not si:  # Если тикер не найден
            logger.warning(f'Тикер {class_code}.{security_code} не найден')
            continue  # то переходим к следующему тикеру, дальше не продолжаем
        logger.info(f'Ответ от сервера: {si}')
        logger.info(f'Информация о тикере {si.class_code}.{si.ticker} ({si.name}, {si.exchange})')
        logger.info(f'- Валюта: {si.currency}')
        logger.info(f'- Лот: {si.lot}')
        min_step = tp_provider.quotation_to_float(si.min_price_increment)  # Шаг цены
        logger.info(f'- Шаг цены: {min_step}')
        decimals = int(log10(1 / min_step) + 0.99)
        logger.info(f'- Кол-во десятичных знаков: {decimals}')

    tp_provider.close_channel()  # Закрываем канал перед выходом
