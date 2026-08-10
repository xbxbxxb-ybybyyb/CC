from enum import Enum, unique


@unique
class DataType(Enum):
    STATUS = 0,
    ORDER = 1,
    TRADE = 2,
    CANCEL = 3,
    TICK1S = 4,
    TICKFULL = 5,
    TICKEX = 6,
    KLINE1MIN = 7,
    DAILYDATA = 8,
    FACTOR = 9,
    FUTURETICKEX = 10,
    INDEXTICKEX = 11,
    ENHANCEDTRADE = 12,
    STATICINFO = 13,
    TICK3S = 14,
    ETFCREATIONREDEMPTIONINFO = 15

