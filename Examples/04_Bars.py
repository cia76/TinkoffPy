from datetime import datetime, timedelta
from time import time
import os.path

from pytz import utc
import pandas as pd
from TinkoffPy import TinkoffPy  # Работа с Tinkoff Invest API из Python
from TinkoffPy.Config import Config  # Файл конфигурации

from TinkoffPy.grpc.marketdata_pb2 import GetCandlesRequest, CandleInterval
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.json_format import MessageToDict


def save_candles_to_file(class_code='TQBR', security_codes=('SBER',), interval=CandleInterval.CANDLE_INTERVAL_DAY,
                         skip_first_date=False, skip_last_date=False, four_price_doji=False):
    """Получение баров, объединение с имеющимися барами в файле (если есть), сохранение баров в файл

    :param str class_code: Код площадки
    :param tuple security_codes: Коды тикеров в виде кортежа
    :param CandleInterval interval: Временной интервал
    :param bool skip_first_date: Убрать бары на первую полученную дату
    :param bool skip_last_date: Убрать бары на последнюю полученную дату
    :param bool four_price_doji: Оставить бары с дожи 4-х цен
    """
    # Ограничения на максимальный период запроса period https://tinkoff.github.io/investAPI/faq_marketdata/
    if interval == CandleInterval.CANDLE_INTERVAL_1_MIN:  # 1 минута
        tf = 'M1'
        period = timedelta(days=1)
    elif interval == CandleInterval.CANDLE_INTERVAL_2_MIN:  # 2 минуты
        tf = 'M2'
        period = timedelta(days=1)
    elif interval == CandleInterval.CANDLE_INTERVAL_3_MIN:  # 3 минуты
        tf = 'M3'
        period = timedelta(days=1)
    elif interval == CandleInterval.CANDLE_INTERVAL_5_MIN:  # 5 минут
        tf = 'M5'
        period = timedelta(days=1)
    elif interval == CandleInterval.CANDLE_INTERVAL_10_MIN:  # 10 минут
        tf = 'M10'
        period = timedelta(days=1)
    elif interval == CandleInterval.CANDLE_INTERVAL_15_MIN:  # 15 минут
        tf = 'M15'
        period = timedelta(days=1)
    elif interval == CandleInterval.CANDLE_INTERVAL_30_MIN:  # 30 минут
        tf = 'M30'
        period = timedelta(days=2)
    elif interval == CandleInterval.CANDLE_INTERVAL_HOUR:  # 1 час
        tf = 'M60'
        period = timedelta(weeks=1)
    elif interval == CandleInterval.CANDLE_INTERVAL_2_HOUR:  # 2 часа
        tf = 'M120'
        period = timedelta(weeks=4)  # ~1 месяц
    elif interval == CandleInterval.CANDLE_INTERVAL_4_HOUR:  # 4 часа
        tf = 'M240'
        period = timedelta(weeks=4)  # ~1 месяц
    elif interval == CandleInterval.CANDLE_INTERVAL_DAY:  # 1 день
        tf = 'D1'
        period = timedelta(weeks=52)  # ~1 год
    elif interval == CandleInterval.CANDLE_INTERVAL_WEEK:  # 1 неделя
        tf = 'W1'
        period = timedelta(weeks=104)  # ~2 года
    elif interval == CandleInterval.CANDLE_INTERVAL_MONTH:  # 1 месяц
        tf = 'MN1'
        period = timedelta(weeks=520)  # ~10 лет
    else:  # Если временной интервал задан неверно
        print('Временной интервал задан неверно')
        return  # то выходим, дальше не продолжаем
    intraday = tf != 'MN1' and tf.startswith('M')  # Внутридневные интервалы начинаются с M, кроме MN1 (месяц)

    for security_code in security_codes:  # Пробегаемся по всем тикерам
        file_bars = None  # Дальше будем пытаться получить бары из файла
        file_name = f'{datapath}{class_code}.{security_code}_{tf}.txt'
        file_exists = os.path.isfile(file_name)  # Существует ли файл
        if file_exists:  # Если файл существует
            print(f'Получение файла {file_name}')
            file_bars = pd.read_csv(file_name, sep='\t', index_col='datetime')  # Считываем файл в DataFrame
            file_bars.index = pd.to_datetime(file_bars.index, format='%d.%m.%Y %H:%M')  # Переводим индекс в формат datetime
            last_date: datetime = file_bars.index[-1]  # Дата и время последнего бара по МСК
            print(f'- Первая запись файла: {file_bars.index[0]}')
            print(f'- Последняя запись файла: {last_date}')
            print(f'- Кол-во записей в файле: {len(file_bars)}')
            last_file_date_utc = utc.localize(last_date) if interval == CandleInterval.CANDLE_INTERVAL_MONTH else\
                tp_provider.msk_to_utc_datetime(last_date, True)  # Дата и время последнего бара по UTC
        else:  # Файл не существует
            print(f'Файл {file_name} не найден и будет создан')
            last_file_date_utc = utc.localize(datetime(1990, 1, 1))  # Берем дату, когда никакой тикер еще не торговался
        print(f'Получение истории {class_code}.{security_code} {tf} из Tinkoff')
        figi = tp_provider.get_symbol_info(class_code, security_code).figi  # Уникальный код тикера
        last_date_utc = datetime.utcnow().replace(tzinfo=utc)  # Запросы будем отправлять в обратном порядке. От текущей даты и времени до последней записи файла или когда тикер еще не торговался
        new_bars_list = []  # Список новых бар
        while True:  # Будем получать бары пока не получим все
            to = Timestamp(seconds=int(last_date_utc.timestamp()), nanos=last_date_utc.microsecond * 1_000)  # Дата и время окончания запроса в Timestamp
            request = GetCandlesRequest(instrument_id=figi, to=to, interval=interval)  # Запрос на получение бар
            from_ = getattr(request, 'from')  # т.к. from - ключевое слово в Python, то получаем атрибут from из атрибута интервала
            prev_date_utc = last_date_utc - period  # Дата и время начала запроса
            from_.seconds = int(prev_date_utc.timestamp())
            from_.nanos = prev_date_utc.microsecond * 1_000
            try:  # Если вышли по кол-ву запросов в минуту лимитной политики https://tinkoff.github.io/investAPI/limits/
                new_bars_dict = MessageToDict(tp_provider.call_function(tp_provider.stub_marketdata.GetCandles, request), including_default_value_fields=True)['candles']  # Получаем бары, переводим в словарь/список
            except AttributeError:
                print('Превышено кол-во запросов в минуту лимитной политики')
                break  # то выходим из цикла получения баров
            for new_bar in new_bars_dict:  # Пробегаемся по всем полученным барам
                if not new_bar['isComplete']:  # Если добрались до незавершенного бара
                    break  # то это последний бар, больше бары обрабатывать не будем
                dt_utc = datetime.fromisoformat(new_bar['time'][:-1])  # Дата и время начала бара в UTC
                dt = tp_provider.utc_to_msk_datetime(dt_utc) if intraday else \
                    datetime(dt_utc.year, dt_utc.month, dt_utc.day)  # Дату/время переводим из UTC в МСК
                open_ = int(new_bar['open']['units']) + int(new_bar['open']['nano']) / 10**9
                high = int(new_bar['high']['units']) + int(new_bar['high']['nano']) / 10**9
                low = int(new_bar['low']['units']) + int(new_bar['low']['nano']) / 10**9
                close = int(new_bar['close']['units']) + int(new_bar['close']['nano']) / 10**9
                volume = int(new_bar['volume'])
                new_bars_list.append({'datetime': dt, 'open': open_, 'high': high, 'low': low, 'close': close, 'volume': volume})
            print(new_bars_list[-1]['datetime'])  # Последняя дата/время полученных баров
            last_date_utc = prev_date_utc  # Следующий запрос будем делать до начала этого
            if last_date_utc < last_file_date_utc:  # Если дата окончания UTC раньше даты окончания файла
                break  # то выходим из цикла получения баров
        if len(new_bars_list) == 0:  # Если новых записей нет
            print('Новых записей нет')
            continue  # то переходим к следующему тикеру, дальше не продолжаем
        pd_bars = pd.DataFrame(new_bars_list)  # Список новых бар -> DataFrame
        pd_bars = pd_bars.loc[pd_bars.astype(str).drop_duplicates().index]  # Удаляем дубли бар
        pd_bars.index = pd_bars['datetime']  # В индекс ставим дату
        pd_bars = pd_bars[['open', 'high', 'low', 'close', 'volume']]  # Отбираем нужные колонки
        pd_bars.sort_index(inplace=True)  # Сортируем по индексу
        if not file_exists and skip_first_date:  # Если файла нет, и убираем бары на первую дату
            len_with_first_date = len(pd_bars)  # Кол-во баров до удаления на первую дату
            first_date = pd_bars.index[0].date()  # Первая дата
            pd_bars.drop(pd_bars[(pd_bars.index.date == first_date)].index, inplace=True)  # Удаляем их
            print(f'- Удалено баров на первую дату {first_date}: {len_with_first_date - len(pd_bars)}')
        if skip_last_date:  # Если убираем бары на последнюю дату
            len_with_last_date = len(pd_bars)  # Кол-во баров до удаления на последнюю дату
            last_date = pd_bars.index[-1].date()  # Последняя дата
            pd_bars.drop(pd_bars[(pd_bars.index.date == last_date)].index, inplace=True)  # Удаляем их
            print(f'- Удалено баров на последнюю дату {last_date}: {len_with_last_date - len(pd_bars)}')
        if not four_price_doji:  # Если удаляем дожи 4-х цен
            len_with_doji = len(pd_bars)  # Кол-во баров до удаления дожи
            pd_bars.drop(pd_bars[(pd_bars.high == pd_bars.low)].index, inplace=True)  # Удаляем их по условия High == Low
            print('- Удалено дожи 4-х цен:', len_with_doji - len(pd_bars))
        if len(pd_bars) == 0:  # Если нечего объединять
            print('Новых записей нет')
            continue  # то переходим к следующему тикеру, дальше не продолжаем
        print(f'- Первая запись в Tinkoff: {pd_bars.index[0]}')
        print(f'- Последняя запись в Tinkoff: {pd_bars.index[-1]}')
        print(f'- Кол-во записей в Tinkoff: {len(pd_bars)}')
        if file_exists:  # Если файл существует
            pd_bars = pd.concat([file_bars, pd_bars]).drop_duplicates(keep='last').sort_index()  # Объединяем файл с данными из Finam, убираем дубликаты, сортируем заново
        pd_bars.to_csv(file_name, sep='\t', date_format='%d.%m.%Y %H:%M')
        print(f'- В файл {file_name} сохранено записей: {len(pd_bars)}')


