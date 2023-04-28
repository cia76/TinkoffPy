from typing import Union  # Объединение типов
from grpc import ssl_channel_credentials, secure_channel, RpcError, StatusCode  # Защищенный канал
from .grpc.instruments_pb2_grpc import InstrumentsServiceStub
from .grpc.marketdata_pb2_grpc import MarketDataServiceStub
from .grpc.operations_pb2_grpc import OperationsServiceStub
from .grpc.orders_pb2_grpc import OrdersServiceStub
from .grpc.stoporders_pb2_grpc import StopOrdersServiceStub
from .grpc.common_pb2 import MoneyValue, Quotation
from .grpc.instruments_pb2 import InstrumentRequest, InstrumentIdType, InstrumentResponse, Instrument
from .grpc.operations_pb2 import PortfolioRequest


class TinkoffPy:
    """Работа с Tinkoff Invest API из Python https://tinkoff.github.io/investAPI/"""
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

    # Запросы

    def call_function(self, func, request):
        """Вызов функции"""
        try:  # Пытаемся
            response, call = func.with_call(request=request, metadata=self.metadata)  # вызвать функцию
            return response  # и вернуть ответ
        except RpcError:  # Если получили ошибку канала
            return None  # то возвращаем пустое значение

    # Функции конвертации

    def get_symbol_info(self, class_code: str, symbol: str, reload=False) -> Union[Instrument, None]:
        """Получение информации тикера

        :param str class_code: : Код площадки
        :param str symbol: Тикер
        :param bool reload: Получить информацию с Тинькофф
        :return: Значение из кэша/Тинькоффили None, если тикер не найден
        """
        if reload or (class_code, symbol) not in self.symbols:  # Если нужно получить информацию с Тинькофф или нет информации о тикере в справочнике
            try:  # Пробуем
                request = InstrumentRequest(id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER, class_code=class_code, id=symbol)  # Поиск тикера по коду площадки/названию
                response: InstrumentResponse
                response, call = self.stub_instruments.GetInstrumentBy.with_call(request=request, metadata=self.metadata)  # получить информацию о тикере с Тинькофф
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
            response: InstrumentResponse
            response, call = self.stub_instruments.GetInstrumentBy.with_call(request=request, metadata=self.metadata)  # получить информацию о тикере с Тинькофф
            self.symbols[(response.instrument.class_code, response.instrument.ticker)] = response.instrument  # Заносим информацию о тикере в справочник
            return response.instrument
        except RpcError as ex:  # Если произошла ошибка
            if ex.args[0].code == StatusCode.NOT_FOUND:  # Тикер не найден
                print(f'Информация о тикере с figi={figi} не найдена')
            return None  # то возвращаем пустое значение

    def data_name_to_class_code_symbol(self, dataname) -> (str, str):
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
    def class_code_symbol_to_data_name(class_code, symbol) -> str:
        """Название тикера из кода площадки и кода тикера

        :param str class_code: Код площадки
        :param str symbol: Тикер
        :return: Название тикера
        """
        return f'{class_code}.{symbol}'

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
