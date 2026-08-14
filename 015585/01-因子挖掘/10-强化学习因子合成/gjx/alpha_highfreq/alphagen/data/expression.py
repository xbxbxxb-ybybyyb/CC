from abc import ABCMeta, abstractmethod
from typing import List, Type, Union, Tuple

import torch
from torch import Tensor

from alphagen_qlib.stock_data import StockData, FeatureType

'''
定义了全部的算子
'''

class OutOfDataRangeError(IndexError):
    pass


class Expression(metaclass=ABCMeta):
    @abstractmethod
    def evaluate(self, data: StockData, *args) -> Tensor:
        ...

    # 内置好了，可以自动把/识别为__truediv__，*识别为__mul__等
    def __repr__(self) -> str:
        return str(self)

    def __add__(self, other: Union["Expression", float]) -> "Add":
        if isinstance(other, Expression):
            return Add(self, other)
        else:
            return Add(self, Constant(other))

    def __radd__(self, other: float) -> "Add":
        return Add(Constant(other), self)

    def __sub__(self, other: Union["Expression", float]) -> "Sub":
        if isinstance(other, Expression):
            return Sub(self, other)
        else:
            return Sub(self, Constant(other))

    def __rsub__(self, other: float) -> "Sub":
        return Sub(Constant(other), self)

    def __mul__(self, other: Union["Expression", float]) -> "Mul":
        if isinstance(other, Expression):
            return Mul(self, other)
        else:
            return Mul(self, Constant(other))

    def __rmul__(self, other: float) -> "Mul":
        return Mul(Constant(other), self)

    def __truediv__(self, other: Union["Expression", float]) -> "Div":
        if isinstance(other, Expression):
            return Div(self, other)
        else:
            return Div(self, Constant(other))

    def __rtruediv__(self, other: float) -> "Div":
        return Div(Constant(other), self)

    def __pow__(self, other: Union["Expression", float]) -> "Pow":
        if isinstance(other, Expression):
            return Pow(self, other)
        else:
            return Pow(self, Constant(other))

    def __rpow__(self, other: float) -> "Pow":
        return Pow(Constant(other), self)

    def __pos__(self) -> "Expression":
        return self

    def __neg__(self) -> "Sub":
        return Sub(Constant(0), self)

    def __abs__(self) -> "Abs":
        return Abs(self)

    @property
    def is_featured(self):
        raise NotImplementedError

    @property
    def is_timeserie(self):
        raise NotImplementedError


class Feature(Expression):
    def __init__(self, feature: FeatureType) -> None:
        self._feature = feature
        self.init_list = []

    def evaluate(self, data: StockData) -> Tensor:
        start1 = data.max_backtrack_days  # 这里是怕多取了一些天
        stop1 = data.max_backtrack_days + data.n_days
        return data.data[start1:stop1, :, int(self._feature), :]


    def __str__(self) -> str: return '$' + self._feature.name.lower()

    @property
    def is_featured(self): return True
    # 是否是特征

    @property
    def feature_units(self):
        # 定义量纲
        if self._feature.value in [FeatureType.LastPx.value, FeatureType.HighPx.value, FeatureType.LowPx.value, FeatureType.WeightedAvgBidPx.value,
                             FeatureType.WeightedAvgOfferPx.value, FeatureType.Buy1Price.value, FeatureType.Buy2Price.value, FeatureType.Sell1Price.value,
                                  FeatureType.Sell2Price.value]:
            return 'curr_ret'
        elif self._feature.value in [FeatureType.TotalVolumeTrade.value, FeatureType.TotalBidQty.value, FeatureType.TotalOfferQty.value
                                    , FeatureType.Buy1OrderQty.value, FeatureType.Buy2OrderQty.value, FeatureType.Sell1OrderQty.value,
                                    FeatureType.Sell2OrderQty.value, FeatureType.ff_shares.value]:
            return 'shares'
        elif self._feature.value in [FeatureType.TotalValueTrade.value,FeatureType.pre_close.value]:
            return 'curr'
        elif self._feature.value in [FeatureType.NumTrades.value, FeatureType.Buy1NumOrders.value, FeatureType.Buy2NumOrders.value
                                    , FeatureType.Sell1NumOrders.value, FeatureType.Sell2NumOrders.value]:
            return 'unit'

    @property
    def is_timeserie(self): return True
    # 是否是三维数据

    @property
    def filter_type(self): return self.init_list
    # 目前为止的筛选条件:[]


class Constant(Expression):
    def __init__(self, value: float) -> None:
        self._value = value

    def evaluate(self, data: StockData) -> Tensor:
        # if (period.start < -data.max_backtrack_days or
        #         period.stop - 1 > data.max_future_days):
        #     raise OutOfDataRangeError()
        device = data.data.device
        dtype = data.data.dtype
        return torch.full(size=(data.n_days, data.n_stocks),
                          fill_value=self._value, dtype=dtype, device=device)  # 搁后面广播一下就行


    def __str__(self) -> str: return f'Constant({str(self._value)})'

    @property
    def is_featured(self): return False

    @property
    def is_timeserie(self): return True


class GetConstant(Expression):
    # 获取某个时刻的数据的算子的输入，取值为['93000','93100','93500','93900','93957']
    def __init__(self, get_constant: str) -> None:
        self._get_constant = get_constant

    def evaluate(self, data: StockData, period: slice = slice(0, 1)) -> Tensor:
        assert False, "Should not call evaluate on GetConstant"

    def __str__(self) -> str: return str(self.get_constant)

    @property
    def is_featured(self): return False

    @property
    def is_timeserie(self): return False


