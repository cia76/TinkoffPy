# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from TinkoffPy.grpc import orders_pb2 as TinkoffPy_dot_grpc_dot_orders__pb2

GRPC_GENERATED_VERSION = '1.70.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in TinkoffPy/grpc/orders_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class OrdersStreamServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.TradesStream = channel.unary_stream(
                '/tinkoff.public.invest.api.contract.v1.OrdersStreamService/TradesStream',
                request_serializer=TinkoffPy_dot_grpc_dot_orders__pb2.TradesStreamRequest.SerializeToString,
                response_deserializer=TinkoffPy_dot_grpc_dot_orders__pb2.TradesStreamResponse.FromString,
                _registered_method=True)
        self.OrderStateStream = channel.unary_stream(
                '/tinkoff.public.invest.api.contract.v1.OrdersStreamService/OrderStateStream',
                request_serializer=TinkoffPy_dot_grpc_dot_orders__pb2.OrderStateStreamRequest.SerializeToString,
                response_deserializer=TinkoffPy_dot_grpc_dot_orders__pb2.OrderStateStreamResponse.FromString,
                _registered_method=True)


class OrdersStreamServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def TradesStream(self, request, context):
        """Stream сделок пользователя
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def OrderStateStream(self, request, context):
        """Stream поручений пользователя. Перед работой прочитайте [статью](./orders_state_stream/).
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_OrdersStreamServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'TradesStream': grpc.unary_stream_rpc_method_handler(
                    servicer.TradesStream,
                    request_deserializer=TinkoffPy_dot_grpc_dot_orders__pb2.TradesStreamRequest.FromString,
                    response_serializer=TinkoffPy_dot_grpc_dot_orders__pb2.TradesStreamResponse.SerializeToString,
            ),
            'OrderStateStream': grpc.unary_stream_rpc_method_handler(
                    servicer.OrderStateStream,
                    request_deserializer=TinkoffPy_dot_grpc_dot_orders__pb2.OrderStateStreamRequest.FromString,
                    response_serializer=TinkoffPy_dot_grpc_dot_orders__pb2.OrderStateStreamResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'tinkoff.public.invest.api.contract.v1.OrdersStreamService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('tinkoff.public.invest.api.contract.v1.OrdersStreamService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class OrdersStreamService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def TradesStream(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(
            request,
            target,
            '/tinkoff.public.invest.api.contract.v1.OrdersStreamService/TradesStream',
            TinkoffPy_dot_grpc_dot_orders__pb2.TradesStreamRequest.SerializeToString,
            TinkoffPy_dot_grpc_dot_orders__pb2.TradesStreamResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def OrderStateStream(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(
            request,
            target,
            '/tinkoff.public.invest.api.contract.v1.OrdersStreamService/OrderStateStream',
            TinkoffPy_dot_grpc_dot_orders__pb2.OrderStateStreamRequest.SerializeToString,
            TinkoffPy_dot_grpc_dot_orders__pb2.OrderStateStreamResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)


class OrdersServiceStub(object):
    """Сервис предназначен для работы с торговыми поручениями:<br/> **1**.
    выставление;<br/> **2**. отмена;<br/> **3**. получение статуса;<br/> **4**.
    расчет полной стоимости;<br/> **5**. получение списка заявок.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.PostOrder = channel.unary_unary(
                '/tinkoff.public.invest.api.contract.v1.OrdersService/PostOrder',
                request_serializer=TinkoffPy_dot_grpc_dot_orders__pb2.PostOrderRequest.SerializeToString,
                response_deserializer=TinkoffPy_dot_grpc_dot_orders__pb2.PostOrderResponse.FromString,
                _registered_method=True)
        self.PostOrderAsync = channel.unary_unary(
                '/tinkoff.public.invest.api.contract.v1.OrdersService/PostOrderAsync',
                request_serializer=TinkoffPy_dot_grpc_dot_orders__pb2.PostOrderAsyncRequest.SerializeToString,
                response_deserializer=TinkoffPy_dot_grpc_dot_orders__pb2.PostOrderAsyncResponse.FromString,
                _registered_method=True)
        self.CancelOrder = channel.unary_unary(
                '/tinkoff.public.invest.api.contract.v1.OrdersService/CancelOrder',
                request_serializer=TinkoffPy_dot_grpc_dot_orders__pb2.CancelOrderRequest.SerializeToString,
                response_deserializer=TinkoffPy_dot_grpc_dot_orders__pb2.CancelOrderResponse.FromString,
                _registered_method=True)
        self.GetOrderState = channel.unary_unary(
                '/tinkoff.public.invest.api.contract.v1.OrdersService/GetOrderState',
                request_serializer=TinkoffPy_dot_grpc_dot_orders__pb2.GetOrderStateRequest.SerializeToString,
                response_deserializer=TinkoffPy_dot_grpc_dot_orders__pb2.OrderState.FromString,
                _registered_method=True)
        self.GetOrders = channel.unary_unary(
                '/tinkoff.public.invest.api.contract.v1.OrdersService/GetOrders',
                request_serializer=TinkoffPy_dot_grpc_dot_orders__pb2.GetOrdersRequest.SerializeToString,
                response_deserializer=TinkoffPy_dot_grpc_dot_orders__pb2.GetOrdersResponse.FromString,
                _registered_method=True)
        self.ReplaceOrder = channel.unary_unary(
                '/tinkoff.public.invest.api.contract.v1.OrdersService/ReplaceOrder',
                request_serializer=TinkoffPy_dot_grpc_dot_orders__pb2.ReplaceOrderRequest.SerializeToString,
                response_deserializer=TinkoffPy_dot_grpc_dot_orders__pb2.PostOrderResponse.FromString,
                _registered_method=True)
        self.GetMaxLots = channel.unary_unary(
                '/tinkoff.public.invest.api.contract.v1.OrdersService/GetMaxLots',
                request_serializer=TinkoffPy_dot_grpc_dot_orders__pb2.GetMaxLotsRequest.SerializeToString,
                response_deserializer=TinkoffPy_dot_grpc_dot_orders__pb2.GetMaxLotsResponse.FromString,
                _registered_method=True)
        self.GetOrderPrice = channel.unary_unary(
                '/tinkoff.public.invest.api.contract.v1.OrdersService/GetOrderPrice',
                request_serializer=TinkoffPy_dot_grpc_dot_orders__pb2.GetOrderPriceRequest.SerializeToString,
                response_deserializer=TinkoffPy_dot_grpc_dot_orders__pb2.GetOrderPriceResponse.FromString,
                _registered_method=True)


class OrdersServiceServicer(object):
    """Сервис предназначен для работы с торговыми поручениями:<br/> **1**.
    выставление;<br/> **2**. отмена;<br/> **3**. получение статуса;<br/> **4**.
    расчет полной стоимости;<br/> **5**. получение списка заявок.
    """

    def PostOrder(self, request, context):
        """Метод выставления заявки.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def PostOrderAsync(self, request, context):
        """Асинхронный метод выставления заявки.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CancelOrder(self, request, context):
        """Метод отмены биржевой заявки.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetOrderState(self, request, context):
        """Метод получения статуса торгового поручения.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetOrders(self, request, context):
        """Метод получения списка активных заявок по счету.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ReplaceOrder(self, request, context):
        """Метод изменения выставленной заявки.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetMaxLots(self, request, context):
        """расчет количества доступных для покупки/продажи лотов
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetOrderPrice(self, request, context):
        """Метод получения предварительной стоимости для лимитной заявки
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_OrdersServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'PostOrder': grpc.unary_unary_rpc_method_handler(
                    servicer.PostOrder,
                    request_deserializer=TinkoffPy_dot_grpc_dot_orders__pb2.PostOrderRequest.FromString,
                    response_serializer=TinkoffPy_dot_grpc_dot_orders__pb2.PostOrderResponse.SerializeToString,
            ),
            'PostOrderAsync': grpc.unary_unary_rpc_method_handler(
                    servicer.PostOrderAsync,
                    request_deserializer=TinkoffPy_dot_grpc_dot_orders__pb2.PostOrderAsyncRequest.FromString,
                    response_serializer=TinkoffPy_dot_grpc_dot_orders__pb2.PostOrderAsyncResponse.SerializeToString,
            ),
            'CancelOrder': grpc.unary_unary_rpc_method_handler(
                    servicer.CancelOrder,
                    request_deserializer=TinkoffPy_dot_grpc_dot_orders__pb2.CancelOrderRequest.FromString,
                    response_serializer=TinkoffPy_dot_grpc_dot_orders__pb2.CancelOrderResponse.SerializeToString,
            ),
            'GetOrderState': grpc.unary_unary_rpc_method_handler(
                    servicer.GetOrderState,
                    request_deserializer=TinkoffPy_dot_grpc_dot_orders__pb2.GetOrderStateRequest.FromString,
                    response_serializer=TinkoffPy_dot_grpc_dot_orders__pb2.OrderState.SerializeToString,
            ),
            'GetOrders': grpc.unary_unary_rpc_method_handler(
                    servicer.GetOrders,
                    request_deserializer=TinkoffPy_dot_grpc_dot_orders__pb2.GetOrdersRequest.FromString,
                    response_serializer=TinkoffPy_dot_grpc_dot_orders__pb2.GetOrdersResponse.SerializeToString,
            ),
            'ReplaceOrder': grpc.unary_unary_rpc_method_handler(
                    servicer.ReplaceOrder,
                    request_deserializer=TinkoffPy_dot_grpc_dot_orders__pb2.ReplaceOrderRequest.FromString,
                    response_serializer=TinkoffPy_dot_grpc_dot_orders__pb2.PostOrderResponse.SerializeToString,
            ),
            'GetMaxLots': grpc.unary_unary_rpc_method_handler(
                    servicer.GetMaxLots,
                    request_deserializer=TinkoffPy_dot_grpc_dot_orders__pb2.GetMaxLotsRequest.FromString,
                    response_serializer=TinkoffPy_dot_grpc_dot_orders__pb2.GetMaxLotsResponse.SerializeToString,
            ),
            'GetOrderPrice': grpc.unary_unary_rpc_method_handler(
                    servicer.GetOrderPrice,
                    request_deserializer=TinkoffPy_dot_grpc_dot_orders__pb2.GetOrderPriceRequest.FromString,
                    response_serializer=TinkoffPy_dot_grpc_dot_orders__pb2.GetOrderPriceResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'tinkoff.public.invest.api.contract.v1.OrdersService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('tinkoff.public.invest.api.contract.v1.OrdersService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class OrdersService(object):
    """Сервис предназначен для работы с торговыми поручениями:<br/> **1**.
    выставление;<br/> **2**. отмена;<br/> **3**. получение статуса;<br/> **4**.
    расчет полной стоимости;<br/> **5**. получение списка заявок.
    """

    @staticmethod
    def PostOrder(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/tinkoff.public.invest.api.contract.v1.OrdersService/PostOrder',
            TinkoffPy_dot_grpc_dot_orders__pb2.PostOrderRequest.SerializeToString,
            TinkoffPy_dot_grpc_dot_orders__pb2.PostOrderResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def PostOrderAsync(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/tinkoff.public.invest.api.contract.v1.OrdersService/PostOrderAsync',
            TinkoffPy_dot_grpc_dot_orders__pb2.PostOrderAsyncRequest.SerializeToString,
            TinkoffPy_dot_grpc_dot_orders__pb2.PostOrderAsyncResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def CancelOrder(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/tinkoff.public.invest.api.contract.v1.OrdersService/CancelOrder',
            TinkoffPy_dot_grpc_dot_orders__pb2.CancelOrderRequest.SerializeToString,
            TinkoffPy_dot_grpc_dot_orders__pb2.CancelOrderResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetOrderState(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/tinkoff.public.invest.api.contract.v1.OrdersService/GetOrderState',
            TinkoffPy_dot_grpc_dot_orders__pb2.GetOrderStateRequest.SerializeToString,
            TinkoffPy_dot_grpc_dot_orders__pb2.OrderState.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetOrders(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/tinkoff.public.invest.api.contract.v1.OrdersService/GetOrders',
            TinkoffPy_dot_grpc_dot_orders__pb2.GetOrdersRequest.SerializeToString,
            TinkoffPy_dot_grpc_dot_orders__pb2.GetOrdersResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ReplaceOrder(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/tinkoff.public.invest.api.contract.v1.OrdersService/ReplaceOrder',
            TinkoffPy_dot_grpc_dot_orders__pb2.ReplaceOrderRequest.SerializeToString,
            TinkoffPy_dot_grpc_dot_orders__pb2.PostOrderResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetMaxLots(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/tinkoff.public.invest.api.contract.v1.OrdersService/GetMaxLots',
            TinkoffPy_dot_grpc_dot_orders__pb2.GetMaxLotsRequest.SerializeToString,
            TinkoffPy_dot_grpc_dot_orders__pb2.GetMaxLotsResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetOrderPrice(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/tinkoff.public.invest.api.contract.v1.OrdersService/GetOrderPrice',
            TinkoffPy_dot_grpc_dot_orders__pb2.GetOrderPriceRequest.SerializeToString,
            TinkoffPy_dot_grpc_dot_orders__pb2.GetOrderPriceResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
