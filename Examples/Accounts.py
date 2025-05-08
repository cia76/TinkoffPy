import logging  # Выводим лог на консоль и в файл
from datetime import datetime  # Дата и время

from TinkoffPy import TinkoffPy  # Работа с Tinkoff Invest API из Python
from TinkoffPy.grpc.operations_pb2 import PortfolioRequest, PortfolioResponse
from TinkoffPy.grpc.orders_pb2 import GetOrdersRequest, GetOrdersResponse, OrderDirection
from TinkoffPy.grpc.stoporders_pb2 import GetStopOrdersRequest, GetStopOrdersResponse, StopOrderDirection


if __name__ == '__main__':  # Точка входа при запуске этого скрипта
    logger = logging.getLogger('TinkoffPy.Accounts')  # Будем вести лог
    tp_provider = TinkoffPy()  # Подключаемся ко всем торговым счетам

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Формат сообщения
                        datefmt='%d.%m.%Y %H:%M:%S',  # Формат даты
                        level=logging.DEBUG,  # Уровень логируемых событий NOTSET/DEBUG/INFO/WARNING/ERROR/CRITICAL
                        handlers=[logging.FileHandler('Accounts.log', encoding='utf-8'), logging.StreamHandler()])  # Лог записываем в файл и выводим на консоль
    logging.Formatter.converter = lambda *args: datetime.now(tz=tp_provider.tz_msk).timetuple()  # В логе время указываем по МСК

    for account in tp_provider.accounts:  # Пробегаемся по всем счетам
        logger.info(f'Учетная запись {account.id}')
        request = PortfolioRequest(account_id=account.id, currency=tp_provider.currency)
        response: PortfolioResponse = tp_provider.call_function(tp_provider.stub_operations.GetPortfolio, request)  # Получаем портфель по счету
        for position in response.positions:  # Пробегаемся по всем активным позициям счета
            instrument = tp_provider.figi_to_symbol_info(position.figi)  # Поиск тикера по уникальному коду
            if instrument.class_code == 'CETS':  # Валюты
                continue  # за позиции не считаем
            size = int(tp_provider.quotation_to_float(position.quantity))  # Кол-во в штуках
            entry_price = tp_provider.money_value_to_float(position.average_position_price)  # Цена входа
            last_price = tp_provider.money_value_to_float(position.current_price)  # Последняя цена
            logger.info(f'- Позиция {instrument.class_code}.{instrument.ticker} ({instrument.name}) {size} @ {entry_price} / {last_price}')
        portfolio_amount = tp_provider.money_value_to_float(response.total_amount_portfolio)  # Оценка портфеля
        currencies_amount = tp_provider.money_value_to_float(response.total_amount_currencies)  # Свободные средства
        logger.info(f'- Позиции {(portfolio_amount - currencies_amount)} + Свободные средства {currencies_amount} = {portfolio_amount}')
        request = GetOrdersRequest(account_id=account.id)
        response: GetOrdersResponse = tp_provider.call_function(tp_provider.stub_orders.GetOrders, request)  # Получаем активные заявки
        for order in response.orders:  # Пробегаемся по всем заявкам
            si = tp_provider.figi_to_symbol_info(order.figi)  # Поиск тикера по уникальному коду
            logger.info(f'- Заявка номер {order.order_id} '
                        f'{"Покупка" if order.direction == OrderDirection.ORDER_DIRECTION_BUY else "Продажа"} '
                        f'{si.class_code}.{si.ticker} {order.lots_requested * si.lot} '
                        f'@ {tp_provider.money_value_to_float(order.initial_security_price)}')
        request = GetStopOrdersRequest(account_id=account.id)
        response: GetStopOrdersResponse = tp_provider.call_function(tp_provider.stub_stop_orders.GetStopOrders, request)  # Получаем активные стоп заявки
        for stop_order in response.stop_orders:  # Пробегаемся по всем стоп заявкам
            si = tp_provider.figi_to_symbol_info(stop_order.figi)  # Поиск тикера по уникальному коду
            logger.info(f'- Стоп заявка номер {stop_order.stop_order_id} '
                        f'{"Покупка" if stop_order.direction == StopOrderDirection.STOP_ORDER_DIRECTION_BUY else "Продажа"} '
                        f'{si.class_code}.{si.ticker} {stop_order.lots_requested * si.lot} '
                        f'@ {tp_provider.money_value_to_float(stop_order.stop_price)} / {tp_provider.money_value_to_float(stop_order.price)}')

    tp_provider.close_channel()  # Закрываем канал перед выходом