class DivRule(Expression):
    # 筛选条件
    def __init__(self, div_rule: str) -> None:
        self._div_rule = div_rule

    def evaluate(self, data: StockData) -> Tensor:
        assert False, "Should not call evaluate on delta time"

    def __str__(self) -> str: return str(self._div_rule)

    @property
    def is_featured(self): return False


class BinaryDivRule(Expression):
    # 一个特征根据另一个特征筛选时的筛选条件
    def __init__(self, div_rule: str) -> None:
        self._div_rule = div_rule

    def evaluate(self, data: StockData) -> Tensor:
        assert False, "Should not call evaluate on delta time"

    def __str__(self) -> str: return str(self._div_rule)

    @property
    def is_featured(self): return False


# Operator base classes
class Operator(Expression):
    @classmethod
    @abstractmethod
    def n_args(cls) -> int: ...

    @classmethod
    @abstractmethod
    def category_type(cls) -> Type['Operator']: ...


class UnaryOperator(Operator):
    # 一元算子
    def __init__(self, operand: Union[Expression, float]) -> None:
        self._operand = operand if isinstance(operand, Expression) else Constant(operand)
        self.init_list = self._operand.init_list

    @classmethod
    def n_args(cls) -> int: return 1

    @classmethod
    def category_type(cls) -> Type['Operator']: return UnaryOperator

    def evaluate(self, data: StockData) -> Tensor:
        return self._apply(self._operand.evaluate(data))  # self._operand可能是时序算子的其实

    @abstractmethod
    def _apply(self, operand: Tensor) -> Tensor: ...

    def __str__(self) -> str:
        return f"{type(self).__name__}({self._operand})"

    @property
    def is_featured(self): return self._operand.is_featured
    # 输入是特征，输出还是特征

    @property
    def is_timeserie(self): return self._operand.is_timeserie
    # 输入是多少维现在输出还是多少维

    @property
    def filter_type(self): return self._operand.filter_type
    # 并不会改变目前为止的筛选条件列表

    @property
    def feature_units(self):
        # 不会改变原本的量纲
        if str(self._operand) in [str(Feature(FeatureType.LastPx)), str(Feature(FeatureType.HighPx)),
                                  str(Feature(FeatureType.LowPx)), str(Feature(FeatureType.WeightedAvgBidPx)),
                                  str(Feature(FeatureType.WeightedAvgOfferPx)), str(Feature(FeatureType.Buy1Price)),
                                  str(Feature(FeatureType.Buy2Price)), str(Feature(FeatureType.Sell1Price)),
                                  str(Feature(FeatureType.Sell2Price))]:
            return 'curr_ret'
        elif str(self._operand) in [str(Feature(FeatureType.TotalVolumeTrade)), str(Feature(FeatureType.TotalBidQty)),
                                    str(Feature(FeatureType.TotalOfferQty))
            , str(Feature(FeatureType.Buy1OrderQty)), str(Feature(FeatureType.Buy2OrderQty)),
                                    str(Feature(FeatureType.Sell1OrderQty)),
                                    str(Feature(FeatureType.Sell2OrderQty)), str(Feature(FeatureType.ff_shares))]:
            return 'shares'
        elif str(self._operand) in [str(Feature(FeatureType.TotalValueTrade)), str(Feature(FeatureType.pre_close))]:
            return 'curr'
        elif str(self._operand) in [str(Feature(FeatureType.NumTrades)), str(Feature(FeatureType.Buy1NumOrders)),
                                    str(Feature(FeatureType.Buy2NumOrders))
            , str(Feature(FeatureType.Sell1NumOrders)), str(Feature(FeatureType.Sell2NumOrders))]:
            return 'unit'


class FilterOperator(Operator):
    # 一元算子：根据特定的条件进行筛选
    def __init__(self, operand: Union[Expression, float], div_rule: [str,DivRule]) -> None:
        self._operand = operand if isinstance(operand, Expression) else Constant(operand)
        self._div_rule = str(div_rule)
        self.init_list = self._operand.init_list
        self.init_list.append(self._div_rule)
        self._idx1, self._idx2 = None, None

    @classmethod
    def n_args(cls) -> int: return 2

    @classmethod
    def category_type(cls) -> Type['Operator']: return Filter

    def evaluate(self, data: StockData) -> Tensor:
        # L: period length (requested time window length)
        # W: window length (dt for rolling)
        # S: stock count
        values = self._operand.evaluate(data)   # (L+W-1, S)
        # values = values.unfold(0, self._delta_time, 1)              # (L, S, W)
        if self._div_rule in ['[93000,93100]','[93900,93957]','[93000,93500]','[93500,93957]']: # 如果是筛选时间片段，可以获取对应的时刻在数据中的索引
            t1, t2 = self._div_rule[1:-1].split(',')
            self._idx1, self._idx2 = data.get_time_idx(t1, t2)
        return self._apply(values)                                # (L, S)

    @abstractmethod
    def _apply(self, operand: Tensor) -> Tensor: ...

    def __str__(self) -> str:
        return f"{type(self).__name__}({self._operand},{self._div_rule})"

    @property
    def is_featured(self): return self._operand.is_featured

    @property
    def filter_type(self):
        # 到目前为止的筛选列表需要更新，添加当前的筛选条件
        return self.init_list

    @property
    def is_timeserie(self): return self._operand.is_timeserie
    # 如果是被filter处理过的数据经过时序算子，则1）不需要unfold那一步 2）计算的时候可以忽略nan，比如60个数据里有nan
    @property
    def feature_units(self):
        if str(self._operand) in [str(Feature(FeatureType.LastPx)), str(Feature(FeatureType.HighPx)),
                                  str(Feature(FeatureType.LowPx)), str(Feature(FeatureType.WeightedAvgBidPx)),
                                  str(Feature(FeatureType.WeightedAvgOfferPx)), str(Feature(FeatureType.Buy1Price)),
                                  str(Feature(FeatureType.Buy2Price)), str(Feature(FeatureType.Sell1Price)),
                                  str(Feature(FeatureType.Sell2Price))]:
            return 'curr_ret'
        elif str(self._operand) in [str(Feature(FeatureType.TotalVolumeTrade)), str(Feature(FeatureType.TotalBidQty)),
                                    str(Feature(FeatureType.TotalOfferQty))
            , str(Feature(FeatureType.Buy1OrderQty)), str(Feature(FeatureType.Buy2OrderQty)),
                                    str(Feature(FeatureType.Sell1OrderQty)),
                                    str(Feature(FeatureType.Sell2OrderQty)), str(Feature(FeatureType.ff_shares))]:
            return 'shares'
        elif str(self._operand) in [str(Feature(FeatureType.TotalValueTrade)), str(Feature(FeatureType.pre_close))]:
            return 'curr'
        elif str(self._operand) in [str(Feature(FeatureType.NumTrades)), str(Feature(FeatureType.Buy1NumOrders)),
                                    str(Feature(FeatureType.Buy2NumOrders))
            , str(Feature(FeatureType.Sell1NumOrders)), str(Feature(FeatureType.Sell2NumOrders))]:
            return 'unit'


