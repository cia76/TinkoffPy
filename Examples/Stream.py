import logging  # Выводим лог на консоль и в файл
from threading import Thread  # Запускаем поток подписки
from datetime import datetime  # Дата и время
from time import sleep  # Подписка на события по времени

from TinkoffPy import TinkoffPy  # Работа с Tinkoff Invest API из Python
from TinkoffPy.grpc.marketdata_pb2 import MarketDataRequest, SubscribeOrderBookRequest, SubscriptionAction, \
    OrderBookInstrument, SubscribeLastPriceRequest, LastPriceInstrument, GetOrderBookRequest, GetOrderBookResponse, \
    GetLastPricesRequest, GetLastPricesResponse


if __name__ == '__main__':  # Точка входа при запуске этого скрипта
    logger = logging.getLogger('TinkoffPy.Transactions')  # Будем вести лог
    tp_provider = TinkoffPy()  # Подключаемся ко всем торговым счетам

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Формат сообщения
                        datefmt='%d.%m.%Y %H:%M:%S',  # Формат даты
                        level=logging.DEBUG,  # Уровень логируемых событий NOTSET/DEBUG/INFO/WARNING/ERROR/CRITICAL
                        handlers=[logging.FileHandler('Stream.log'), logging.StreamHandler()])  # Лог записываем в файл и выводим на консоль
    logging.Formatter.converter = lambda *args: datetime.now(tz=tp_provider.tz_msk).timetuple()  # В логе время указываем по МСК

    class_code = 'TQBR'  # Акции ММВБ
    security_code = 'SBER'  # Тикер
    # class_code = 'SPBFUT'  # Фьючерсы
    # security_code = 'SiH4'  # Формат фьючерса: <Тикер><Месяц экспирации><Последняя цифра года> Месяц экспирации: 3-H, 6-M, 9-U, 12-Z

    Thread(target=tp_provider.subscriptions_marketdata_handler, name='SubscriptionsMarketdataThread').start()  # Создаем и запускаем поток обработки подписок на биржевую информацию
    si = tp_provider.get_symbol_info(class_code, security_code)  # Спецификация тикера

    # Стакан
    logger.info(f'Текущий стакан {class_code}.{security_code}')
    order_book: GetOrderBookResponse = tp_provider.call_function(tp_provider.stub_marketdata.GetOrderBook, GetOrderBookRequest(depth=10, instrument_id=si.figi))  # Запрос стакана
    logger.debug(order_book)
    logger.info(f'bids от {tp_provider.quotation_to_float(order_book.bids[0].price)} до {tp_provider.quotation_to_float(order_book.bids[-1].price)}, '
                f'asks от {tp_provider.quotation_to_float(order_book.asks[0].price)} до {tp_provider.quotation_to_float(order_book.asks[-1].price)}')

    sleep_secs = 5  # Кол-во секунд получения стакана
    logger.info(f'{sleep_secs} секунд стакана {class_code}.{security_code}')
    # noinspection PyShadowingNames
    tp_provider.on_orderbook = lambda order_book: logger.info(
        f'ask = {tp_provider.quotation_to_float(order_book.asks[0].price)} '
        f'bid = {tp_provider.quotation_to_float(order_book.bids[0].price)}')  # Обработчик события прихода подписки на стакан
    tp_provider.subscription_marketdata_queue.put(  # Ставим в буфер команд подписки на биржевую информацию
        MarketDataRequest(subscribe_order_book_request=SubscribeOrderBookRequest(
            subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,  # запрос подписки
            instruments=(OrderBookInstrument(depth=10, instrument_id=si.figi),))))  # с глубиной стакана 10
    logger.info(f'Подписка на стакан {class_code}.{security_code} создана')
    sleep(sleep_secs)  # Ждем кол-во секунд получения стакана
    tp_provider.subscription_marketdata_queue.put(  # Ставим в буфер команд подписки на биржевую информацию
        MarketDataRequest(subscribe_order_book_request=SubscribeOrderBookRequest(
            subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_UNSUBSCRIBE,  # запрос отмены подписки
            instruments=(OrderBookInstrument(depth=10, instrument_id=si.figi),))))  # с глубиной стакана 10
    logger.info(f'Подписка на стакан {class_code}.{security_code} отменена')  # Отписываеся от стакана
    tp_provider.on_orderbook = tp_provider.default_handler  # Возвращаем обработчик по умолчанию

    # Котировки
    logger.info(f'Текущие котировки {class_code}.{security_code}')
    quotes: GetLastPricesResponse = tp_provider.call_function(tp_provider.stub_marketdata.GetLastPrices, GetLastPricesRequest(instrument_id=[si.figi]))  # Запрос последних цен
    logger.debug(quotes)
    logger.info(f'Последняя цена сделки: {tp_provider.quotation_to_float(quotes.last_prices[-1].price)}')

    sleep_secs = 5  # Кол-во секунд получения котировок
    logger.info(f'{sleep_secs} секунд котировок {class_code}.{security_code}')
    tp_provider.on_last_price = lambda last_price: logger.info(f'Цена последней сделки по тикеру {class_code}.{security_code} = {tp_provider.quotation_to_float(last_price.price)}')  # Цена последней сделки
    tp_provider.subscription_marketdata_queue.put(  # Ставим в буфер команд подписки на биржевую информацию
        MarketDataRequest(subscribe_last_price_request=SubscribeLastPriceRequest(
            subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,  # запрос подписки
            instruments=(LastPriceInstrument(instrument_id=si.figi),))))  # на последнюю цену
    logger.info(f'Подписка на котировки {class_code}.{security_code} создана')
    sleep(sleep_secs)  # Ждем кол-во секунд получения обезличенных сделок
    tp_provider.subscription_marketdata_queue.put(  # Ставим в буфер команд подписки на биржевую информацию
        MarketDataRequest(subscribe_last_price_request=SubscribeLastPriceRequest(
            subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_UNSUBSCRIBE,  # запрос отмены подписки
            instruments=(LastPriceInstrument(instrument_id=si.figi),))))  # на последнюю цену
    logger.info(f'Подписка на котировки {class_code}.{security_code} отменена')  # Отписываеся от котировок
    tp_provider.on_last_price = tp_provider.default_handler  # Возвращаем обработчик по умолчанию

    # Выход
    tp_provider.close_channel()  # Закрываем канал перед выходом
