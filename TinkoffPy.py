from typing import Union  # Объединение типов
from datetime import datetime, timedelta
from time import sleep
from queue import SimpleQueue  # Очередь подписок/отписок
import logging

from google.protobuf.timestamp_pb2 import Timestamp

from TinkoffPy.grpc import common_pb2
from TinkoffPy.grpc import users_pb2  # Структуры сервиса счетов https://russianinvestments.github.io/investAPI/users/
from TinkoffPy.grpc.users_pb2_grpc import UsersServiceStub  # Методы сервиса счетов
from TinkoffPy.grpc import instruments_pb2  # Структуры сервиса инструментов https://russianinvestments.github.io/investAPI/instruments/
from TinkoffPy.grpc.instruments_pb2_grpc import InstrumentsServiceStub  # Методы сервиса инструментов
from TinkoffPy.grpc import orders_pb2  # Структуры сервиса ордеров https://russianinvestments.github.io/investAPI/orders/
from TinkoffPy.grpc.orders_pb2_grpc import OrdersServiceStub, OrdersStreamServiceStub  # Методы сервиса ордеров. Поток сделок и поручений пользователя
from TinkoffPy.grpc import operations_pb2  # Структуры сервиса операций https://russianinvestments.github.io/investAPI/operations/
from TinkoffPy.grpc.operations_pb2_grpc import OperationsServiceStub, OperationsStreamServiceStub  # Методы сервиса операций. Поток операций
from TinkoffPy.grpc import marketdata_pb2  # Структуры сервиса котировок https://russianinvestments.github.io/investAPI/marketdata/
from TinkoffPy.grpc.marketdata_pb2_grpc import MarketDataServiceStub, MarketDataStreamServiceStub  # Методы сервиса котировок. Поток котировок
from TinkoffPy.grpc.stoporders_pb2_grpc import StopOrdersServiceStub  # Методы сервиса стоп-ордеров https://russianinvestments.github.io/investAPI/stoporders/

from pytz import timezone, utc  # Работаем с временнОй зоной и UTC
from grpc import ssl_channel_credentials, secure_channel, RpcError, StatusCode  # Защищенный канал

from TinkoffPy import Config  # Файл конфигурации


