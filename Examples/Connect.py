import logging  # Выводим лог на консоль и в файл
from threading import Thread  # Запускаем поток подписки
from datetime import datetime, UTC

from TinkoffPy import TinkoffPy  # Работа с Tinkoff Invest API из Python
from TinkoffPy.grpc.marketdata_pb2 import MarketDataRequest, SubscribeCandlesRequest, SubscriptionAction, CandleInstrument, SubscriptionInterval


if __name__ == '__main__':  # Точка входа при запуске этого скрипта
    logger = logging.getLogger('TinkoffPy.Connect')  # Будем вести лог
    tp_provider = TinkoffPy()  # Подключаемся ко всем торговым счетам
    # tp_provider = TinkoffPy(demo=True)  # Подключаемся к демо счетам

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Формат сообщения
                        datefmt='%d.%m.%Y %H:%M:%S',  # Формат даты
                        level=logging.DEBUG,  # Уровень логируемых событий NOTSET/DEBUG/INFO/WARNING/ERROR/CRITICAL
                        handlers=[logging.FileHandler('Connect.log'), logging.StreamHandler()])  # Лог записываем в файл и выводим на консоль
    logging.Formatter.converter = lambda *args: datetime.now(tz=tp_provider.tz_msk).timetuple()  # В логе время указываем по МСК

    class_code = 'TQBR'  # Акции ММВБ
    security_code = 'SBER'  # Тикер
    # class_code = 'SPBFUT'  # Фьючерсы
    # security_code = 'SiU4'  # Формат фьючерса: <Тикер><Месяц экспирации><Последняя цифра года> Месяц экспирации: 3-H, 6-M, 9-U, 12-Z

    # Проверяем работу запрос/ответ
    logger.info(f'Данные тикера {class_code}.{security_code}')  # Время на сервере приходит в подписках. Поэтому, запросим данные тикера
    si = tp_provider.get_symbol_info(class_code, security_code)  # Спецификация тикера
    logger.info(f'Ответ от сервера: {si}' if si else f'Тикер {class_code}.{security_code} не найден')

    # Проверяем работу подписок
    tp_provider.on_candle = lambda candle: logger.info(f'{class_code}.{security_code} (M1) - '
                                                       f'{tp_provider.utc_to_msk_datetime(datetime.fromtimestamp(candle.time.seconds, UTC))} - '
                                                       f'Open = {tp_provider.quotation_to_float(candle.open)}, '
                                                       f'High = {tp_provider.quotation_to_float(candle.high)}, '
                                                       f'Low = {tp_provider.quotation_to_float(candle.low)}, '
                                                       f'Close = {tp_provider.quotation_to_float(candle.close)}, '
                                                       f'Volume = {int(candle.volume)}')  # Обработчик новых баров по подписке из Тинькофф
    Thread(target=tp_provider.subscriptions_marketdata_handler, name='SubscriptionsMarketdataThread').start()  # Создаем и запускаем поток обработки подписок сделок по заявке
    tp_provider.subscription_marketdata_queue.put(  # Ставим в буфер команд подписки на биржевую информацию
        MarketDataRequest(subscribe_candles_request=SubscribeCandlesRequest(  # запрос на новые бары
            subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,  # подписка
            instruments=(CandleInstrument(interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE, instrument_id=si.figi),),  # на тикер по временному интервалу 1 минута
            waiting_close=True)))  # по закрытию бара
    logger.info(f'Тикер {class_code}.{security_code} подписан на новые бары на временнОм интервале 1 минута')

    # Выход
    input('Enter - выход\n')
    tp_provider.close_channel()  # Закрываем канал перед выходом