class BinaryFilterOperator(Operator):
    # 二元筛选算子，一个特征根据另一个特征筛选
    def __init__(self, operand1: Union[Expression, float], operand2: Union[Expression, float], div_rule: [str,BinaryDivRule]) -> None:
        self._operand1 = operand1 if isinstance(operand1, Expression) else Constant(operand1)
        self._operand2 = operand1 if isinstance(operand2, Expression) else Constant(operand2)
        self._div_rule = str(div_rule)
        self.init_list = self._operand1.init_list
        self.init_list.append(self._div_rule)

    @classmethod
    def n_args(cls) -> int: return 3

    @classmethod
    def category_type(cls) -> Type['Operator']: return BinaryFilter  # 额这里一定要记得改，不然在valid里会有大问题

    def evaluate(self, data: StockData) -> Tensor:
        # L: period length (requested time window length)
        # W: window length (dt for rolling)
        # S: stock count
        values1 = self._operand1.evaluate(data)   # (L+W-1, S)
        values2 = self._operand1.evaluate(data)  # (L+W-1, S)

        return self._apply(values1, values2)                                  # (L, S)

    @abstractmethod
    def _apply(self, operand1: Tensor, operand2: Tensor) -> Tensor: ...

    def __str__(self) -> str:
        return f"{type(self).__name__}({self._operand1},{self._operand2}, {self._div_rule})"

    @property
    def is_featured(self): return self._operand1.is_featured

    @property
    def filter_type(self):
        return self.init_list

    @property
    def is_timeserie(self): return self._operand1.is_timeserie
    # 如果是被filter处理过的数据经过时序算子，则1）不需要unfold那一步 2）计算的时候可以忽略nan，比如60个数据里有nan
    # 那么求均值时对剩下的30个求即可，分母也是30

    # 会改变单位的算子比如sign可以单独在定义里面设置为other
    @property
    def feature_units(self):
        if str(self._operand1) in [str(Feature(FeatureType.LastPx)), str(Feature(FeatureType.HighPx)),
                                  str(Feature(FeatureType.LowPx)), str(Feature(FeatureType.WeightedAvgBidPx)),
                                  str(Feature(FeatureType.WeightedAvgOfferPx)), str(Feature(FeatureType.Buy1Price)),
                                  str(Feature(FeatureType.Buy2Price)), str(Feature(FeatureType.Sell1Price)),
                                  str(Feature(FeatureType.Sell2Price))]:
            return 'curr_ret'
        elif str(self._operand1) in [str(Feature(FeatureType.TotalVolumeTrade)), str(Feature(FeatureType.TotalBidQty)),
                                    str(Feature(FeatureType.TotalOfferQty))
            , str(Feature(FeatureType.Buy1OrderQty)), str(Feature(FeatureType.Buy2OrderQty)),
                                    str(Feature(FeatureType.Sell1OrderQty)),
                                    str(Feature(FeatureType.Sell2OrderQty)), str(Feature(FeatureType.ff_shares))]:
            return 'shares'
        elif str(self._operand1) in [str(Feature(FeatureType.TotalValueTrade)), str(Feature(FeatureType.pre_close))]:
            return 'curr'
        elif str(self._operand1) in [str(Feature(FeatureType.NumTrades)), str(Feature(FeatureType.Buy1NumOrders)),
                                    str(Feature(FeatureType.Buy2NumOrders))
            , str(Feature(FeatureType.Sell1NumOrders)), str(Feature(FeatureType.Sell2NumOrders))]:
            return 'unit'