# noinspection PyProtectedMember
class TinkoffPy:
    """Работа с Tinkoff Invest API https://russianinvestments.github.io/investAPI/ из Python
    Генерация кода в папку grpc осуществлена из proto контрактов: https://github.com/RussianInvestments/investAPI/tree/main/src/docs/contracts
    """
    tz_msk = timezone('Europe/Moscow')  # Время UTC будем приводить к московскому времени
    server = 'invest-public-api.tinkoff.ru:443'  # Торговый сервер
    server_demo = 'sandbox-invest-public-api.tinkoff.ru:443'  # Демо сервер (песочница)
    currency: operations_pb2.PortfolioRequest.CurrencyRequest = operations_pb2.PortfolioRequest.CurrencyRequest.RUB  # Суммы будем получать в российских рублях
    logger = logging.getLogger('TinkoffPy')  # Будем вести лог

    def __init__(self, token=Config.token, demo=False):
        """Инициализация

        :param str token: Токен
        """
        self.metadata = (('authorization', f'Bearer {token}'),)  # Токен доступа
        self.channel = secure_channel(self.server_demo if demo else self.server, ssl_channel_credentials())  # Защищенный канал

        # Сервисы запросов
        self.stub_users = UsersServiceStub(self.channel)  # Счета
        self.stub_instruments = InstrumentsServiceStub(self.channel)  # Инструменты
        self.stub_marketdata = MarketDataServiceStub(self.channel)  # Биржевая информация
        self.stub_operations = OperationsServiceStub(self.channel)  # Операции
        self.stub_orders = OrdersServiceStub(self.channel)  # Заявки
        self.stub_stop_orders = StopOrdersServiceStub(self.channel)  # Стоп заявки

        # Сервисы подписок, буферы команд, потоки обработки, события
        self.stub_marketdata_stream = MarketDataStreamServiceStub(self.channel)  # Биржевая информация
        self.subscription_marketdata_queue: SimpleQueue[marketdata_pb2.MarketDataRequest] = SimpleQueue()  # Буфер команд
        self.marketdata_thread = None  # Поток обработки событий
        self.on_candle = self.default_handler  # Свеча
        self.on_trade = self.default_handler  # Сделки
        self.on_orderbook = self.default_handler  # Стакан
        self.on_trading_status = self.default_handler  # Торговый статус
        self.on_last_price = self.default_handler  # Цена последней сделки

        self.stub_operations_stream = OperationsStreamServiceStub(self.channel)  # Операции
        self.portfolio_thread = None  # Поток обработки событий портфеля
        self.position_thread = None  # Поток обработки событий позиций
        self.on_portfolio = self.default_handler  # Портфель
        self.on_position = self.default_handler  # Позиция

        self.stub_orders_stream = OrdersStreamServiceStub(self.channel)  # Заявки и сделки
        self.orders_thread = None  # Поток обработки событий
        self.on_order_trades = self.default_handler  # Сделки по заявке

        self.time_delta = timedelta(seconds=3)  # Разница между локальным временем и временем торгового сервера с учетом временнОй зоны
        response: users_pb2.GetAccountsResponse = self.call_function(self.stub_users.GetAccounts, users_pb2.GetAccountsRequest())  # Запрос всех счетов
        self.accounts = [account for account in response.accounts if account.closed_date.seconds == 0]  # Все незакрытые счета
        self.symbols: dict[tuple[str, str], instruments_pb2.Instrument] = {}  # Информация о тикерах

    # Запросы

    def call_function(self, func, request):
        """Вызов функции"""
        while True:  # Пока не получим ответ или ошибку
            try:  # Пытаемся
                response, call = func.with_call(request=request, metadata=self.metadata)  # вызвать функцию
                # self.logger.debug(f'Запрос: {request} Ответ: {response}')  # Для отладки работоспособности сервера Тинькофф Инвестиции
                return response  # и вернуть ответ
            except RpcError as ex:  # Если получили ошибку канала
                func_name = func._method.decode('utf-8')  # Название функции
                details = ex.args[0].details  # Сообщение об ошибке
                if ex.args[0].code == StatusCode.RESOURCE_EXHAUSTED:  # Превышено кол-во запросов в минуту
                    sleep_seconds = 60 - datetime.now().second + self.time_delta.total_seconds()  # Время в секундах до начала следующей минуты с учетом разницы локального времени и времени торгового сервера
                    self.logger.warning(f'Превышение кол-ва запросов в минуту при вызове функции {func_name} с параметрами {request}Запрос повторится через {sleep_seconds} с')
                    sleep(sleep_seconds)  # Ждем
                else:  # В остальных случаях
                    self.logger.error(f'Ошибка {details} при вызове функции {func_name} с параметрами {request}')
                    return None  # Возвращаем пустое значение

    # Подписки

    def default_handler(self, event: Union[
        marketdata_pb2.Candle, marketdata_pb2.Trade, marketdata_pb2.OrderBook, marketdata_pb2.TradingStatus,
        marketdata_pb2.LastPrice, operations_pb2.PortfolioResponse, operations_pb2.PositionData, orders_pb2.OrderTrades
    ]):
        """Пустой обработчик события по умолчанию. Его можно заменить на пользовательский"""
        pass

    def request_marketdata_iterator(self):
        """Генератор запросов на подписку/отписку биржевой информации"""
        while True:  # Будем пытаться читать из очереди до закрытия канала
            yield self.subscription_marketdata_queue.get()  # Возврат из этой функции. При повторном ее вызове исполнение продолжится с этой строки

    def subscriptions_marketdata_handler(self):
        """Поток обработки подписок на биржевую информацию. Список подписок на клиенте"""
        events = self.stub_marketdata_stream.MarketDataStream(request_iterator=self.request_marketdata_iterator(), metadata=self.metadata)  # Получаем значения подписок
        try:
            for event in events:  # Пробегаемся по значениям подписок до закрытия канала
                e: marketdata_pb2.MarketDataResponse = event  # Приводим пришедшее значение к подписке
                if e.candle != marketdata_pb2.Candle():  # Свеча
                    self.logger.debug(f'subscriptions_marketdata_handler: Пришел бар {e.candle}')
                    self.on_candle(e.candle)
                if e.trade != marketdata_pb2.Trade():  # Сделки
                    self.logger.debug(f'subscriptions_marketdata_handler: Пришла сделка {e.trade}')
                    self.on_trade(e.trade)
                if e.orderbook != marketdata_pb2.OrderBook():  # Стакан
                    self.logger.debug(f'subscriptions_marketdata_handler: Пришел стакан {e.orderbook}')
                    self.on_orderbook(e.orderbook)
                if e.trading_status != marketdata_pb2.TradingStatus():  # Торговый статус
                    self.logger.debug(f'subscriptions_marketdata_handler: Пришел торговый статус {e.trading_status}')
                    self.on_trading_status(e.trading_status)
                if e.last_price != marketdata_pb2.LastPrice():  # Цена последней сделки
                    self.logger.debug(f'subscriptions_marketdata_handler: Пришла цена последней сделки {e.last_price}')
                    self.on_last_price(e.last_price)
                if e.ping != common_pb2.Ping():  # Проверка канала со стороны Тинькофф. Получаем время сервера
                    dt = self.utc_to_msk_datetime(datetime.utcfromtimestamp(e.ping.time.seconds))
                    self.logger.debug(f'subscriptions_marketdata_handler: Пришло время сервера {dt:%d.%m.%Y %H:%M}')
                    self.set_time_delta(e.ping.time)  # Обновляем разницу между локальным временем и временем сервера
        except RpcError:  # При закрытии канала попадем на эту ошибку (grpc._channel._MultiThreadedRendezvous)
            pass  # Все в порядке, ничего делать не нужно

    def subscriptions_marketdata_server_handler(self, request: marketdata_pb2.MarketDataServerSideStreamRequest):
        """Поток обработки подписок на биржевую информацию. Список подписок на сервере"""
        try:
            for event in self.stub_marketdata_stream.MarketDataServerSideStream(request=request, metadata=self.metadata):  # Пробегаемся по значениям подписок до закрытия канала
                e: marketdata_pb2.MarketDataResponse = event  # Приводим пришедшее значение к подписке
                if e.candle != marketdata_pb2.Candle():  # Свеча
                    self.logger.debug(f'subscriptions_marketdata_handler: Пришел бар {e.candle}')
                    self.on_candle(e.candle)
                if e.trade != marketdata_pb2.Trade():  # Сделки
                    self.logger.debug(f'subscriptions_marketdata_handler: Пришла сделка {e.trade}')
                    self.on_trade(e.trade)
                if e.orderbook != marketdata_pb2.OrderBook():  # Стакан
                    self.logger.debug(f'subscriptions_marketdata_handler: Пришел стакан {e.orderbook}')
                    self.on_orderbook(e.orderbook)
                if e.trading_status != marketdata_pb2.TradingStatus():  # Торговый статус
                    self.logger.debug(f'subscriptions_marketdata_handler: Пришел торговый статус {e.trading_status}')
                    self.on_trading_status(e.trading_status)
                if e.last_price != marketdata_pb2.LastPrice():  # Цена последней сделки
                    self.logger.debug(f'subscriptions_marketdata_handler: Пришла цена последней сделки {e.last_price}')
                    self.on_last_price(e.last_price)
                if e.ping != common_pb2.Ping():  # Проверка канала со стороны Тинькофф. Получаем время сервера
                    dt = self.utc_to_msk_datetime(datetime.utcfromtimestamp(e.ping.time.seconds))
                    self.logger.debug(f'subscriptions_marketdata_handler: Пришло время сервера {dt:%d.%m.%Y %H:%M}')
                    self.set_time_delta(e.ping.time)  # Обновляем разницу между локальным временем и временем сервера
        except RpcError:  # При закрытии канала попадем на эту ошибку (grpc._channel._MultiThreadedRendezvous)
            pass  # Все в порядке, ничего делать не нужно

    def subscriptions_portfolio_handler(self, account_id):
        """Поток обработки подписок на портфель"""
        try:
            for event in self.stub_operations_stream.PortfolioStream(request=operations_pb2.PortfolioStreamRequest(accounts=(account_id,)), metadata=self.metadata):  # Пробегаемся по значениям подписок до закрытия канала
                e: operations_pb2.PortfolioStreamResponse = event  # Приводим пришедшее значение к подписке
                if e.portfolio != operations_pb2.PortfolioResponse():  # Портфель
                    self.logger.debug(f'subscriptions_portfolio_handler: Пришли портфели {e.subscriptions.accounts}')
                    self.on_portfolio(e.portfolio)
                if e.ping != common_pb2.Ping():  # Проверка канала со стороны Тинькофф. Получаем время сервера
                    dt = self.utc_to_msk_datetime(datetime.utcfromtimestamp(e.ping.time.seconds))
                    self.logger.debug(f'subscriptions_portfolio_handler: Пришло время сервера {dt:%d.%m.%Y %H:%M}')
        except RpcError:  # При закрытии канала попадем на эту ошибку (grpc._channel._MultiThreadedRendezvous)
            pass  # Все в порядке, ничего делать не нужно

    def subscriptions_positions_handler(self, account_id):
        """Поток обработки подписок на позиции"""
        try:
            for event in self.stub_operations_stream.PositionsStream(request=operations_pb2.PositionsStreamRequest(accounts=(account_id,)), metadata=self.metadata):  # Пробегаемся по значениям подписок до закрытия канала
                e: operations_pb2.PositionsStreamResponse = event  # Приводим пришедшее значение к подписке
                if e.position != operations_pb2.PositionData():  # Позиция
                    self.logger.debug(f'subscriptions_positions_handler: Пришла позиция {e.position}')
                    self.on_position(e.position)
                if e.ping != common_pb2.Ping():  # Проверка канала со стороны Тинькофф. Получаем время сервера
                    dt = self.utc_to_msk_datetime(datetime.utcfromtimestamp(e.ping.time.seconds))
                    self.logger.debug(f'subscriptions_positions_handler: Пришло время сервера {dt:%d.%m.%Y %H:%M}')
        except RpcError:  # При закрытии канала попадем на эту ошибку (grpc._channel._MultiThreadedRendezvous)
            pass  # Все в порядке, ничего делать не нужно

    def subscriptions_trades_handler(self, account_ids):
        """Поток обработки подписок на сделки по заявке"""
        try:
            for event in self.stub_orders_stream.TradesStream(request=orders_pb2.TradesStreamRequest(accounts=account_ids), metadata=self.metadata):  # Пробегаемся по значениям подписок до закрытия канала
                e: orders_pb2.TradesStreamResponse = event  # Приводим пришедшее значение к подписке
                if e.order_trades != orders_pb2.OrderTrades():  # Сделки по заявке
                    self.logger.debug(f'subscriptions_trades_handler: Пришли сделки по заявке {e.order_trades}')
                    self.on_order_trades(e.order_trades)
                if e.ping != common_pb2.Ping():  # Проверка канала со стороны Тинькофф. Получаем время сервера
                    dt = self.utc_to_msk_datetime(datetime.utcfromtimestamp(e.ping.time.seconds))
                    self.logger.debug(f'subscriptions_trades_handler: Пришло время сервера {dt:%d.%m.%Y %H:%M}')
                    self.set_time_delta(e.ping.time)  # Обновляем разницу между локальным временем и временем сервера
        except RpcError:  # При закрытии канала попадем на эту ошибку (grpc._channel._MultiThreadedRendezvous)
            pass  # Все в порядке, ничего делать не нужно

    # Выход и закрытие

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_channel()

    def __del__(self):
        self.close_channel()

    def close_channel(self):
        """Закрытие канала"""
        self.channel.close()

    # Функции конвертации

    def dataname_to_class_code_symbol(self, dataname) -> tuple[str, str]:
        """Биржа и код тикера из названия тикера. Если задается без биржи, то по умолчанию ставится MOEX

        :param str dataname: Название тикера
        :return: Код площадки и код тикера
        """
        symbol_parts = dataname.split('.')  # По разделителю пытаемся разбить тикер на части
        if len(symbol_parts) >= 2:  # Если тикер задан в формате <Код площадки>.<Код тикера>
            class_code = symbol_parts[0]  # Код площадки
            symbol = '.'.join(symbol_parts[1:])  # Код тикера
        else:  # Если тикер задан без площадки
            symbol = dataname  # Код тикера
            class_code = next((item.class_code for item in self.symbols.values() if item.ticker == symbol), None)  # Получаем код площадки первого совпадающего тикера
        return class_code, symbol  # Возвращаем код площадки и код тикера

    @staticmethod
    def class_code_symbol_to_dataname(class_code, symbol) -> str:
        """Название тикера из кода площадки и кода тикера

        :param str class_code: Код площадки
        :param str symbol: Тикер
        :return: Название тикера
        """
        return f'{class_code}.{symbol}'

    def get_symbol_info(self, class_code, symbol, reload=False) -> Union[instruments_pb2.Instrument, None]:
        """Спецификация тикера

        :param str class_code: : Код площадки
        :param str symbol: Тикер
        :param bool reload: Получить информацию с Тинькофф
        :return: Значение из кэша/Тинькофф или None, если тикер не найден
        """
        if reload or (class_code, symbol) not in self.symbols:  # Если нужно получить информацию с Тинькофф или нет информации о тикере в справочнике
            request = instruments_pb2.InstrumentRequest(id_type=instruments_pb2.InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER, class_code=class_code, id=symbol)  # Поиск тикера по коду площадки/названию
            response: instruments_pb2.InstrumentResponse = self.call_function(self.stub_instruments.GetInstrumentBy, request)  # Получаем информацию о тикере
            if not response:  # Если информация о тикере не найдена
                self.logger.warning(f'Информация о {class_code}.{symbol} не найдена')
                return None  # то возвращаем пустое значение
            self.symbols[(class_code, symbol)] = response.instrument  # Заносим информацию о тикере в справочник
        return self.symbols[(class_code, symbol)]  # Возвращаем значение из справочника

    def figi_to_symbol_info(self, figi) -> Union[instruments_pb2.Instrument, None]:
        """Получение информации тикера по уникальному коду

        :param str figi: : Уникальный код тикера
        :return: Значение из кэша/Тинькофф или None, если тикер не найден
        """
        instrument = next((item for item in self.symbols.values() if item.figi == figi), None)  # Пытаемся найти значение в справочнике
        if instrument:  # Если значение найдено в справочнике
            return instrument  # то возвращаем его
        request = instruments_pb2.InstrumentRequest(id_type=instruments_pb2.InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI, class_code='', id=figi)  # Поиск тикера по уникальному коду
        response: instruments_pb2.InstrumentResponse = self.call_function(self.stub_instruments.GetInstrumentBy, request)  # Получаем информацию о тикере
        if not response:  # Если информация о тикере не найдена
            self.logger.warning(f'Информация о тикере с figi={figi} не найдена')
            return None  # то возвращаем пустое значение
        instrument = response.instrument  # Информацию о тикере
        self.symbols[(instrument.class_code, instrument.ticker)] = instrument  # заносим в справочник
        return instrument  # и возвращаем его

    @staticmethod
    def timeframe_to_tinkoff_timeframe(tf) -> tuple[marketdata_pb2.CandleInterval, bool]:
        """Перевод временнОго интервала во временной интервал Тинькофф

        :param str tf: Временной интервал https://ru.wikipedia.org/wiki/Таймфрейм
        :return: Временной интервал Тинькофф, внутридневной бар
        """
        if tf[0:1] == 'D':  # 1 день
            return marketdata_pb2.CandleInterval.CANDLE_INTERVAL_DAY, False
        if tf[0:1] == 'W':  # 1 неделя
            return marketdata_pb2.CandleInterval.CANDLE_INTERVAL_WEEK, False
        if 'MN' in tf:  # 1 месяц
            return marketdata_pb2.CandleInterval.CANDLE_INTERVAL_MONTH, False
        if tf[0:1] == 'M':  # Минуты
            if not tf[1:].isdigit():  # Если после минут не стоит число
                raise NotImplementedError  # то с такими временнЫми интервалами не работаем
            interval = int(tf[1:])  # Временной интервал
            if interval == 1:  # 1 минута
                return marketdata_pb2.CandleInterval.CANDLE_INTERVAL_1_MIN, True
            if interval == 2:  # 2 минуты
                return marketdata_pb2.CandleInterval.CANDLE_INTERVAL_2_MIN, True
            if interval == 3:  # 3 минуты
                return marketdata_pb2.CandleInterval.CANDLE_INTERVAL_3_MIN, True
            if interval == 5:  # 5 минут
                return marketdata_pb2.CandleInterval.CANDLE_INTERVAL_5_MIN, True
            if interval == 10:  # 10 минут
                return marketdata_pb2.CandleInterval.CANDLE_INTERVAL_10_MIN, True
            if interval == 15:  # 15 минут
                return marketdata_pb2.CandleInterval.CANDLE_INTERVAL_15_MIN, True
            if interval == 30:  # 30 минут
                return marketdata_pb2.CandleInterval.CANDLE_INTERVAL_30_MIN, True
            if interval == 60:  # 1 час
                return marketdata_pb2.CandleInterval.CANDLE_INTERVAL_HOUR, True
            if interval == 120:  # 2 часа
                return marketdata_pb2.CandleInterval.CANDLE_INTERVAL_2_HOUR, True
            if interval == 240:  # 4 часа
                return marketdata_pb2.CandleInterval.CANDLE_INTERVAL_4_HOUR, True
        raise NotImplementedError  # С остальными временнЫми интервалами не работаем

    @staticmethod
    def tinkoff_timeframe_to_timeframe(tf) -> tuple[str, timedelta]:
        """Перевод временнОго интервала Тинькофф во временной интервал и максимальный период запроса

        :param CandleInterval tf: Временной интервал Тинькофф
        :return: Временной интервал https://ru.wikipedia.org/wiki/Таймфрейм и максимальный период запроса
        """
        # Ограничения на максимальный период запроса https://tinkoff.github.io/investAPI/load_history/
        if tf == marketdata_pb2.CandleInterval.CANDLE_INTERVAL_1_MIN:  # 1 минута
            return 'M1', timedelta(days=1)  # Максимальный запрос за 1 день
        if tf == marketdata_pb2.CandleInterval.CANDLE_INTERVAL_2_MIN:  # 2 минуты
            return 'M2', timedelta(days=1)  # Максимальный запрос за 1 день
        if tf == marketdata_pb2.CandleInterval.CANDLE_INTERVAL_3_MIN:  # 3 минуты
            return 'M3', timedelta(days=1)  # Максимальный запрос за 1 день
        if tf == marketdata_pb2.CandleInterval.CANDLE_INTERVAL_5_MIN:  # 5 минут
            return 'M5', timedelta(days=1)  # Максимальный запрос за 1 день
        if tf == marketdata_pb2.CandleInterval.CANDLE_INTERVAL_10_MIN:  # 10 минут
            return 'M10', timedelta(days=1)  # Максимальный запрос за 1 день
        if tf == marketdata_pb2.CandleInterval.CANDLE_INTERVAL_15_MIN:  # 15 минут
            return 'M15', timedelta(days=1)  # Максимальный запрос за 1 день
        if tf == marketdata_pb2.CandleInterval.CANDLE_INTERVAL_30_MIN:  # 30 минут
            return 'M30', timedelta(days=2)  # Максимальный запрос за 2 дня
        if tf == marketdata_pb2.CandleInterval.CANDLE_INTERVAL_HOUR:  # 1 час
            return 'M60', timedelta(days=7)  # Максимальный запрос за 1 неделю
        if tf == marketdata_pb2.CandleInterval.CANDLE_INTERVAL_2_HOUR:  # 2 часа
            return 'M120', timedelta(days=28)  # Максимальный запрос за 1 месяц
        if tf == marketdata_pb2.CandleInterval.CANDLE_INTERVAL_4_HOUR:  # 4 часа
            return 'M240', timedelta(days=28)  # Максимальный запрос за 1 месяц
        if tf == marketdata_pb2.CandleInterval.CANDLE_INTERVAL_DAY:  # 1 день
            return 'D1', timedelta(days=365)  # Максимальный запрос за 1 год
        if tf == marketdata_pb2.CandleInterval.CANDLE_INTERVAL_WEEK:  # 1 неделя
            return 'W1', timedelta(days=365 * 2)  # Максимальный запрос за 2 года
        if tf == marketdata_pb2.CandleInterval.CANDLE_INTERVAL_MONTH:  # 1 месяц
            return 'MN1', timedelta(days=365 * 10)  # Максимальный запрос за 10 лет
        raise NotImplementedError  # С остальными временнЫми интервалами не работаем

    def price_to_tinkoff_price(self, class_code, symbol, price) -> float:
        """Перевод цены в цену Tinkoff. Обратные формулы по статье https://tinkoff.github.io/investAPI/table_order_currency/

        :param str class_code: Код режима торгов
        :param str symbol: Тикер
        :param float price: Цена
        :return: Цена в Tinkoff
        """
        si = self.get_symbol_info(class_code, symbol)  # Информация о тикере
        min_step = self.quotation_to_float(si.min_price_increment)  # Шаг цены
        request = instruments_pb2.InstrumentRequest(id_type=instruments_pb2.InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER, class_code=class_code, id=symbol)  # Поиск тикера по коду площадки/названию
        if si.instrument_kind == common_pb2.INSTRUMENT_TYPE_BOND:  # Для облигаций
            bonds_response: instruments_pb2.BondsResponse = self.call_function(self.stub_instruments.BondBy, request)  # Получаем информацию об облигации
            instrument = bonds_response.instruments[0]  # Берем первую облигацию из списка
            return price * 100 / instrument.nominal // min_step * min_step  # Пункты цены для котировок облигаций представляют собой проценты номинала облигации
        if si.instrument_kind == common_pb2.INSTRUMENT_TYPE_CURRENCY:  # Для валют
            currency_response: instruments_pb2.CurrencyResponse = self.call_function(self.stub_instruments.CurrencyBy, request)  # Получаем информацию о валюте
            instrument = currency_response.instrument  # Информация о валюте
            return price / si.lot * self.money_value_to_float(instrument.nominal) // min_step * min_step
        if si.instrument_kind == common_pb2.INSTRUMENT_TYPE_FUTURES:  # Для фьючерсов
            futures_response: instruments_pb2.FutureResponse = self.call_function(self.stub_instruments.FutureBy, request)  # Получаем информацию о фьючерсе
            margin_request = instruments_pb2.GetFuturesMarginRequest(figi=si.figi)  # Запрос маржи
            margin_response: instruments_pb2.GetFuturesMarginResponse = self.call_function(self.stub_instruments.GetFuturesMargin, margin_request)  # Получаем информацию ГО по фьючерсу
            return price * self.quotation_to_float(futures_response.instrument.min_price_increment) / self.quotation_to_float(margin_response.min_price_increment_amount) // min_step * min_step  # Стоимость фьючерсов предоставляется в пунктах
        return price // min_step * min_step  # В остальных случаях возвращаем цену кратную шагу цены

    def tinkoff_price_to_price(self, class_code, symbol, tinkoff_price) -> float:
        """Перевод цены Tinkoff в цену. Формулы по статье https://tinkoff.github.io/investAPI/table_order_currency/

        :param str class_code: Код режима торгов
        :param str symbol: Тикер
        :param float tinkoff_price: Цена в Tinkoff
        :return: Цена
        """
        si = self.get_symbol_info(class_code, symbol)  # Информация о тикере
        min_step = self.quotation_to_float(si.min_price_increment)  # Шаг цены
        tinkoff_price = tinkoff_price // min_step * min_step  # Цена кратная шагу цены
        request = instruments_pb2.InstrumentRequest(id_type=instruments_pb2.InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER, class_code=class_code, id=symbol)  # Поиск тикера по коду площадки/названию
        if si.instrument_kind == common_pb2.INSTRUMENT_TYPE_BOND:  # Для облигаций
            bonds_response: instruments_pb2.BondsResponse = self.call_function(self.stub_instruments.BondBy, request)  # Получаем информацию об облигации
            instrument = bonds_response.instruments[0]  # Берем первую облигацию из списка
            return tinkoff_price / 100 * self.money_value_to_float(instrument.nominal)  # Пункты цены для котировок облигаций представляют собой проценты номинала облигации
        if si.instrument_kind == common_pb2.INSTRUMENT_TYPE_CURRENCY:  # Для валют
            currency_response: instruments_pb2.CurrencyResponse = self.call_function(self.stub_instruments.CurrencyBy, request)  # Получаем информацию о валюте
            instrument = currency_response.instrument  # Информация о валюте
            return tinkoff_price * si.lot / self.money_value_to_float(instrument.nominal)
        if si.instrument_kind == common_pb2.INSTRUMENT_TYPE_FUTURES:  # Для фьючерсов
            futures_response: instruments_pb2.FutureResponse = self.call_function(self.stub_instruments.FutureBy, request)  # Получаем информацию о фьючерсе
            margin_request = instruments_pb2.GetFuturesMarginRequest(figi=si.figi)  # Запрос маржи
            margin_response: instruments_pb2.GetFuturesMarginResponse = self.call_function(self.stub_instruments.GetFuturesMargin, margin_request)  # Получаем информацию ГО по фьючерсу
            return tinkoff_price / self.quotation_to_float(futures_response.instrument.min_price_increment) * self.quotation_to_float(margin_response.min_price_increment_amount)  # Стоимость фьючерсов предоставляется в пунктах
        return tinkoff_price  # В остальных случаях цена не изменяется

    def money_value_to_float(self, money_value, currency=None) -> float:
        """Перевод денежной суммы в валюте в вещественное число

        :param MoneyValue money_value: Денежная сумма в валюте
        :param PortfolioRequest.CurrencyRequest currency: Валюта
        :return: Вещественное число
        """
        figis = ('TCS0013HGFT4', 'TCS2013HJJ31')  # Уникальные коды курсовых тикеров USD000000TOD / EUR_RUB__TOD
        if not currency:  # Если не укаазна валюта
            currency = self.currency  # то будем считать в валюте по умолчанию
        k = 1  # Коэфф. конвертации
        if currency != money_value.currency:  # Если нужно конвертировать
            response: marketdata_pb2.GetLastPricesResponse = self.call_function(self.stub_marketdata.GetLastPrices, marketdata_pb2.GetLastPricesRequest(instrument_id=figis))  # Последние цены курсовых тикеров
            usd = self.quotation_to_float(response.last_prices[0].price)  # Курс доллар/рубль
            eur = self.quotation_to_float(response.last_prices[1].price)  # Курс евро/рубль
            if money_value.currency == operations_pb2.PortfolioRequest.CurrencyRequest.RUB and currency == operations_pb2.PortfolioRequest.CurrencyRequest.USD:  # Конвертируем рубль в доллар США
                k = 1 / usd  # Обратная котировка
            elif money_value.currency == operations_pb2.PortfolioRequest.CurrencyRequest.RUB and currency == operations_pb2.PortfolioRequest.CurrencyRequest.EUR:  # Конвертируем рубль в евро
                k = 1 / eur  # Обратная котировка
            elif money_value.currency == operations_pb2.PortfolioRequest.CurrencyRequest.USD and currency == operations_pb2.PortfolioRequest.CurrencyRequest.RUB:  # Конвертируем доллар США в рубль
                k = usd  # Прямая котировка
            elif money_value.currency == operations_pb2.PortfolioRequest.CurrencyRequest.USD and currency == operations_pb2.PortfolioRequest.CurrencyRequest.EUR:  # Конвертируем доллар США в евро
                k = usd / eur
            elif money_value.currency == operations_pb2.PortfolioRequest.CurrencyRequest.EUR and currency == operations_pb2.PortfolioRequest.CurrencyRequest.RUB:  # Конвертируем евро в рубль
                k = eur  # Прямая котировка
            elif money_value.currency == operations_pb2.PortfolioRequest.CurrencyRequest.EUR and currency == operations_pb2.PortfolioRequest.CurrencyRequest.USD:  # Конвертируем евро в доллар США
                k = eur / usd
        return money_value.units + money_value.nano / 1_000_000_000 * k

    @staticmethod
    def money_dict_value_to_float(money_value) -> float:
        """Перевод денежной суммы в валюте в вещественное число

        :param dict money_value: Денежная сумма в валюте
        :return: Вещественное число
        """
        return int(money_value['units']) + money_value['nano'] / 1_000_000_000

    @staticmethod
    def float_to_quotation(f) -> common_pb2.Quotation:
        """Перевод вещественного числа в денежную сумму

        :param float f: Вещественное число
        :return: Денежная сумма
        """
        int_f = int(f)  # Целая часть числа
        return common_pb2.Quotation(units=int_f, nano=int(f * 1_000_000_000 - int_f * 1_000_000_000))

    @staticmethod
    def quotation_to_float(quotation) -> float:
        """Перевод денежной суммы в вещественное число

        :param Quotation quotation: Денежная сумма
        :return: Вещественное число
        """
        return quotation.units + quotation.nano / 1_000_000_000

    @staticmethod
    def dict_quotation_to_float(dict_quotation) -> float:
        """Перевод из словаря денежной суммы в вещественное число

        :param dict dict_quotation: Денежная сумма
        :return: Вещественное число
        """
        return int(dict_quotation['units']) + int(dict_quotation['nano']) / 1_000_000_000

    def timestamp_to_msk_datetime(self, timestamp) -> datetime:
        """Перевод времени из Google UTC Timestamp в московское

        :param Timestamp timestamp: Время Google UTC Timestamp
        :return: Московское время
        """
        return self.utc_to_msk_datetime(datetime.utcfromtimestamp(timestamp.seconds + timestamp.nanos / 1_000_000_000))

    def msk_datetime_to_timestamp(self, dt) -> int:
        """Перевод московского времени в кол-во секунд, прошедших с 01.01.1970 00:00 UTC

        :param datetime dt: Московское время
        :return: Кол-во секунд, прошедших с 01.01.1970 00:00 UTC
        """
        dt_msk = self.tz_msk.localize(dt)  # Заданное время ставим в зону МСК
        return int(dt_msk.timestamp())  # Переводим в кол-во секунд, прошедших с 01.01.1970 в UTC

    def msk_datetime_to_google_timestamp(self, dt) -> Timestamp:
        """Перевод московского времени в Google UTC Timestamp

        :param datetime dt: Московское время
        :return: Время Google UTC Timestamp
        """
        dt_msk = self.tz_msk.localize(dt)  # Заданное время ставим в зону МСК
        return Timestamp(seconds=int(dt_msk.timestamp()), nanos=dt_msk.microsecond * 1_000)

    def msk_to_utc_datetime(self, dt, tzinfo=False) -> datetime:
        """Перевод времени из московского в UTC

        :param datetime dt: Московское время
        :param bool tzinfo: Отображать временнУю зону
        :return: Время UTC
        """
        dt_msk = self.tz_msk.localize(dt)  # Заданное время ставим в зону МСК
        dt_utc = dt_msk.astimezone(utc)  # Переводим в UTC
        return dt_utc if tzinfo else dt_utc.replace(tzinfo=None)

    def utc_to_msk_datetime(self, dt, tzinfo=False) -> datetime:
        """Перевод времени из UTC в московское

        :param datetime dt: Время UTC
        :param bool tzinfo: Отображать временнУю зону
        :return: Московское время
        """
        dt_utc = utc.localize(dt)  # Заданное время ставим в зону UTC
        dt_msk = dt_utc.astimezone(self.tz_msk)  # Переводим в МСК
        return dt_msk if tzinfo else dt_msk.replace(tzinfo=None)

    def set_time_delta(self, timestamp: Timestamp):
        """Установка разницы между локальным временем и временем торгового сервера с учетом временнОй зоны

        :param Timestamp timestamp: Текущее время на сервере в формате Google UTC Timestamp
        """
        self.time_delta = datetime.utcfromtimestamp(timestamp.seconds) - datetime.utcnow()
