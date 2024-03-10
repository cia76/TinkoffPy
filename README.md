# TinkoffPy
Библиотека-обертка, которая позволяет работать с функционалом [Tinkoff Invest API](https://tinkoff.github.io/investAPI/) брокера [Тинькофф Инвестиции](https://www.tinkoff.ru/invest/) из Python.

### Назначение
 - Создание автоматических торговых систем любой сложности
 - Написание дополнений к системам Технического Анализа
 - Тестирование торговых систем и автоматическая торговля в [BackTrader](https://www.backtrader.com/) через коннектор [BackTraderTinkoff](https://github.com/cia76/BackTraderTinkoff).

### Установка
1. Установите все требуемые библиотеки через **pip install -r requirements.txt**
2. Для работы с библиотекой потребуется токен. Инструкцию по его получению для реальных счетов смотрите в файле **Config.py**

### Начало работы
В папке **Examples** находится хорошо документированный код примеров. С них лучше начать разбираться с библиотекой.

- **Connect.py** - Подключение к TradeAPI. Проверка работы запрос/ответ: Данные тикера. Проверка работы подписок: Подписка на новые бары.
- **Accounts.py** - Получение позиций, свободных средств, заявок и стоп заявок для каждого счета.
- **Ticker.py** - Информация о различных тикерах. Валюта, лот, кол-во десятичных знаков. Вычисление шага цены из кол-ва десятичных знаков.
- **Bars.py** - Загрузка свечек из файла, если есть. Получение истории свечек. Сохранение всех свечек в файл с фильтрами первого/последнего дня и дожи 4-х цен.
- **Stream.py** - Запрос стакана. Подписка на стакан. Запрос обезличенных сделок. Подписка на обезличенные сделки.
- **Transactions.py** - Подписки на цену последней сделки, портфель, позиции, сделки по заявке. Получение последней цены сделки из дневных свечек. Выставление рыночных заявок на покупку и продажу. Выставление и отмена лимитной заявки. Выставление и отмена стоп заявки.

### Авторство, право использования, развитие
Автор библиотеки Чечет Игорь Александрович. Библиотека написана в рамках проекта [Финансовая Лаборатория](https://finlab.vip/).

Библиотека предоставляется бесплатно в исходном коде, с подробными комментариями и видеоразборами. При распространении ссылка на автора и проект обязательны.

Исправление ошибок, доработка и развитие библиотеки осуществляется автором и сообществом частных алготрейдеров проекта [Финансовая Лаборатория](https://finlab.vip/).
### Что дальше
- Бесплатный курс "Автоторговля" по идеям, концепциям и процессам алгоритмической/автоматической торговли [смотрите здесь >>>](https://finlab.vip/wpm-category/autotrading2021/)


- Бесплатный курс "BackTrader: Быстрый старт" [ждет вас здесь >>>](https://finlab.vip/wpm-category/btquikstart/)


- [Подписывайтесь на Telegram канал "Финансовой Лаборатории",](https://t.me/finlabvip) чтобы быть в курсе всех новинок алгоритмической и автоматической торговли.