class BinaryOperator(Operator):
    # 二元算子
    def __init__(self, lhs: Union[Expression, float], rhs: Union[Expression, float]) -> None:
        self._lhs = lhs if isinstance(lhs, Expression) else Constant(lhs)
        self._rhs = rhs if isinstance(rhs, Expression) else Constant(rhs)
        self.init_list = self._lhs.init_list if self._lhs.filter_type != 'SHOOT' else self._rhs.init_list

    @classmethod
    def n_args(cls) -> int: return 2

    @classmethod
    def category_type(cls) -> Type['Operator']: return BinaryOperator

    def evaluate(self, data: StockData) -> Tensor:
        return self._apply(self._lhs.evaluate(data), self._rhs.evaluate(data))

    @abstractmethod
    def _apply(self, lhs: Tensor, rhs: Tensor) -> Tensor: ...

    def __str__(self) -> str:
        return f"{type(self).__name__}({self._lhs},{self._rhs})"

    @property
    def is_featured(self): return self._lhs.is_featured or self._rhs.is_featured

    @property
    def filter_type(self): return self._lhs.filter_type if self._lhs.filter_type != 'SHOOT' else self._rhs.filter_type
    # 返回被筛选过的那个输入的筛选规则列表

    @property
    def is_timeserie(self): return self._lhs.is_timeserie or self._rhs.is_timeserie


class GetOperator(Operator):
    # 用于获取某个时刻数据的算子
    def __init__(self, operand: Union[Expression, float], get_constant: Union[str, GetConstant]) -> None:
        self._operand = operand if isinstance(operand, Expression) else Constant(operand)
        if isinstance(get_constant, GetConstant):
            get_constant = get_constant._get_constant
        self._get_constant= get_constant
        self.init_list = None
        self.idx = None

    @classmethod
    def n_args(cls) -> int: return 2

    @classmethod
    def category_type(cls) -> Type['Operator']: return GetOperator

    def evaluate(self, data: StockData) -> Tensor:
        values = self._operand.evaluate(data)  # (L,S,W) 用默认的slice
        self.idx = data.get_idx(self._get_constant)
        return self._apply(values)  # 返回原值即可，因为筛选的工作实际上要在feature里面完成

    @abstractmethod
    def _apply(self, operand: Tensor, get_constant: int) -> Tensor: ...

    def __str__(self) -> str:
        return f"{type(self).__name__}({self._operand},{self._get_constant})"

    @property
    def is_featured(self): return self._operand.is_featured

    @property
    def filter_type(self): return 'SHOOT'
    # 筛选列表清空

    @property
    def is_timeserie(self): return False

    @property
    def feature_units(self):
        if str(self._operand) in [str(Feature(FeatureType.LastPx)), str(Feature(FeatureType.HighPx)),
                                   str(Feature(FeatureType.LowPx)), str(Feature(FeatureType.WeightedAvgBidPx)),
                                   str(Feature(FeatureType.WeightedAvgOfferPx)), str(Feature(FeatureType.Buy1Price)),
                                   str(Feature(FeatureType.Buy2Price)), str(Feature(FeatureType.Sell1Price)),
                                   str(Feature(FeatureType.Sell2Price))]:
            return 'curr_ret'
        elif str(self._operand) in [str(Feature(FeatureType.TotalVolumeTrade)), str(Feature(FeatureType.TotalBidQty)),
                                     str(Feature(FeatureType.TotalOfferQty))
            , str(Feature(FeatureType.Buy1OrderQty)), str(Feature(FeatureType.Buy2OrderQty)),
                                     str(Feature(FeatureType.Sell1OrderQty)),
                                     str(Feature(FeatureType.Sell2OrderQty)), str(Feature(FeatureType.ff_shares))]:
            return 'shares'
        elif str(self._operand) in [str(Feature(FeatureType.TotalValueTrade)), str(Feature(FeatureType.pre_close))]:
            return 'curr'
        elif str(self._operand) in [str(Feature(FeatureType.NumTrades)), str(Feature(FeatureType.Buy1NumOrders)),
                                     str(Feature(FeatureType.Buy2NumOrders))
            , str(Feature(FeatureType.Sell1NumOrders)), str(Feature(FeatureType.Sell2NumOrders))]:
            return 'unit'

    # modifies the time window

class RollingOperator(Operator):
    # 一元时序算子
    def __init__(self, operand: Union[Expression, float]) -> None:
        self._operand = operand if isinstance(operand, Expression) else Constant(operand)
        self.init_list = None

    @classmethod
    def n_args(cls) -> int: return 1

    @classmethod
    def category_type(cls) -> Type['Operator']: return RollingOperator

    def evaluate(self, data: StockData) -> Tensor:
        # L: period length (requested time window length)
        # W: window length (dt for rolling)
        # S: stock count
        values = self._operand.evaluate(data)  # (L,S,W)
        return self._apply(values[:,:,1:])  # 左开右闭，小心930

    @abstractmethod
    def _apply(self, operand: Tensor) -> Tensor: ...

    def __str__(self) -> str:
        return f"{type(self).__name__}({self._operand})"

    @property
    def is_featured(self): return self._operand.is_featured

    @property
    def filter_type(self): return 'SHOOT'

    @property
    def is_timeserie(self): return False

    @property
    def feature_units(self):
        if str(self._operand) in [str(Feature(FeatureType.LastPx)), str(Feature(FeatureType.HighPx)),
                                   str(Feature(FeatureType.LowPx)), str(Feature(FeatureType.WeightedAvgBidPx)),
                                   str(Feature(FeatureType.WeightedAvgOfferPx)), str(Feature(FeatureType.Buy1Price)),
                                   str(Feature(FeatureType.Buy2Price)), str(Feature(FeatureType.Sell1Price)),
                                   str(Feature(FeatureType.Sell2Price))]:
            return 'curr_ret'
        elif str(self._operand) in [str(Feature(FeatureType.TotalVolumeTrade)), str(Feature(FeatureType.TotalBidQty)),
                                     str(Feature(FeatureType.TotalOfferQty))
            , str(Feature(FeatureType.Buy1OrderQty)), str(Feature(FeatureType.Buy2OrderQty)),
                                     str(Feature(FeatureType.Sell1OrderQty)),
                                     str(Feature(FeatureType.Sell2OrderQty)), str(Feature(FeatureType.ff_shares))]:
            return 'shares'
        elif str(self._operand) in [str(Feature(FeatureType.TotalValueTrade)), str(Feature(FeatureType.pre_close))]:
            return 'curr'
        elif str(self._operand) in [str(Feature(FeatureType.NumTrades)), str(Feature(FeatureType.Buy1NumOrders)),
                                     str(Feature(FeatureType.Buy2NumOrders))
            , str(Feature(FeatureType.Sell1NumOrders)), str(Feature(FeatureType.Sell2NumOrders))]:
            return 'unit'


