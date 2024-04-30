# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: common.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0c\x63ommon.proto\x12%tinkoff.public.invest.api.contract.v1\x1a\x1fgoogle/protobuf/timestamp.proto\";\n\nMoneyValue\x12\x10\n\x08\x63urrency\x18\x01 \x01(\t\x12\r\n\x05units\x18\x02 \x01(\x03\x12\x0c\n\x04nano\x18\x03 \x01(\x05\"(\n\tQuotation\x12\r\n\x05units\x18\x01 \x01(\x03\x12\x0c\n\x04nano\x18\x02 \x01(\x05\"C\n\x04Ping\x12(\n\x04time\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x11\n\tstream_id\x18\x02 \x01(\t\"*\n\x04Page\x12\r\n\x05limit\x18\x01 \x01(\x05\x12\x13\n\x0bpage_number\x18\x02 \x01(\x05\"G\n\x0cPageResponse\x12\r\n\x05limit\x18\x01 \x01(\x05\x12\x13\n\x0bpage_number\x18\x02 \x01(\x05\x12\x13\n\x0btotal_count\x18\x03 \x01(\x05\"X\n\x10ResponseMetadata\x12\x13\n\x0btracking_id\x18* \x01(\t\x12/\n\x0bserver_time\x18+ \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"K\n\tBrandData\x12\x11\n\tlogo_name\x18\x01 \x01(\t\x12\x17\n\x0flogo_base_color\x18\x02 \x01(\t\x12\x12\n\ntext_color\x18\x03 \x01(\t*\xd2\x02\n\x0eInstrumentType\x12\x1f\n\x1bINSTRUMENT_TYPE_UNSPECIFIED\x10\x00\x12\x18\n\x14INSTRUMENT_TYPE_BOND\x10\x01\x12\x19\n\x15INSTRUMENT_TYPE_SHARE\x10\x02\x12\x1c\n\x18INSTRUMENT_TYPE_CURRENCY\x10\x03\x12\x17\n\x13INSTRUMENT_TYPE_ETF\x10\x04\x12\x1b\n\x17INSTRUMENT_TYPE_FUTURES\x10\x05\x12\x16\n\x12INSTRUMENT_TYPE_SP\x10\x06\x12\x1a\n\x16INSTRUMENT_TYPE_OPTION\x10\x07\x12(\n$INSTRUMENT_TYPE_CLEARING_CERTIFICATE\x10\x08\x12\x19\n\x15INSTRUMENT_TYPE_INDEX\x10\t\x12\x1d\n\x19INSTRUMENT_TYPE_COMMODITY\x10\n*\xce\x06\n\x15SecurityTradingStatus\x12\'\n#SECURITY_TRADING_STATUS_UNSPECIFIED\x10\x00\x12\x35\n1SECURITY_TRADING_STATUS_NOT_AVAILABLE_FOR_TRADING\x10\x01\x12*\n&SECURITY_TRADING_STATUS_OPENING_PERIOD\x10\x02\x12*\n&SECURITY_TRADING_STATUS_CLOSING_PERIOD\x10\x03\x12,\n(SECURITY_TRADING_STATUS_BREAK_IN_TRADING\x10\x04\x12*\n&SECURITY_TRADING_STATUS_NORMAL_TRADING\x10\x05\x12+\n\'SECURITY_TRADING_STATUS_CLOSING_AUCTION\x10\x06\x12-\n)SECURITY_TRADING_STATUS_DARK_POOL_AUCTION\x10\x07\x12,\n(SECURITY_TRADING_STATUS_DISCRETE_AUCTION\x10\x08\x12\x32\n.SECURITY_TRADING_STATUS_OPENING_AUCTION_PERIOD\x10\t\x12<\n8SECURITY_TRADING_STATUS_TRADING_AT_CLOSING_AUCTION_PRICE\x10\n\x12,\n(SECURITY_TRADING_STATUS_SESSION_ASSIGNED\x10\x0b\x12)\n%SECURITY_TRADING_STATUS_SESSION_CLOSE\x10\x0c\x12(\n$SECURITY_TRADING_STATUS_SESSION_OPEN\x10\r\x12\x31\n-SECURITY_TRADING_STATUS_DEALER_NORMAL_TRADING\x10\x0e\x12\x33\n/SECURITY_TRADING_STATUS_DEALER_BREAK_IN_TRADING\x10\x0f\x12<\n8SECURITY_TRADING_STATUS_DEALER_NOT_AVAILABLE_FOR_TRADING\x10\x10*V\n\tPriceType\x12\x1a\n\x16PRICE_TYPE_UNSPECIFIED\x10\x00\x12\x14\n\x10PRICE_TYPE_POINT\x10\x01\x12\x17\n\x13PRICE_TYPE_CURRENCY\x10\x02\x42\x61\n\x1cru.tinkoff.piapi.contract.v1P\x01Z\x0c./;investapi\xa2\x02\x05TIAPI\xaa\x02\x14Tinkoff.InvestApi.V1\xca\x02\x11Tinkoff\\Invest\\V1b\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'common_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  _globals['DESCRIPTOR']._options = None
  _globals['DESCRIPTOR']._serialized_options = b'\n\034ru.tinkoff.piapi.contract.v1P\001Z\014./;investapi\242\002\005TIAPI\252\002\024Tinkoff.InvestApi.V1\312\002\021Tinkoff\\Invest\\V1'
  _globals['_INSTRUMENTTYPE']._serialized_start=545
  _globals['_INSTRUMENTTYPE']._serialized_end=883
  _globals['_SECURITYTRADINGSTATUS']._serialized_start=886
  _globals['_SECURITYTRADINGSTATUS']._serialized_end=1732
  _globals['_PRICETYPE']._serialized_start=1734
  _globals['_PRICETYPE']._serialized_end=1820
  _globals['_MONEYVALUE']._serialized_start=88
  _globals['_MONEYVALUE']._serialized_end=147
  _globals['_QUOTATION']._serialized_start=149
  _globals['_QUOTATION']._serialized_end=189
  _globals['_PING']._serialized_start=191
  _globals['_PING']._serialized_end=258
  _globals['_PAGE']._serialized_start=260
  _globals['_PAGE']._serialized_end=302
  _globals['_PAGERESPONSE']._serialized_start=304
  _globals['_PAGERESPONSE']._serialized_end=375
  _globals['_RESPONSEMETADATA']._serialized_start=377
  _globals['_RESPONSEMETADATA']._serialized_end=465
  _globals['_BRANDDATA']._serialized_start=467
  _globals['_BRANDDATA']._serialized_end=542
# @@protoc_insertion_point(module_scope)
