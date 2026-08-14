from enum import IntEnum
from typing import Type, Tuple
from alphagen_qlib.stock_data import FeatureType
from alphagen.data.expression import Operator

'''
定义好了token，用来包裹算子/特征/常数/筛选条件/开始/结束
'''

class SequenceIndicatorType(IntEnum):
    BEG = 0
    SEP = 1


class Token:
    def __repr__(self):
        return str(self)


class ConstantToken(Token):
    def __init__(self, constant: float) -> None:
        self.constant = constant

    def __str__(self): return str(self.constant)

class DivRuleToken(Token):
    def __init__(self, div_rule: str) -> None:
        self.div_rule = div_rule

    def __str__(self): return str(self.div_rule)

class BinaryDivRuleToken(Token):
    def __init__(self, binary_div_rule: str) -> None:
        self.binary_div_rule = binary_div_rule

    def __str__(self): return str(self.binary_div_rule)


class GetConstantToken(Token):
    def __init__(self, get_constant: int) -> None:
        self.get_constant = get_constant

    def __str__(self): return str(self.get_constant)


class DeltaTimeToken(Token):
    def __init__(self, delta_time: str) -> None:
        self.delta_time = delta_time

    def __str__(self): return str(self.delta_time)


class FeatureToken(Token):
    def __init__(self, feature: FeatureType) -> None:
        self.feature = feature

    def __str__(self): return '$' + self.feature.name.lower()


class OperatorToken(Token):
    def __init__(self, operator: Type[Operator]) -> None:
        self.operator = operator

    def __str__(self): return self.operator.__name__


class SequenceIndicatorToken(Token):
    def __init__(self, indicator: SequenceIndicatorType) -> None:
        self.indicator = indicator

    def __str__(self): return self.indicator.name


BEG_TOKEN = SequenceIndicatorToken(SequenceIndicatorType.BEG)
SEP_TOKEN = SequenceIndicatorToken(SequenceIndicatorType.SEP)