class PairRollingOperator(Operator):
    # 二元时序算子
    def __init__(self,
                 lhs: Expression, rhs: Expression) -> None:
        self._lhs = lhs if isinstance(lhs, Expression) else Constant(lhs)
        self._rhs = rhs if isinstance(rhs, Expression) else Constant(rhs)
        self.init_list = None


    @classmethod
    def n_args(cls) -> int: return 2

    @classmethod
    def category_type(cls) -> Type['Operator']: return PairRollingOperator

    def evaluate(self, data: StockData) -> Tensor:
        lhs = self._lhs.evaluate(data)
        rhs = self._rhs.evaluate(data)
        return self._apply(lhs[:,:,1:], rhs[:,:,1:])  # (L, S) 左开右闭，小心930

    @abstractmethod
    def _apply(self, lhs: Tensor, rhs: Tensor) -> Tensor: ...

    def __str__(self) -> str:
        return f"{type(self).__name__}({self._lhs},{self._rhs})"

    @property
    def is_featured(self): return self._lhs.is_featured or self._rhs.is_featured

    @property
    def filter_type(self): return 'SHOOT'

    @property
    def is_timeserie(self): return False


class DiffOperator(Operator):
    # 差分算子【不会改变数据维度】
    def __init__(self, operand: Union[Expression, float]) -> None:
        self._operand = operand if isinstance(operand, Expression) else Constant(operand)
        self.init_list = self._operand.init_list

    @classmethod
    def n_args(cls) -> int: return 1

    @classmethod
    def category_type(cls) -> Type['Operator']: return DiffOperator

    def evaluate(self, data: StockData) -> Tensor:
        # L: period length (requested time window length)
        # W: window length (dt for rolling)
        # S: stock count
        values = self._operand.evaluate(data)  # (L,S,W)
        return self._apply(values)  # 左开右闭，小心930

    @abstractmethod
    def _apply(self, operand: Tensor) -> Tensor: ...

    def __str__(self) -> str:
        return f"{type(self).__name__}({self._operand})"

    @property
    def is_featured(self): return self._operand.is_featured

    @property
    def filter_type(self): return self._operand.filter_type

    @property
    def is_timeserie(self): return True

    @property
    def feature_units(self):
        if str(self._operand) in [str(Feature(FeatureType.LastPx)), str(Feature(FeatureType.HighPx)),
                                   str(Feature(FeatureType.LowPx)), str(Feature(FeatureType.WeightedAvgBidPx)),
                                   str(Feature(FeatureType.WeightedAvgOfferPx)), str(Feature(FeatureType.Buy1Price)),
                                   str(Feature(FeatureType.Buy2Price)), str(Feature(FeatureType.Sell1Price)),
                                   str(Feature(FeatureType.Sell2Price))]:
            return 'curr_ret'
        elif str(self._operand) in [str(Feature(FeatureType.TotalVolumeTrade)), str(Feature(FeatureType.TotalBidQty)),
                                     str(Feature(FeatureType.TotalOfferQty))
            , str(Feature(FeatureType.Buy1OrderQty)), str(Feature(FeatureType.Buy2OrderQty)),
                                     str(Feature(FeatureType.Sell1OrderQty)),
                                     str(Feature(FeatureType.Sell2OrderQty)), str(Feature(FeatureType.ff_shares))]:
            return 'shares'
        elif str(self._operand) in [str(Feature(FeatureType.TotalValueTrade)), str(Feature(FeatureType.pre_close))]:
            return 'curr'
        elif str(self._operand) in [str(Feature(FeatureType.NumTrades)), str(Feature(FeatureType.Buy1NumOrders)),
                                     str(Feature(FeatureType.Buy2NumOrders))
            , str(Feature(FeatureType.Sell1NumOrders)), str(Feature(FeatureType.Sell2NumOrders))]:
            return 'unit'

# Operator implementations
class BinaryFilter(BinaryFilterOperator):
    def _apply(self, operand1: Tensor, operand2: Tensor):
        sub_tensor = torch.nan * torch.ones(operand1.shape).to(operand1.device)
        if self._div_rule == 'when_y>0':
            values = torch.where(operand2 < 0, operand1, sub_tensor)
        if self._div_rule == 'when_y<0':
            values = torch.where(operand2 > 0, operand1, sub_tensor)
        if self._div_rule == 'when_y<1/4[y]':
            quan = torch.quantile(operand2, 0.25, dim=2)
            values = torch.where(operand2 < quan[...,None], operand1,sub_tensor)
        if self._div_rule == 'when_y>3/4[y]':
            quan = torch.quantile(operand2, 0.75, dim=2)
            values = torch.where(operand2> quan[...,None], operand1, sub_tensor)
        return values


