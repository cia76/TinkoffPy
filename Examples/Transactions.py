import logging  # Выводим лог на консоль и в файл
from threading import Thread  # Запускаем поток подписки
from datetime import datetime  # Дата и время
from time import sleep  # Задержка в секундах перед выполнением операций
from uuid import uuid4

from TinkoffPy import TinkoffPy  # Работа с Tinkoff Invest API из Python
from TinkoffPy.grpc.marketdata_pb2 import LastPrice, MarketDataRequest, SubscribeLastPriceRequest, SubscriptionAction, LastPriceInstrument
from TinkoffPy.grpc.orders_pb2 import ORDER_DIRECTION_BUY, ORDER_DIRECTION_SELL, PostOrderRequest, ORDER_TYPE_MARKET, PostOrderResponse, ORDER_TYPE_LIMIT, CancelOrderRequest, CancelOrderResponse
from TinkoffPy.grpc.stoporders_pb2 import PostStopOrderRequest, StopOrderExpirationType, STOP_ORDER_DIRECTION_BUY, StopOrderType, PostStopOrderResponse, CancelStopOrderRequest, CancelStopOrderResponse


price: float = 0  # Последняя цена сделки по тикеру


def on_last_price(last_price: LastPrice):
    global price
    price = tp_provider.quotation_to_float(last_price.price)
    logger.info(f'Цена последней сделки по тикеру {class_code}.{security_code} = {price}')