if __name__ == '__main__':  # Точка входа при запуске этого скрипта
    start_time = time()  # Время начала запуска скрипта
    tp_provider = TinkoffPy(Config.Token)  # Провайдер работает со всеми счетами по токену (из файла Config.py)

    class_code = 'TQBR'  # Акции ММВБ
    security_codes = ('SBER', 'VTBR', 'GAZP', 'MTLR', 'LKOH', 'PLZL', 'SBERP', 'BSPB', 'POLY', 'RNFT',
                      'GMKN', 'AFLT', 'NVTK', 'TATN', 'YNDX', 'MGNT', 'ROSN', 'AFKS', 'NLMK', 'ALRS',
                      'MOEX', 'SMLT', 'MAGN', 'CHMF', 'CBOM', 'MTLRP', 'SNGS', 'BANEP', 'MTSS', 'IRAO',
                      'SNGSP', 'SELG', 'UPRO', 'RUAL', 'TRNFP', 'FEES', 'SGZH', 'BANE', 'PHOR', 'PIKK')  # TOP 40 акций ММВБ
    # security_codes = ('SBER',)  # Для тестов
    datapath = os.path.join('..', '..', 'DataTinkoff', '')  # Путь сохранения файлов для Windows/Linux

    skip_last_date = True  # Если получаем данные внутри сессии, то не берем бары за дату незавершенной сессии
    # skip_last_date = False  # Если получаем данные, когда рынок не работает, то берем все бары
    # Из-за ограничений кол-ва запросов лимитной политики запуск производим в несколько этапов
    # На каждом этапе удаляем неполностью полученный тикер, запускаем снова, и так до финала
    save_candles_to_file(class_code, security_codes, four_price_doji=True)  # Дневные бары получаем всегда все, т.к. выдаются только завершенные бары
    # Часовые бары уже не получится получить полностью из-за лимитной политики
    # Как альтернативу можно использовать сервис загрузки исторических минутных данных в виде архива https://tinkoff.github.io/investAPI/get_history/
    # Нужно дополнительно из минутных бар переводить в требуемый временной интервал
    # save_candles_to_file(class_code, security_codes, CandleInterval.CANDLE_INTERVAL_HOUR, skip_last_date=skip_last_date)  # часовые бары
    # save_candles_to_file(class_code, security_codes, CandleInterval.CANDLE_INTERVAL_15_MIN, skip_last_date=skip_last_date)  # 15-и минутные бары
    # save_candles_to_file(class_code, security_codes, CandleInterval.CANDLE_INTERVAL_5_MIN, skip_last_date=skip_last_date)  # 5-и минутные бары
    # save_candles_to_file(class_code, security_codes, CandleInterval.CANDLE_INTERVAL_1_MIN, skip_last_date=skip_last_date, four_price_doji=True)  # минутные бары

    print(f'Скрипт выполнен за {(time() - start_time):.2f} с')