class Filter(FilterOperator):
    def _apply(self, operand: Tensor):
        sub_tensor = torch.nan * torch.ones(operand.shape).to(operand.device)
        if self._div_rule in ['[93000,93100]','[93900,93957]','[93000,93500]','[93500,93957]']:
            values = operand.clone()
            values[:, :, :self._idx1] = torch.nan
            if self._idx2 < operand.shape[-1] - 1:
                values[:, :, self._idx2 + 1:] = torch.nan
        if self._div_rule == '<mkt_mean':
            values = torch.where(operand < torch.nanmean(operand, dim=1,keepdim=True), operand, sub_tensor)
        if self._div_rule == '>mkt_mean':
            values = torch.where(operand > torch.nanmean(operand, dim=1, keepdim=True), operand, sub_tensor)
        if self._div_rule == '>ts_mean':
            values = torch.where(operand < torch.nanmean(operand, dim=2, keepdim=True), operand, sub_tensor)
        if self._div_rule == '<ts_mean':
            values = torch.where(operand > torch.nanmean(operand, dim=2, keepdim=True), operand, sub_tensor)
        if self._div_rule == '<const_0':
            values = torch.where(operand < 0, operand, sub_tensor)
        if self._div_rule == '>const_0':
            values = torch.where(operand > 0, operand, sub_tensor)  # 版本太低了没法直接填标量
        return values


class Abs(UnaryOperator):
    def _apply(self, operand: Tensor) -> Tensor: return operand.abs()


class Sign(UnaryOperator):
    def _apply(self, operand: Tensor) -> Tensor: return operand.sign()

    @property
    def feature_units(self):
        return 'other'


class Log(UnaryOperator):
    def _apply(self, operand: Tensor) -> Tensor:
        # 取绝对值
        operand = operand.abs()
        # 将等于0的值替换为0.0001
        epsilon = torch.tensor(1e-8, device=operand.device)
        operand = operand + epsilon
        # 取log
        return operand.log()


# class CSRank(UnaryOperator):
#     def _apply(self, operand: Tensor) -> Tensor:
#         nan_mask = operand.isnan()
#         n = (~nan_mask).sum(dim=1, keepdim=True)
#         rank = operand.argsort(dim=1).argsort(dim=1) / n  # 默认是对最后一维使用,s所以要加dim因为我是三维数据
#         rank[nan_mask] = torch.nan
#         return rank


class Add(BinaryOperator):
    def _apply(self, lhs: Tensor, rhs: Tensor) -> Tensor:
        if len(lhs.shape) < len(rhs.shape):
            lhs = lhs[...,None]
        elif len(lhs.shape) > len(rhs.shape):
            rhs = rhs[...,None]
        return lhs + rhs

    @property
    def feature_units(self):
        raise self._lhs.feature_units == self._rhs.feature_units
        return self._lhs.feature_units

class Sub(BinaryOperator):
    def _apply(self, lhs: Tensor, rhs: Tensor) -> Tensor:
        if len(lhs.shape) < len(rhs.shape):
            lhs = lhs[...,None]
        elif len(lhs.shape) > len(rhs.shape):
            rhs = rhs[...,None]
        return lhs - rhs

    @property
    def feature_units(self):
        raise self._lhs.feature_units == self._rhs.feature_units
        return self._lhs.feature_units


class Mul(BinaryOperator):
    def _apply(self, lhs: Tensor, rhs: Tensor) -> Tensor:
        if len(lhs.shape) < len(rhs.shape):
            lhs = lhs[...,None]
        elif len(lhs.shape) > len(rhs.shape):
            rhs = rhs[...,None]
        return lhs * rhs

    @property
    def feature_units(self):
        return 'other'

class Div(BinaryOperator):
    def _apply(self, lhs: Tensor, rhs: Tensor) -> Tensor:
        if len(lhs.shape) < len(rhs.shape):
            lhs = lhs[..., None]
        elif len(lhs.shape) > len(rhs.shape):
            rhs = rhs[..., None]
        epsilon = torch.tensor(1e-8, device=lhs.device)
        return lhs / (rhs + epsilon)

    @property
    def feature_units(self):
        return 'other'


class Pow(BinaryOperator):
    def _apply(self, lhs: Tensor, rhs: Tensor) -> Tensor: return lhs ** rhs


class Greater(BinaryOperator):
    def _apply(self, lhs: Tensor, rhs: Tensor) -> Tensor:
        if len(lhs.shape) < len(rhs.shape):
            lhs = lhs[...,None]
        elif len(lhs.shape) > len(rhs.shape):
            rhs = rhs[...,None]
        return lhs.max(rhs)

    @property
    def is_featured(self):
        return self._lhs.is_featured and self._rhs.is_featured

    @property
    def feature_units(self):
        raise self._lhs.feature_units == self._rhs.feature_units
        return self._lhs.feature_units

class Less(BinaryOperator):
    def _apply(self, lhs: Tensor, rhs: Tensor) -> Tensor:
        if len(lhs.shape) < len(rhs.shape):
            lhs = lhs[...,None]
        elif len(lhs.shape) > len(rhs.shape):
            rhs = rhs[...,None]
        if rhs.device != lhs.device:
            print('different device')
        return lhs.min(rhs)

    @property
    def is_featured(self):
        return self._lhs.is_featured and self._rhs.is_featured

    @property
    def feature_units(self):
        raise self._lhs.feature_units == self._rhs.feature_units
        return self._lhs.feature_units


