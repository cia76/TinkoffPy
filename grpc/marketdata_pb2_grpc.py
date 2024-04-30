# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from TinkoffPy.grpc import marketdata_pb2 as marketdata__pb2


class MarketDataServiceStub(object):
    """Сервис получения биржевой информации:</br> **1**. свечи;</br> **2**. стаканы;</br> **3**. торговые статусы;</br> **4**. лента сделок.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetCandles = channel.unary_unary(
                '/tinkoff.public.invest.api.contract.v1.MarketDataService/GetCandles',
                request_serializer=marketdata__pb2.GetCandlesRequest.SerializeToString,
                response_deserializer=marketdata__pb2.GetCandlesResponse.FromString,
                )
        self.GetLastPrices = channel.unary_unary(
                '/tinkoff.public.invest.api.contract.v1.MarketDataService/GetLastPrices',
                request_serializer=marketdata__pb2.GetLastPricesRequest.SerializeToString,
                response_deserializer=marketdata__pb2.GetLastPricesResponse.FromString,
                )
        self.GetOrderBook = channel.unary_unary(
                '/tinkoff.public.invest.api.contract.v1.MarketDataService/GetOrderBook',
                request_serializer=marketdata__pb2.GetOrderBookRequest.SerializeToString,
                response_deserializer=marketdata__pb2.GetOrderBookResponse.FromString,
                )
        self.GetTradingStatus = channel.unary_unary(
                '/tinkoff.public.invest.api.contract.v1.MarketDataService/GetTradingStatus',
                request_serializer=marketdata__pb2.GetTradingStatusRequest.SerializeToString,
                response_deserializer=marketdata__pb2.GetTradingStatusResponse.FromString,
                )
        self.GetTradingStatuses = channel.unary_unary(
                '/tinkoff.public.invest.api.contract.v1.MarketDataService/GetTradingStatuses',
                request_serializer=marketdata__pb2.GetTradingStatusesRequest.SerializeToString,
                response_deserializer=marketdata__pb2.GetTradingStatusesResponse.FromString,
                )
        self.GetLastTrades = channel.unary_unary(
                '/tinkoff.public.invest.api.contract.v1.MarketDataService/GetLastTrades',
                request_serializer=marketdata__pb2.GetLastTradesRequest.SerializeToString,
                response_deserializer=marketdata__pb2.GetLastTradesResponse.FromString,
                )
        self.GetClosePrices = channel.unary_unary(
                '/tinkoff.public.invest.api.contract.v1.MarketDataService/GetClosePrices',
                request_serializer=marketdata__pb2.GetClosePricesRequest.SerializeToString,
                response_deserializer=marketdata__pb2.GetClosePricesResponse.FromString,
                )
        self.GetTechAnalysis = channel.unary_unary(
                '/tinkoff.public.invest.api.contract.v1.MarketDataService/GetTechAnalysis',
                request_serializer=marketdata__pb2.GetTechAnalysisRequest.SerializeToString,
                response_deserializer=marketdata__pb2.GetTechAnalysisResponse.FromString,
                )


class MarketDataServiceServicer(object):
    """Сервис получения биржевой информации:</br> **1**. свечи;</br> **2**. стаканы;</br> **3**. торговые статусы;</br> **4**. лента сделок.
    """

    def GetCandles(self, request, context):
        """Метод запроса исторических свечей по инструменту.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetLastPrices(self, request, context):
        """Метод запроса цен последних сделок по инструментам.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetOrderBook(self, request, context):
        """Метод получения стакана по инструменту.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetTradingStatus(self, request, context):
        """Метод запроса статуса торгов по инструментам.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetTradingStatuses(self, request, context):
        """Метод запроса статуса торгов по инструментам.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetLastTrades(self, request, context):
        """Метод запроса обезличенных сделок за последний час.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetClosePrices(self, request, context):
        """Метод запроса цен закрытия торговой сессии по инструментам.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetTechAnalysis(self, request, context):
        """Метод получения технических индикаторов по инструменту
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_MarketDataServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetCandles': grpc.unary_unary_rpc_method_handler(
                    servicer.GetCandles,
                    request_deserializer=marketdata__pb2.GetCandlesRequest.FromString,
                    response_serializer=marketdata__pb2.GetCandlesResponse.SerializeToString,
            ),
            'GetLastPrices': grpc.unary_unary_rpc_method_handler(
                    servicer.GetLastPrices,
                    request_deserializer=marketdata__pb2.GetLastPricesRequest.FromString,
                    response_serializer=marketdata__pb2.GetLastPricesResponse.SerializeToString,
            ),
            'GetOrderBook': grpc.unary_unary_rpc_method_handler(
                    servicer.GetOrderBook,
                    request_deserializer=marketdata__pb2.GetOrderBookRequest.FromString,
                    response_serializer=marketdata__pb2.GetOrderBookResponse.SerializeToString,
            ),
            'GetTradingStatus': grpc.unary_unary_rpc_method_handler(
                    servicer.GetTradingStatus,
                    request_deserializer=marketdata__pb2.GetTradingStatusRequest.FromString,
                    response_serializer=marketdata__pb2.GetTradingStatusResponse.SerializeToString,
            ),
            'GetTradingStatuses': grpc.unary_unary_rpc_method_handler(
                    servicer.GetTradingStatuses,
                    request_deserializer=marketdata__pb2.GetTradingStatusesRequest.FromString,
                    response_serializer=marketdata__pb2.GetTradingStatusesResponse.SerializeToString,
            ),
            'GetLastTrades': grpc.unary_unary_rpc_method_handler(
                    servicer.GetLastTrades,
                    request_deserializer=marketdata__pb2.GetLastTradesRequest.FromString,
                    response_serializer=marketdata__pb2.GetLastTradesResponse.SerializeToString,
            ),
            'GetClosePrices': grpc.unary_unary_rpc_method_handler(
                    servicer.GetClosePrices,
                    request_deserializer=marketdata__pb2.GetClosePricesRequest.FromString,
                    response_serializer=marketdata__pb2.GetClosePricesResponse.SerializeToString,
            ),
            'GetTechAnalysis': grpc.unary_unary_rpc_method_handler(
                    servicer.GetTechAnalysis,
                    request_deserializer=marketdata__pb2.GetTechAnalysisRequest.FromString,
                    response_serializer=marketdata__pb2.GetTechAnalysisResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'tinkoff.public.invest.api.contract.v1.MarketDataService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class MarketDataService(object):
    """Сервис получения биржевой информации:</br> **1**. свечи;</br> **2**. стаканы;</br> **3**. торговые статусы;</br> **4**. лента сделок.
    """

    @staticmethod
    def GetCandles(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/tinkoff.public.invest.api.contract.v1.MarketDataService/GetCandles',
            marketdata__pb2.GetCandlesRequest.SerializeToString,
            marketdata__pb2.GetCandlesResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetLastPrices(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/tinkoff.public.invest.api.contract.v1.MarketDataService/GetLastPrices',
            marketdata__pb2.GetLastPricesRequest.SerializeToString,
            marketdata__pb2.GetLastPricesResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetOrderBook(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/tinkoff.public.invest.api.contract.v1.MarketDataService/GetOrderBook',
            marketdata__pb2.GetOrderBookRequest.SerializeToString,
            marketdata__pb2.GetOrderBookResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetTradingStatus(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/tinkoff.public.invest.api.contract.v1.MarketDataService/GetTradingStatus',
            marketdata__pb2.GetTradingStatusRequest.SerializeToString,
            marketdata__pb2.GetTradingStatusResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetTradingStatuses(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/tinkoff.public.invest.api.contract.v1.MarketDataService/GetTradingStatuses',
            marketdata__pb2.GetTradingStatusesRequest.SerializeToString,
            marketdata__pb2.GetTradingStatusesResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetLastTrades(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/tinkoff.public.invest.api.contract.v1.MarketDataService/GetLastTrades',
            marketdata__pb2.GetLastTradesRequest.SerializeToString,
            marketdata__pb2.GetLastTradesResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetClosePrices(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/tinkoff.public.invest.api.contract.v1.MarketDataService/GetClosePrices',
            marketdata__pb2.GetClosePricesRequest.SerializeToString,
            marketdata__pb2.GetClosePricesResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetTechAnalysis(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/tinkoff.public.invest.api.contract.v1.MarketDataService/GetTechAnalysis',
            marketdata__pb2.GetTechAnalysisRequest.SerializeToString,
            marketdata__pb2.GetTechAnalysisResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class MarketDataStreamServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.MarketDataStream = channel.stream_stream(
                '/tinkoff.public.invest.api.contract.v1.MarketDataStreamService/MarketDataStream',
                request_serializer=marketdata__pb2.MarketDataRequest.SerializeToString,
                response_deserializer=marketdata__pb2.MarketDataResponse.FromString,
                )
        self.MarketDataServerSideStream = channel.unary_stream(
                '/tinkoff.public.invest.api.contract.v1.MarketDataStreamService/MarketDataServerSideStream',
                request_serializer=marketdata__pb2.MarketDataServerSideStreamRequest.SerializeToString,
                response_deserializer=marketdata__pb2.MarketDataResponse.FromString,
                )


class MarketDataStreamServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def MarketDataStream(self, request_iterator, context):
        """Bi-directional стрим предоставления биржевой информации.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def MarketDataServerSideStream(self, request, context):
        """Server-side стрим предоставления биржевой информации.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_MarketDataStreamServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'MarketDataStream': grpc.stream_stream_rpc_method_handler(
                    servicer.MarketDataStream,
                    request_deserializer=marketdata__pb2.MarketDataRequest.FromString,
                    response_serializer=marketdata__pb2.MarketDataResponse.SerializeToString,
            ),
            'MarketDataServerSideStream': grpc.unary_stream_rpc_method_handler(
                    servicer.MarketDataServerSideStream,
                    request_deserializer=marketdata__pb2.MarketDataServerSideStreamRequest.FromString,
                    response_serializer=marketdata__pb2.MarketDataResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'tinkoff.public.invest.api.contract.v1.MarketDataStreamService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class MarketDataStreamService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def MarketDataStream(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(request_iterator, target, '/tinkoff.public.invest.api.contract.v1.MarketDataStreamService/MarketDataStream',
            marketdata__pb2.MarketDataRequest.SerializeToString,
            marketdata__pb2.MarketDataResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def MarketDataServerSideStream(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/tinkoff.public.invest.api.contract.v1.MarketDataStreamService/MarketDataServerSideStream',
            marketdata__pb2.MarketDataServerSideStreamRequest.SerializeToString,
            marketdata__pb2.MarketDataResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