if __name__ == '__main__':  # Точка входа при запуске этого скрипта
    logger = logging.getLogger('TinkoffPy.Transactions')  # Будем вести лог
    tp_provider = TinkoffPy()  # Подключаемся ко всем торговым счетам

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Формат сообщения
                        datefmt='%d.%m.%Y %H:%M:%S',  # Формат даты
                        level=logging.DEBUG,  # Уровень логируемых событий NOTSET/DEBUG/INFO/WARNING/ERROR/CRITICAL
                        handlers=[logging.FileHandler('Transactions.log', encoding='utf-8'), logging.StreamHandler()])  # Лог записываем в файл и выводим на консоль
    logging.Formatter.converter = lambda *args: datetime.now(tz=tp_provider.tz_msk).timetuple()  # В логе время указываем по МСК

    class_code = 'TQBR'  # Акции ММВБ
    security_code = 'SBER'  # Тикер
    # class_code = 'SPBFUT'  # Фьючерсы
    # security_code = 'SiH4'  # Формат фьючерса: <Тикер><Месяц экспирации><Последняя цифра года> Месяц экспирации: 3-H, 6-M, 9-U, 12-Z

    si = tp_provider.get_symbol_info(class_code, security_code)  # Спецификация тикера
    min_step = tp_provider.quotation_to_float(si.min_price_increment)  # Шаг цены

    # Обработчики подписок
    tp_provider.on_last_price = on_last_price  # Цена последней сделки
    tp_provider.on_portfolio = lambda portfolio: logger.info(f'Портфель - {portfolio}')  # Портфель
    tp_provider.on_position = lambda position: logger.info(f'Позиция - {position}')  # Позиции
    tp_provider.on_order_trades = lambda order_trades: logger.info(f'Сделки по заявке - {order_trades}')  # Сделки по заявке

    account_id = tp_provider.accounts[0].id  # Первый счет

    # Создание подписок
    Thread(target=tp_provider.subscriptions_marketdata_handler, name='SubscriptionsMarketdataThread').start()  # Создаем и запускаем поток обработки подписок на биржевую информацию
    tp_provider.subscription_marketdata_queue.put(  # Ставим в буфер команд подписки на биржевую информацию
        MarketDataRequest(subscribe_last_price_request=SubscribeLastPriceRequest(
            subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,  # запрос подписки
            instruments=(LastPriceInstrument(instrument_id=si.figi),))))  # на последнюю цену
    Thread(target=tp_provider.subscriptions_portfolio_handler, name='SubscriptionsPortfolioThread', args=(account_id,)).start()  # Создаем и запускаем поток обработки подписок портфеля
    Thread(target=tp_provider.subscriptions_positions_handler, name='SubscriptionsPositionsThread', args=(account_id,)).start()  # Создаем и запускаем поток обработки подписок позиций
    Thread(target=tp_provider.subscriptions_trades_handler, name='SubscriptionsTradesThread', args=(account_id,)).start()  # Создаем и запускаем поток обработки подписок сделок по заявке

    sleep(10)  # Ждем 10 секунд, чтобы пришла подписка на последнюю цену

    # Новая рыночная заявка (открытие позиции)
    # logger.info(f'Заявка {class_code}.{security_code} на покупку минимального лота по рыночной цене')
    # request = PostOrderRequest(instrument_id=si.figi, quantity=1, direction=ORDER_DIRECTION_BUY,
    #                            account_id=account_id, order_type=ORDER_TYPE_MARKET, order_id=str(uuid4()))
    # response: PostOrderResponse = tp_provider.call_function(tp_provider.stub_orders.PostOrder, request)
    # logger.debug(response)
    # logger.info(f'Номер рыночной заявки на покупку: {response.order_id}')

    # sleep(10)  # Ждем 10 секунд

    # Новая рыночная заявка (закрытие позиции)
    # logger.info(f'Заявка {class_code}.{security_code} на продажу минимального лота по рыночной цене')
    # request = PostOrderRequest(instrument_id=si.figi, quantity=1, direction=ORDER_DIRECTION_SELL,
    #                            account_id=account_id, order_type=ORDER_TYPE_MARKET, order_id=str(uuid4()))
    # response: PostOrderResponse = tp_provider.call_function(tp_provider.stub_orders.PostOrder, request)
    # logger.debug(response)
    # logger.info(f'Номер стоп заявки на покупку: {response.order_id}')

    # sleep(10)  # Ждем 10 секунд

    # Новая лимитная заявка
    tinkoff_limit_price = tp_provider.price_to_tinkoff_price(class_code, security_code, price * 0.99)  # Лимитная цена на 1% ниже последней цены сделки
    limit_price = tp_provider.float_to_quotation(tinkoff_limit_price)
    logger.info(f'Заявка {class_code}.{security_code} на покупку минимального лота по лимитной цене {tinkoff_limit_price}')
    order_id = str(uuid4())
    request = PostOrderRequest(instrument_id=si.figi, quantity=1, price=limit_price, direction=ORDER_DIRECTION_BUY,
                               account_id=account_id, order_type=ORDER_TYPE_LIMIT, order_id=order_id)
    response: PostOrderResponse = tp_provider.call_function(tp_provider.stub_orders.PostOrder, request)
    logger.debug(response)
    logger.info(f'Номер лимитной заявки на покупку: {response.order_id}')

    sleep(10)  # Ждем 10 секунд

    # Удаление существующей лимитной заявки
    logger.info(f'Удаление лимитной заявки на покупку: {response.order_id}')
    request = CancelOrderRequest(account_id=account_id, order_id=response.order_id)  # Отмена активной заявки
    response: CancelOrderResponse = tp_provider.call_function(tp_provider.stub_orders.CancelOrder, request)
    logger.info(f'Статус: {response}')

    sleep(10)  # Ждем 10 секунд

    # Новая стоп заявка
    tinkoff_stop_price = tp_provider.price_to_tinkoff_price(class_code, security_code, price * 1.01)  # Стоп цена на 1% выше последней цены сделки
    stop_price = tp_provider.float_to_quotation(tinkoff_stop_price)
    logger.info(f'Заявка {class_code}.{security_code} на покупку минимального лота по стоп цене {tinkoff_stop_price}')
    request = PostStopOrderRequest(instrument_id=si.figi, quantity=1, stop_price=stop_price, direction=STOP_ORDER_DIRECTION_BUY,
                                   account_id=account_id,
                                   expiration_type=StopOrderExpirationType.STOP_ORDER_EXPIRATION_TYPE_GOOD_TILL_CANCEL,
                                   stop_order_type=StopOrderType.STOP_ORDER_TYPE_STOP_LOSS)
    response: PostStopOrderResponse = tp_provider.call_function(tp_provider.stub_stop_orders.PostStopOrder, request)
    logger.debug(response)
    logger.info(f'Номер стоп заявки на покупку: {response.stop_order_id}')

    sleep(10)  # Ждем 10 секунд

    # Удаление существующей стоп заявки
    logger.info(f'Удаление стоп заявки на покупку: {response.stop_order_id}')
    request = CancelStopOrderRequest(account_id=account_id, stop_order_id=response.stop_order_id)  # Отмена активной стоп заявки
    response: CancelStopOrderResponse = tp_provider.call_function(tp_provider.stub_stop_orders.CancelStopOrder, request)
    logger.info(f'Статус: {response}')

    sleep(10)  # Ждем 10 секунд

    # Отмена подписок
    tp_provider.subscription_marketdata_queue.put(  # Ставим в буфер команд подписки на биржевую информацию
        MarketDataRequest(subscribe_last_price_request=SubscribeLastPriceRequest(  # запрос цены последней сделки
            subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_UNSUBSCRIBE,  # отмена подписки
            instruments=(LastPriceInstrument(instrument_id=si.figi),))))  # на тикер

    # Сброс обработчиков подписок
    tp_provider.on_last_price = tp_provider.default_handler  # Цена последней сделки
    tp_provider.on_portfolio = tp_provider.default_handler  # Портфель
    tp_provider.on_position = tp_provider.default_handler  # Позиции
    tp_provider.on_order_trades = tp_provider.default_handler  # Сделки по заявке

    # Выход
    tp_provider.close_channel()  # Закрываем канал перед выходом