class Euc_Dis(BinaryOperator):
    def _apply(self, lhs: Tensor, rhs: Tensor) -> Tensor:
        if len(lhs.shape) < len(rhs.shape):
            lhs = lhs[...,None]
        elif len(lhs.shape) > len(rhs.shape):
            rhs = rhs[...,None]
        return torch.sqrt((lhs - rhs) ** 2)

    @property
    def feature_units(self):
        return 'other'



class Get(GetOperator):
    def _apply(self, operand: Tensor) -> Tensor:
        return operand[:,:,self.idx]


# class Ref(RollingOperator):
#     # Ref is not *really* a rolling operator, in that other rolling operators
#     # deal with the values in (-dt, 0], while Ref only deal with the values
#     # at -dt. Nonetheless, it should be classified as rolling since it modifies
#     # the time window.
#
#     def evaluate(self, data: StockData, period: slice = slice(0, 1)) -> Tensor:
#         start = period.start - self._delta_time
#         stop = period.stop - self._delta_time
#         return self._operand.evaluate(data, slice(start, stop))
#
#     def _apply(self, operand: Tensor) -> Tensor:
#         # This is just for fulfilling the RollingOperator interface
#         ...

class Diff1(DiffOperator):
    def _apply(self, operand: Tensor) -> Tensor:
        full_nan = torch.full(operand.shape, torch.nan, device = operand.device)
        operand_diff = operand[:,:,1:] - operand[:,:,:-1]
        full_nan[:,:,1:] = operand_diff
        return full_nan


class Diff5(DiffOperator):
    def _apply(self, operand: Tensor) -> Tensor:
        full_nan = torch.full(operand.shape, torch.nan, device = operand.device)
        operand_diff = operand[:,:,5:] - operand[:,:,:-5]
        full_nan[:,:,5:] = operand_diff
        return full_nan

class Mean(RollingOperator):
    def _apply(self, operand: Tensor) -> Tensor:
        return operand.nanmean(dim=-1)  # 相当于去掉了nan后的数组的均值


class Sum(RollingOperator):
    def _apply(self, operand: Tensor) -> Tensor:
        return operand.nansum(dim=-1)  # 相当于去掉了nan后的数组的和


class Std(RollingOperator):
    def _apply(self, operand: Tensor) -> Tensor:
        return torch.sqrt(torch.nanmean((operand-operand.nanmean(dim=-1)[...,None])**2,dim=-1))


    @property
    def feature_units(self):
        return 'other'

class Var(RollingOperator):
    def _apply(self, operand: Tensor) -> Tensor:
        return operand.nanmean((operand-operand.nanmean(dim=-1))**2,dim=-1)

    @property
    def feature_units(self):
        return 'other'

class Skew(RollingOperator):
    def _apply(self, operand: Tensor) -> Tensor:
        # skew = m3 / m2^(3/2)
        central = operand - operand.nanmean(dim=-1, keepdim=True)
        m3 = (central ** 3).nanmean(dim=-1)
        m2 = (central ** 2).nanmean(dim=-1)
        return m3 / m2 ** 1.5

    @property
    def feature_units(self):
        return 'other'

class Kurt(RollingOperator):
    def _apply(self, operand: Tensor) -> Tensor:
        # kurt = m4 / var^2 - 3
        central = operand - operand.nanmean(dim=-1, keepdim=True)
        m4 = (central ** 4).nanmean(dim=-1)
        var = torch.nanmean((operand-operand.nanmean(dim=-1)[...,None])**2,dim=-1)
        return m4 / var ** 2 - 3

    @property
    def feature_units(self):
        return 'other'


class Max(RollingOperator):
    def _apply(self, operand: Tensor) -> Tensor:
        op_nonan = operand.clone()
        op_nonan[torch.isnan(operand)] = -1e6
        return torch.max(op_nonan, dim = -1)[0]


class Min(RollingOperator):
    def _apply(self, operand: Tensor) -> Tensor:
        op_nonan = operand.clone()
        op_nonan[torch.isnan(operand)] = 1e6
        return torch.min(op_nonan, dim = -1)[0]


class Med(RollingOperator):
    def _apply(self, operand: Tensor) -> Tensor: return operand.median(dim=-1)[0]


class Mad(RollingOperator):
    def _apply(self, operand: Tensor) -> Tensor:
        central = operand - operand.nanmean(dim=-1, keepdim=True)
        return central.abs().nanmean(dim=-1)


class Rank(RollingOperator):
    def _apply(self, operand: Tensor) -> Tensor:
        # mask = operand.isnan().any(dim=-1)
        n = operand.shape[-1]
        last = operand[:, :, -1, None]
        left = (last < operand).count_nonzero(dim=-1)
        right = (last <= operand).count_nonzero(dim=-1)  # nan会返回0
        result = (right + left + (right > left)) / (2 * n)
        # if not self._operand.is_filtered:
        #     result[mask] = torch.nan  # 只要时序切片里nan有不要这一坨了
        return result

    @property
    def feature_units(self):
        return 'other'

#
class PercentileRank(UnaryOperator):
    def _apply(self, operand: Tensor) -> Tensor:
        nan_mask = operand.isnan()
        n = (~nan_mask).sum(dim=1, keepdim=True)
        rank = operand.argsort().argsort().float() / (n - 1)
        rank[nan_mask] = torch.nan
        return rank

    @property
    def feature_units(self):
        return 'other'

class WMA(RollingOperator):
    def _apply(self, operand: Tensor) -> Tensor:
        n = operand.shape[-1]
        weights = torch.arange(n, dtype=operand.dtype, device=operand.device)
        weights /= weights.sum()
        return (weights * operand).nansum(dim=-1)


