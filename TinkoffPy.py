from typing import Union  # Объединение типов
from datetime import datetime, timedelta
from pytz import timezone, utc  # Работаем с временнОй зоной и UTC
from grpc import ssl_channel_credentials, secure_channel, RpcError, StatusCode  # Защищенный канал
from google.protobuf.timestamp_pb2 import Timestamp
from .grpc.instruments_pb2_grpc import InstrumentsServiceStub
from .grpc.marketdata_pb2_grpc import MarketDataServiceStub
from .grpc.operations_pb2_grpc import OperationsServiceStub
from .grpc.orders_pb2_grpc import OrdersServiceStub
from .grpc.stoporders_pb2_grpc import StopOrdersServiceStub
from .grpc.common_pb2 import MoneyValue, Quotation
from .grpc.marketdata_pb2 import CandleInterval
from .grpc.instruments_pb2 import InstrumentRequest, InstrumentIdType, InstrumentResponse, Instrument
from .grpc.operations_pb2 import PortfolioRequest


class TinkoffPy:
    """Работа с Tinkoff Invest API из Python https://tinkoff.github.io/investAPI/"""
    tz_msk = timezone('Europe/Moscow')  # Время UTC будем приводить к московскому времени
    server = 'invest-public-api.tinkoff.ru'  # Торговый сервер
    currency = PortfolioRequest.CurrencyRequest.RUB  # Суммы будем получать в российских рублях

    def __init__(self, token):
        """Инициализация

        :param str token: Токен доступа
        """
        self.metadata = [('authorization', f'Bearer {token}')]  # Токен доступа
        self.channel = secure_channel(self.server, ssl_channel_credentials())  # Защищенный канал
        self.stub_instruments = InstrumentsServiceStub(self.channel)  # Сервис инструментов
        self.stub_marketdata = MarketDataServiceStub(self.channel)  # Сервис получения биржевой информации
        self.stub_operations = OperationsServiceStub(self.channel)  # Сервис операций
        self.stub_orders = OrdersServiceStub(self.channel)  # Сервис заявок
        self.stub_stop_orders = StopOrdersServiceStub(self.channel)  # Сервис стоп заявок
        self.symbols = {}  # Информация о тикерах
        self.delta = timedelta(seconds=0)  # Разница между локальным временем и временем торгового сервера с учетом временнОй зоны

    # Запросы

    def call_function(self, func, request):
        """Вызов функции"""
        try:  # Пытаемся
            response, call = func.with_call(request=request, metadata=self.metadata)  # вызвать функцию
            return response  # и вернуть ответ
        except RpcError:  # Если получили ошибку канала
            return None  # то возвращаем пустое значение

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
            class_code = next(item.class_code for item in self.symbols if item.ticker == symbol)  # Получаем код площадки первого совпадающего тикера
        return class_code, symbol  # Возвращаем код площадки и код тикера

    @staticmethod
    def class_code_symbol_to_dataname(class_code, symbol) -> str:
        """Название тикера из кода площадки и кода тикера

        :param str class_code: Код площадки
        :param str symbol: Тикер
        :return: Название тикера
        """
        return f'{class_code}.{symbol}'

    def get_symbol_info(self, class_code, symbol, reload=False) -> Union[Instrument, None]:
        """Спецификация тикера

        :param str class_code: : Код площадки
        :param str symbol: Тикер
        :param bool reload: Получить информацию с Тинькофф
        :return: Значение из кэша/Тинькофф или None, если тикер не найден
        """
        if reload or (class_code, symbol) not in self.symbols:  # Если нужно получить информацию с Тинькофф или нет информации о тикере в справочнике
            try:  # Пробуем
                request = InstrumentRequest(id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER, class_code=class_code, id=symbol)  # Поиск тикера по коду площадки/названию
                response: InstrumentResponse = self.call_function(self.stub_instruments.GetInstrumentBy, request)  # Получаем информацию о тикере
            except RpcError as ex:  # Если произошла ошибка
                if ex.args[0].code == StatusCode.NOT_FOUND:  # Тикер не найден
                    print(f'Информация о {class_code}.{symbol} не найдена')
                return None  # то возвращаем пустое значение
            self.symbols[(class_code, symbol)] = response.instrument  # Заносим информацию о тикере в справочник
        return self.symbols[(class_code, symbol)]  # Возвращаем значение из справочника

    def figi_to_symbol_info(self, figi) -> Union[Instrument, None]:
        """Получение информации тикера по уникальному коду

        :param str figi: : Уникальный код тикера
        :return: Значение из кэша/Тинькофф или None, если тикер не найден
        """
        try:  # Пробуем
            return next(item for item in self.symbols.values() if item.figi == figi)  # вернуть значение из справочника
        except StopIteration:  # Если тикер не найден
            pass  # то продолжаем дальше
        try:  # Пробуем
            request = InstrumentRequest(id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI, class_code='', id=figi)  # Поиск тикера по уникальному коду
            response: InstrumentResponse = self.call_function(self.stub_instruments.GetInstrumentBy, request)  # Получаем информацию о тикере
            instrument = response.instrument  # Информация о тикере
            self.symbols[(instrument.class_code, instrument.ticker)] = instrument  # Заносим информацию о тикере в справочник
            return instrument
        except RpcError as ex:  # Если произошла ошибка
            if ex.args[0].code == StatusCode.NOT_FOUND:  # Тикер не найден
                print(f'Информация о тикере с figi={figi} не найдена')
            return None  # то возвращаем пустое значение

    @staticmethod
    def timeframe_to_tinkoff_timeframe(tf):
        """Перевод временнОго интервала во временной интервал Тинькофф

        :param str tf: Временной интервал https://ru.wikipedia.org/wiki/Таймфрейм
        :return: Временной интервал Тинькофф, внутридневной бар
        """
        if tf[0:1] == 'D':  # 1 день
            return CandleInterval.CANDLE_INTERVAL_DAY, False
        if tf[0:1] == 'W':  # 1 неделя
            return CandleInterval.CANDLE_INTERVAL_WEEK, False
        if 'MN' in tf:  # 1 месяц
            return CandleInterval.CANDLE_INTERVAL_MONTH, False
        if tf[0:1] == 'M':  # Минуты
            if not tf[1:].isdigit():  # Если после минут не стоит число
                raise NotImplementedError  # то с такими временнЫми интервалами не работаем
            interval = int(tf[1:])  # Временной интервал
            if interval == 1:  # 1 минута
                return CandleInterval.CANDLE_INTERVAL_1_MIN, True
            if interval == 2:  # 2 минуты
                return CandleInterval.CANDLE_INTERVAL_2_MIN, True
            if interval == 3:  # 3 минуты
                return CandleInterval.CANDLE_INTERVAL_3_MIN, True
            if interval == 5:  # 5 минут
                return CandleInterval.CANDLE_INTERVAL_5_MIN, True
            if interval == 10:  # 10 минут
                return CandleInterval.CANDLE_INTERVAL_10_MIN, True
            if interval == 15:  # 15 минут
                return CandleInterval.CANDLE_INTERVAL_15_MIN, True
            if interval == 30:  # 30 минут
                return CandleInterval.CANDLE_INTERVAL_30_MIN, True
            if interval == 60:  # 1 час
                return CandleInterval.CANDLE_INTERVAL_HOUR, True
            if interval == 120:  # 2 часа
                return CandleInterval.CANDLE_INTERVAL_2_HOUR, True
            if interval == 240:  # 4 часа
                return CandleInterval.CANDLE_INTERVAL_4_HOUR, True
        raise NotImplementedError  # С остальными временнЫми интервалами не работаем

    @staticmethod
    def money_value_to_float(money_value: MoneyValue) -> float:
        """Перевод денежной суммы в валюте в вещественное число

        :param money_value: Денежная сумма в валюте
        :return: Вещественное число
        """
        return money_value.units + money_value.nano / 1_000_000_000

    @staticmethod
    def float_to_quotation(f: float) -> Quotation:
        """Перевод вещественного числа в денежную сумму

        :param float f: Вещественное число
        :return: Денежная сумма
        """
        int_f = int(f)  # Целая часть числа
        return Quotation(units=int_f, nano=int((f - int_f) * 1_000_000_000))

    @staticmethod
    def quotation_to_float(quotation: Quotation) -> float:
        """Перевод денежной суммы в вещественное число

        :param quotation: Денежная сумма
        :return: Вещественное число
        """
        return quotation.units + quotation.nano / 1_000_000_000

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

    def set_delta(self, timestamp: Timestamp):
        """Установка разницы между локальным временем и временем торгового сервера с учетом временнОй зоны

        :param Timestamp timestamp: Текущее время на сервере в формате Google UTC Timestamp
        """
        self.delta = datetime.utcfromtimestamp(timestamp.seconds) - datetime.utcnow()