class EMA(RollingOperator):
    def _apply(self, operand: Tensor) -> Tensor:
        n = operand.shape[-1]
        alpha = 1 - 2 / (1 + n)
        power = torch.arange(n, 0, -1, dtype=operand.dtype, device=operand.device)
        weights = alpha ** power
        weights /= weights.sum()
        return (weights * operand).nansum(dim=-1)


class GainFromMin(RollingOperator):
    def _apply(self, operand: Tensor) -> Tensor:
        # 找到过去window期的最低值
        op_nonan = operand.clone()
        op_nonan[torch.isnan(operand)] = 1e6
        min_values = op_nonan.min(dim=-1).values
        # 计算相对最低位的涨幅
        if torch.sum(min_values==0.) == 0.:  # 只要有一支股票不能这样算，就都改成绝对值
            gain_from_min = (operand[...,-1] - min_values) / min_values
        else:
            gain_from_min = operand[...,-1] - min_values
        return gain_from_min

    @property
    def feature_units(self):
        return 'other'

class DropFromMax(RollingOperator):
    def _apply(self, operand: Tensor) -> Tensor:
        # 找到过去window期的最高值
        op_nonan = operand.clone()
        op_nonan[torch.isnan(operand)] = -1e6
        max_values = op_nonan.max(dim=-1).values
        # 计算相对最高位的跌幅
        if torch.sum(max_values == 0.) == 0.:  # 因为要统一一下，要么都是绝对的，要么都是相对的
            drop_from_max = (operand[...,-1] - max_values) / max_values
        else:
            drop_from_max = operand[...,-1] - max_values
        return drop_from_max

    @property
    def feature_units(self):
        return 'other'


class Rel_UpandDown(RollingOperator):
    def _apply(self, operand: Tensor) -> Tensor:
        # 计算过去window期的均值
        mean_values = operand.nanmean(dim=-1)
        # 计算过去window期的标准差
        std_values = torch.sqrt(torch.nanmean((operand-mean_values[:,:,None])**2,dim=-1))
        # 计算上下轨
        upper_band = mean_values + std_values
        lower_band = mean_values - std_values

        # 计算相对上下轨的位置
        mask = (upper_band - lower_band) == 0
        relative_position = (operand[:,:,-1] - lower_band) / (upper_band - lower_band)
        relative_position[mask] = 0
        return relative_position

    @property
    def feature_units(self):
        return 'other'


# 过去d期的zscore
class ZScore(RollingOperator):
    def _apply(self, operand: Tensor) -> Tensor:
        mean = operand.nanmean(dim=-1)
        std = torch.sqrt(torch.nanmean(operand-mean[...,None],dim=-1))
        return (operand[:,:,-1] - mean) / std

    @property
    def feature_units(self):
        return 'other'


# 过去d期的最小值距离现在多远
class MinPos(RollingOperator):
    def _apply(self, operand: Tensor) -> Tensor:
        operand[torch.isnan(operand)] = torch.tensor(1e6, device = operand.device)
        return operand.shape[-1]-operand.argmin(dim=-1,keepdim=True)

    @property
    def feature_units(self):
        return 'other'

# 过去d期的最大值距离现在多远
class MaxPos(RollingOperator):
    def _apply(self, operand: Tensor) -> Tensor:
        operand[torch.isnan(operand)] = torch.tensor(-1e6, device=operand.device)
        return operand.shape[-1]-operand.argmax(dim=-1,keepdim=True)

    @property
    def feature_units(self):
        return 'other'


class Cov(PairRollingOperator):
    def _apply(self, lhs: Tensor, rhs: Tensor) -> Tensor:
        nan_mask1 = torch.isnan(lhs)
        nan_mask2 = torch.isnan(rhs)
        nan_mask = nan_mask1|nan_mask2
        n = torch.sum(~nan_mask, dim=2)
        clhs = lhs - lhs[~nan_mask].mean(dim=-1, keepdim=True)
        crhs = rhs - rhs[~nan_mask].mean(dim=-1, keepdim=True)
        return (clhs * crhs).nansum(dim=-1) / (n - 1)

    @property
    def feature_units(self):
        return 'other'


class Corr(PairRollingOperator):
    def _apply(self, lhs: Tensor, rhs: Tensor) -> Tensor:
        nan_mask1 = torch.isnan(lhs)
        nan_mask2 = torch.isnan(rhs)
        nan_mask = nan_mask1|nan_mask2
        clhs = lhs - lhs[~nan_mask].mean(dim=-1, keepdim=True)
        crhs = rhs - rhs[~nan_mask].mean(dim=-1, keepdim=True)
        ncov = (clhs * crhs).nansum(dim=-1)
        nlvar = (clhs[~nan_mask] ** 2).sum(dim=-1)
        nrvar = (crhs[~nan_mask] ** 2).sum(dim=-1)
        stdmul = (nlvar * nrvar).sqrt()
        # stdmul[(nlvar < 1e-6) | (nrvar < 1e-6)] = 1
        epsilon = torch.tensor(1e-8, device=lhs.device)
        stdmul = stdmul + epsilon
        return ncov / stdmul

    @property
    def feature_units(self):
        return 'other'

#
# # Deprecated!
# Operators: List[Type[Expression]] = [
#     # Unary
#     Abs, Sign, Log, CSRank,
#     # Binary
#     Add, Sub, Mul, Div, Pow, Greater, Less,
#     # Rolling
#     Mean, Sum, Std, Var, Skew, Kurt, Max, Min,
#     Med, Mad, Rank, WMA, EMA, Get, Delta,
#     # Pair rolling
#     Cov, Corr
# ]
