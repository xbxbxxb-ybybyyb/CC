from abc import ABCMeta, abstractmethod
from typing import List, Type, Union

import torch
from torch import Tensor

from alphagen_qlib.stock_data import StockData, FeatureType


class OutOfDataRangeError(IndexError):
    pass

# 如果时序片段里面有nan，那么对这一段时序的算子返回的也是nan

class Expression(metaclass=ABCMeta):
    @abstractmethod
    def evaluate(self, data: StockData, period: slice = slice(0, 1)) -> Tensor: ...

    def __repr__(self) -> str: return str(self)

    def __add__(self, other: Union["Expression", float]) -> "Add":
        if isinstance(other, Expression):
            return Add(self, other)
        else:
            return Add(self, Constant(other))

    def __radd__(self, other: float) -> "Add": return Add(Constant(other), self)

    def __sub__(self, other: Union["Expression", float]) -> "Sub":
        if isinstance(other, Expression):
            return Sub(self, other)
        else:
            return Sub(self, Constant(other))

    def __rsub__(self, other: float) -> "Sub": return Sub(Constant(other), self)

    def __mul__(self, other: Union["Expression", float]) -> "Mul":
        if isinstance(other, Expression):
            return Mul(self, other)
        else:
            return Mul(self, Constant(other))

    def __rmul__(self, other: float) -> "Mul": return Mul(Constant(other), self)

    def __truediv__(self, other: Union["Expression", float]) -> "Div":
        if isinstance(other, Expression):
            return Div(self, other)
        else:
            return Div(self, Constant(other))

    def __rtruediv__(self, other: float) -> "Div": return Div(Constant(other), self)

    # def __pow__(self, other: Union["Expression", float]) -> "Pow":
    #     if isinstance(other, Expression):
    #         return Pow(self, other)
    #     else:
    #         return Pow(self, Constant(other))
    #
    # def __rpow__(self, other: float) -> "Pow": return Pow(Constant(other), self)

    def __pos__(self) -> "Expression": return self
    def __neg__(self) -> "Sub": return Sub(Constant(0), self)
    def __abs__(self) -> "Abs": return Abs(self)

    @property
    def is_featured(self): raise NotImplementedError


class Feature(Expression):
    def __init__(self, feature: FeatureType) -> None:
        self._feature = feature
        self.init_list = []

    def evaluate(self, data: StockData, period: slice = slice(0, 1)) -> Tensor:
        assert period.step == 1 or period.step is None
        if (period.start < -data.max_backtrack_days or
                period.stop - 1 > data.max_future_days):
            raise OutOfDataRangeError()
        start = period.start + data.max_backtrack_days
        stop = period.stop + data.max_backtrack_days + data.n_days - 1
        return data.data[start:stop, int(self._feature), :]

    def __str__(self) -> str: return '$' + self._feature.name.lower()

    @property
    def is_featured(self): return True

    @property
    def feature_units(self):
        if self._feature.value in [FeatureType.open.value, FeatureType.close.value, FeatureType.high.value, FeatureType.low.value,
                             FeatureType.vwap.value]:
            return 'curr_ret'
        elif self._feature.value in [FeatureType.volume.value, FeatureType.free_float_shares.value]:
            return 'unit'
        elif self._feature.value in [FeatureType.amt.value, FeatureType.mkt_cap_ard.value]:
            return 'unit*curr'
        elif self._feature.value in [FeatureType.pre_close.value]:
            return 'curr'
        elif self._feature.value in [FeatureType.turn.value]:
            return 'perc'

    @property
    def is_filtered(self): return False

    @property
    def filter_type(self): return self.init_list


class Constant(Expression):
    def __init__(self, value: float) -> None:
        self._value = value

    def evaluate(self, data: StockData, period: slice = slice(0, 1)) -> Tensor:
        assert period.step == 1 or period.step is None
        if (period.start < -data.max_backtrack_days or
                period.stop - 1 > data.max_future_days):
            raise OutOfDataRangeError()
        device = data.data.device
        dtype = data.data.dtype
        days = period.stop - period.start - 1 + data.n_days
        return torch.full(size=(days, data.n_stocks),
                          fill_value=self._value, dtype=dtype, device=device)

    def __str__(self) -> str: return f'Constant({str(self._value)})'

    @property
    def is_featured(self): return False

    @property
    def is_filtered(self): return True

class DeltaTime(Expression):
    # This is not something that should be in the final expression
    # It is only here for simplicity in the implementation of the tree builder
    def __init__(self, delta_time: int) -> None:
        self._delta_time = delta_time

    def evaluate(self, data: StockData, period: slice = slice(0, 1)) -> Tensor:
        assert False, "Should not call evaluate on delta time"

    def __str__(self) -> str: return str(self._delta_time)

    @property
    def is_featured(self): return False

    @property
    def is_filtered(self): return False

class DivRule(Expression):
    # This is not something that should be in the final expression
    # It is only here for simplicity in the implementation of the tree builder
    def __init__(self, div_rule: str) -> None:
        self._div_rule = div_rule

    def evaluate(self, data: StockData, period: slice = slice(0, 1)) -> Tensor:
        assert False, "Should not call evaluate on delta time"

    def __str__(self) -> str: return str(self._div_rule)

    @property
    def is_featured(self): return False

    @property
    def is_filtered(self): return False

class BinaryDivRule(Expression):
    # This is not something that should be in the final expression
    # It is only here for simplicity in the implementation of the tree builder
    def __init__(self, div_rule: str) -> None:
        self._div_rule = div_rule

    def evaluate(self, data: StockData, period: slice = slice(0, 1)) -> Tensor:
        assert False, "Should not call evaluate on delta time"

    def __str__(self) -> str: return str(self._div_rule)

    @property
    def is_featured(self): return False

    @property
    def is_filtered(self): return False

# Operator base classes

class Operator(Expression):
    @classmethod
    @abstractmethod
    def n_args(cls) -> int: ...

    @classmethod
    @abstractmethod
    def category_type(cls) -> Type['Operator']: ...


class UnaryOperator(Operator):
    def __init__(self, operand: Union[Expression, float]) -> None:
        self._operand = operand if isinstance(operand, Expression) else Constant(operand)
        self.init_list = self._operand.init_list

    @classmethod
    def n_args(cls) -> int: return 1

    @classmethod
    def category_type(cls) -> Type['Operator']: return UnaryOperator

    def evaluate(self, data: StockData, period: slice = slice(0, 1)) -> Tensor:
        return self._apply(self._operand.evaluate(data, period))

    @abstractmethod
    def _apply(self, operand: Tensor) -> Tensor: ...

    def __str__(self) -> str:
        return f"{type(self).__name__}({self._operand})"

    @property
    def is_featured(self): return self._operand.is_featured

    @property
    def is_filtered(self):
        return self._operand.is_filtered

    @property
    def filter_type(self): return self._operand.filter_type

    # 会改变单位的算子比如sign可以单独在定义里面设置为other
    @property
    def feature_units(self):
        if str(self._operand) in [str(Feature(FeatureType.open)), str(Feature(FeatureType.close)), str(Feature(FeatureType.high)), str(Feature(FeatureType.low)),
                             str(Feature(FeatureType.vwap))]:
            return 'curr_ret'
        elif str(self._operand) in [str(Feature(FeatureType.volume)), str(Feature(FeatureType.free_float_shares))]:
            return 'unit'
        elif str(self._operand) in [str(Feature(FeatureType.amt)), str(Feature(FeatureType.mkt_cap_ard))]:
            return 'unit*curr'
        elif str(self._operand) in [str(Feature(FeatureType.pre_close))]:
            return 'curr'
        elif str(self._operand) in [str(Feature(FeatureType.turn))]:
            return 'perc'

class FilterOperator(Operator):
    def __init__(self, operand: Union[Expression, float], delta_time: Union[int, DeltaTime], div_rule: [str,DivRule]) -> None:
        self._operand = operand if isinstance(operand, Expression) else Constant(operand)
        if isinstance(delta_time, DeltaTime):
            delta_time = delta_time._delta_time
        self._delta_time = delta_time if not self._operand.is_filtered else 1
        self._div_rule = str(div_rule)
        self.init_list = self._operand.init_list
        try:
            self.init_list.append((self._div_rule, self._delta_time))
        except:
            print('a')

    @classmethod
    def n_args(cls) -> int: return 3

    @classmethod
    def category_type(cls) -> Type['Operator']: return Filter

    def evaluate(self, data: StockData, period: slice = slice(0, 1)) -> Tensor:
        start = period.start - self._delta_time + 1
        stop = period.stop
        # L: period length (requested time window length)
        # W: window length (dt for rolling)
        # S: stock count
        values = self._operand.evaluate(data, slice(start, stop))   # (L+W-1, S)
        if not self._operand.is_filtered:
            values = values.unfold(0, self._delta_time, 1)              # (L, S, W)

        return self._apply(values)                                # (L, S)

    @abstractmethod
    def _apply(self, operand: Tensor) -> Tensor: ...

    def __str__(self) -> str:
        return f"{type(self).__name__}({self._operand},{self._delta_time}, {self._div_rule})"

    @property
    def is_featured(self): return self._operand.is_featured

    @property
    def filter_type(self):
        return self.init_list

    @property
    def is_filtered(self): return True
    # 如果是被filter处理过的数据经过时序算子，则1）不需要unfold那一步 2）计算的时候可以忽略nan，比如60个数据里有nan
    # 那么求均值时对剩下的30个求即可，分母也是30

    # 会改变单位的算子比如sign可以单独在定义里面设置为other
    @property
    def feature_units(self):
        if str(self._operand) in [str(Feature(FeatureType.open)), str(Feature(FeatureType.close)), str(Feature(FeatureType.high)), str(Feature(FeatureType.low)),
                             str(Feature(FeatureType.vwap))]:
            return 'curr_ret'
        elif str(self._operand) in [str(Feature(FeatureType.volume)), str(Feature(FeatureType.free_float_shares))]:
            return 'unit'
        elif str(self._operand) in [str(Feature(FeatureType.amt)), str(Feature(FeatureType.mkt_cap_ard))]:
            return 'unit*curr'
        elif str(self._operand) in [str(Feature(FeatureType.pre_close))]:
            return 'curr'
        elif str(self._operand) in [str(Feature(FeatureType.turn))]:
            return 'perc'


class BinaryFilterOperator(Operator):
    def __init__(self, operand1: Union[Expression, float], operand2: Union[Expression, float], delta_time: Union[int, DeltaTime], div_rule: [str,BinaryDivRule]) -> None:
        self._operand1 = operand1 if isinstance(operand1, Expression) else Constant(operand1)
        self._operand2 = operand1 if isinstance(operand2, Expression) else Constant(operand2)
        if isinstance(delta_time, DeltaTime):
            delta_time = delta_time._delta_time
        self._div_rule = str(div_rule)
        self.init_list = self._operand1.init_list
        self.init_list.append((self._div_rule, delta_time))
        if isinstance(delta_time, DeltaTime):
            delta_time = delta_time._delta_time
        if self._operand1.is_filtered:  # 因为我需要先计算这个有filter的得到时序维度，才能给delta_time赋值
            self._expr1 = self._operand1
            self._expr2 = self._operand1
            self._delta_time = 1
        elif self._operand2.is_filtered:
            self._expr1 = self._operand2
            self._expr2 = self._operand2
            self._delta_time = 1
        else:
            self._expr1 = self._operand1
            self._expr2 = self._operand2
            self._delta_time = delta_time

    @classmethod
    def n_args(cls) -> int: return 4

    @classmethod
    def category_type(cls) -> Type['Operator']: return BinaryFilter  # 额这里一定要记得改，不然在valid里会有大问题

    def _unfold_one(self, expr: Expression,
                    data: StockData, period: slice = slice(0, 1),delta_time: int = 1) -> Tensor:
        delta_time = delta_time if not expr.is_filtered else 1
        start = period.start - delta_time + 1
        stop = period.stop
        # L: period length (requested time window length)
        # W: window length (dt for rolling)
        # S: stock count
        values = expr.evaluate(data, slice(start, stop))            # (L+W-1, S)
        if not expr.is_filtered:
            values = values.unfold(0, delta_time, 1)  # (L, S, W)
        return values, values.shape[-1]          # (L, S, W)

    def evaluate(self, data: StockData, period: slice = slice(0, 1)) -> Tensor:
        lhs, delta_time = self._unfold_one(self._expr1, data, period, self._delta_time)
        rhs, _ = self._unfold_one(self._expr2, data, period,delta_time)
        return self._apply(lhs, rhs)                                # (L

    @abstractmethod
    def _apply(self, operand1: Tensor, operand2: Tensor) -> Tensor: ...

    def __str__(self) -> str:
        return f"{type(self).__name__}({self._operand1},{self._operand2},{self._delta_time},{self._div_rule})"

    @property
    def is_featured(self): return self._operand1.is_featured # or self._operand2.is_featureds

    @property
    def filter_type(self):
        return self.init_list

    @property
    def is_filtered(self): return True
    # 如果是被filter处理过的数据经过时序算子，则1）不需要unfold那一步 2）计算的时候可以忽略nan，比如60个数据里有nan
    # 那么求均值时对剩下的30个求即可，分母也是30

    # 会改变单位的算子比如sign可以单独在定义里面设置为other
    @property
    def feature_units(self):
        if str(self._operand1) in [str(Feature(FeatureType.open)), str(Feature(FeatureType.close)), str(Feature(FeatureType.high)), str(Feature(FeatureType.low)),
                             str(Feature(FeatureType.vwap))]:
            return 'curr_ret'
        elif str(self._operand1) in [str(Feature(FeatureType.volume)), str(Feature(FeatureType.free_float_shares))]:
            return 'unit'
        elif str(self._operand1) in [str(Feature(FeatureType.amt)), str(Feature(FeatureType.mkt_cap_ard))]:
            return 'unit*curr'
        elif str(self._operand1) in [str(Feature(FeatureType.pre_close))]:
            return 'curr'
        elif str(self._operand1) in [str(Feature(FeatureType.turn))]:
            return 'perc'


class BinaryOperator(Operator):
    def __init__(self, lhs: Union[Expression, float], rhs: Union[Expression, float]) -> None:
        self._lhs = lhs if isinstance(lhs, Expression) else Constant(lhs)
        self._rhs = rhs if isinstance(rhs, Expression) else Constant(rhs)
        self.init_list = self._lhs.init_list

    @classmethod
    def n_args(cls) -> int: return 2

    @classmethod
    def category_type(cls) -> Type['Operator']: return BinaryOperator

    def evaluate(self, data: StockData, period: slice = slice(0, 1)) -> Tensor:
        return self._apply(self._lhs.evaluate(data, period), self._rhs.evaluate(data, period))

    @abstractmethod
    def _apply(self, lhs: Tensor, rhs: Tensor) -> Tensor: ...

    def __str__(self) -> str:
        return f"{type(self).__name__}({self._lhs},{self._rhs})"

    @property
    def is_featured(self): return self._lhs.is_featured or self._rhs.is_featured

    @property
    def filter_type(self): return self._lhs.filter_type if self._lhs.filter_type != 'SHOOT' else self._rhs.filter_type

    @property
    def is_filtered(self): return self._lhs.is_filtered or self._rhs.is_filtered


class RollingOperator(Operator):
    def __init__(self, operand: Union[Expression, float], delta_time: Union[int, DeltaTime]) -> None:
        self._operand = operand if isinstance(operand, Expression) else Constant(operand)
        if isinstance(delta_time, DeltaTime):
            delta_time = delta_time._delta_time
        self._delta_time = delta_time if not self._operand.is_filtered else 1  # filter里面其实已经包含了构造时序数据这一步
        self.init_list = self._operand.init_list

    @classmethod
    def n_args(cls) -> int: return 2

    @classmethod
    def category_type(cls) -> Type['Operator']: return RollingOperator

    def evaluate(self, data: StockData, period: slice = slice(0, 1)) -> Tensor:
        start = period.start - self._delta_time + 1
        stop = period.stop
        # L: period length (requested time window length)
        # W: window length (dt for rolling)
        # S: stock count
        values = self._operand.evaluate(data, slice(start, stop))  # (L+W-1, S)
        if not self._operand.is_filtered:  # 如果被筛选过了实际上已经是三维的了
            values = values.unfold(0, self._delta_time, 1)  # (L, S, W)
        return self._apply(values)  # (L, S)

    @abstractmethod
    def _apply(self, operand: Tensor) -> Tensor: ...

    def __str__(self) -> str:
        return f"{type(self).__name__}({self._operand},{self._delta_time})"

    @property
    def is_featured(self): return self._operand.is_featured

    @property
    def filter_type(self): return self.init_list

    @property
    def is_filtered(self): return False

    # 会改变单位的算子比如sign可以单独在定义里面设置为other
    @property
    def feature_units(self):
        if str(self._operand) in [str(Feature(FeatureType.open)), str(Feature(FeatureType.close)), str(Feature(FeatureType.high)), str(Feature(FeatureType.low)),
                             str(Feature(FeatureType.vwap))]:
            return 'curr_ret'
        elif str(self._operand) in [str(Feature(FeatureType.volume)), str(Feature(FeatureType.free_float_shares))]:
            return 'unit'
        elif str(self._operand) in [str(Feature(FeatureType.amt)), str(Feature(FeatureType.mkt_cap_ard))]:
            return 'unit*curr'
        elif str(self._operand) in [str(Feature(FeatureType.pre_close))]:
            return 'curr'
        elif str(self._operand) in [str(Feature(FeatureType.turn))]:
            return 'perc'



class PairRollingOperator(Operator):
    def __init__(self,
                 lhs: Expression, rhs: Expression,
                 delta_time: Union[int, DeltaTime]) -> None:
        self._lhs = lhs if isinstance(lhs, Expression) else Constant(lhs)
        self._rhs = rhs if isinstance(rhs, Expression) else Constant(rhs)
        if isinstance(delta_time, DeltaTime):
            delta_time = delta_time._delta_time
        if self._lhs.is_filtered:  # 因为我需要先计算这个有filter的得到时序维度，才能给delta_time赋值
            self._expr1 = self._lhs
            self._expr2 = self._rhs
            self._delta_time = 1
        elif self._rhs.is_filtered:
            self._expr1 = self._rhs
            self._expr2 = self._lhs
            self._delta_time = 1
        else:
            self._expr1 = self._lhs
            self._expr2 = self._rhs
            self._delta_time = delta_time
        self.init_list = self._lhs.init_list

    @classmethod
    def n_args(cls) -> int: return 3

    @classmethod
    def category_type(cls) -> Type['Operator']: return PairRollingOperator

    def _unfold_one(self, expr: Expression,
                    data: StockData, period: slice = slice(0, 1),delta_time: int = 1) -> Tensor:
        delta_time = delta_time if not expr.is_filtered else 1
        start = period.start - delta_time + 1
        stop = period.stop
        # L: period length (requested time window length)
        # W: window length (dt for rolling)
        # S: stock count
        values = expr.evaluate(data, slice(start, stop))            # (L+W-1, S)
        if not expr.is_filtered:
            values = values.unfold(0, delta_time, 1)  # (L, S, W)
        return values, values.shape[-1]          # (L, S, W)

    def evaluate(self, data: StockData, period: slice = slice(0, 1)) -> Tensor:
        lhs, delta_time = self._unfold_one(self._expr1, data, period, self._delta_time)
        rhs, _ = self._unfold_one(self._expr2, data, period,delta_time)
        return self._apply(lhs, rhs)                                # (L, S)

    @abstractmethod
    def _apply(self, lhs: Tensor, rhs: Tensor) -> Tensor: ...

    def __str__(self) -> str:
        return f"{type(self).__name__}({self._lhs},{self._rhs},{self._delta_time})"

    @property
    def is_featured(self): return self._lhs.is_featured or self._rhs.is_featured

    @property
    def filter_type(self): return self.init_list

    @property
    def is_filtered(self): return False
# Operator implementations

class BinaryFilter(BinaryFilterOperator):
    def _apply(self, operand1: Tensor, operand2: Tensor):
        sub_tensor = torch.nan * torch.ones(operand1.shape).to(operand1.device)
        if self._div_rule == 'when_y>0':
            values = torch.where(operand2 < 0, operand1, sub_tensor)
        if self._div_rule == 'when_y<0':
            values = torch.where(operand2 > 0, operand1, sub_tensor)
        if self._div_rule == 'when_y<1/4[y]':
            quan = torch.nanquantile(operand2, 0.25, dim=2)
            values = torch.where(operand2 < quan[...,None], operand1,sub_tensor)
        if self._div_rule == 'when_y>3/4[y]':
            quan = torch.nanquantile(operand2, 0.75, dim=2)
            values = torch.where(operand2> quan[...,None], operand1, sub_tensor)
        return values


class Filter(FilterOperator):
    def _apply(self, operand: Tensor):
        sub_tensor = torch.nan * torch.ones(operand.shape).to(operand.device)
        if self._div_rule == '<mkt_mean':
            # values = torch.where(operand < torch.nanmean(operand, dim=1,keepdim=True), operand, sub_tensor)
            values = torch.where(operand < torch.nanquantile(operand, 0.2, dim=1)[:,None,:], operand, sub_tensor)
        elif self._div_rule == '>mkt_mean':
            # values = torch.where(operand > torch.nanmean(operand, dim=1, keepdim=True), operand, sub_tensor)
            values = torch.where(operand > torch.nanquantile(operand, 0.8, dim=1)[:,None,:], operand, sub_tensor)
        elif self._div_rule == '>ts_mean':
            values = torch.where(operand < torch.nanquantile(operand, 0.2, dim=2)[..., None], operand, sub_tensor)
            # values = torch.where(operand < torch.nanmean(operand, dim=2, keepdim=True), operand, sub_tensor)
        elif self._div_rule == '<ts_mean':
            values = torch.where(operand > torch.nanquantile(operand, 0.8, dim=2)[..., None], operand, sub_tensor)
            # values = torch.where(operand > torch.nanmean(operand, dim=2, keepdim=True), operand, sub_tensor)
        elif self._div_rule == '<const_0':
            values = torch.where(operand < 0, operand, sub_tensor)
        elif self._div_rule == '>const_0':
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
#
# class CSRank(UnaryOperator):
#     def _apply(self, operand: Tensor) -> Tensor:
#         nan_mask = operand.isnan()
#         n = (~nan_mask).sum(dim=1, keepdim=True)
#         rank = operand.argsort().argsort() / n
#         rank[nan_mask] = torch.nan
#         return rank

# class Square(UnaryOperator):
#     def _apply(self, operand: Tensor) -> Tensor:
#         return operand ** 2
#
#
# class SquareRoot(UnaryOperator):
#     def _apply(self, operand: Tensor) -> Tensor:
#         return operand.sqrt()
#
#
# class Cube(UnaryOperator):
#     def _apply(self, operand: Tensor) -> Tensor:
#         return operand ** 3
#
#
# class CubeRoot(UnaryOperator):
#     def _apply(self, operand: Tensor) -> Tensor:
#         return operand.pow(1/3)
#
#
# class Reciprocal(UnaryOperator):
#     def _apply(self, operand: Tensor) -> Tensor:
#         return 1 / operand
#
#
# class Inverse(UnaryOperator):
#     def _apply(self, operand: Tensor) -> Tensor:
#         return -operand
#
#
# class Sin(UnaryOperator):
#     def _apply(self, operand: Tensor) -> Tensor:
#         return operand.sin()
#
#
# class Cos(UnaryOperator):
#     def _apply(self, operand: Tensor) -> Tensor:
#         return operand.cos()
#
#
# class Tan(UnaryOperator):
#     def _apply(self, operand: Tensor) -> Tensor:
#         return operand.tan()
#
#
# class Sigmoid(UnaryOperator):
#     def _apply(self, operand: Tensor) -> Tensor:
#         return operand.sigmoid()
#
#
# class Exp(UnaryOperator):
#     def _apply(self, operand: Tensor) -> Tensor:
#         return operand.exp()
#
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
#
# # if x > 0, 1, else 0
# class IfElse1(UnaryOperator):
#     def _apply(self, operand: Tensor) -> Tensor:
#         return torch.where(operand > 0, torch.ones_like(operand), torch.zeros_like(operand))
#
# # if x > 0, x, else 0
# class IfElse2(UnaryOperator):
#     def _apply(self, operand: Tensor) -> Tensor:
#         return torch.where(operand > 0, operand, torch.zeros_like(operand))

#
# # 和市场的平均
# class IfElse3(UnaryOperator):
#     def _apply(self, operand: Tensor) -> Tensor:
#         res = operand - operand.nanmean(dim=1, keepdim=True)
#         std = torch.sqrt(torch.mean((operand - operand.nanmean(dim=1, keepdim=True))**2, dim=1, keepdim=True))
#         return torch.where(res > std, operand, torch.where(res>-std, torch.zeros_like(operand),-operand))
#

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
            lhs = lhs[...,None]
        elif len(lhs.shape) > len(rhs.shape):
            rhs = rhs[...,None]
        epsilon = torch.tensor(1e-8, device=lhs.device)
        return lhs / (rhs  + epsilon)

    @property
    def feature_units(self):
        return 'other'

# class Pow(BinaryOperator):
#     def _apply(self, lhs: Tensor, rhs: Tensor) -> Tensor: return lhs ** rhs

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
        return lhs.min(rhs)

    @property
    def is_featured(self):
        return self._lhs.is_featured and self._rhs.is_featured

    @property
    def feature_units(self):
        raise self._lhs.feature_units == self._rhs.feature_units
        return self._lhs.feature_units

# class Rel_Div(BinaryOperator):
#     def _apply(self, lhs: Tensor, rhs: Tensor) -> Tensor:
#         return (lhs - rhs) / (lhs + rhs)
#
#
# class Perc_Rank_Diff(BinaryOperator):
#     def _apply(self, lhs: Tensor, rhs: Tensor) -> Tensor:
#         rank_lhs = lhs.argsort().argsort().float() / (len(lhs) - 1)
#         rank_rhs = rhs.argsort().argsort().float() / (len(rhs) - 1)
#         return rank_lhs - rank_rhs
#
#
# class Mean_Dis(BinaryOperator):
#     def _apply(self, lhs: Tensor, rhs: Tensor) -> Tensor:
#         mean_lhs = lhs.mean()
#         return (lhs - mean_lhs) ** 2
#
#
# class Perc_Rank_Div(BinaryOperator):
#     def _apply(self, lhs: Tensor, rhs: Tensor) -> Tensor:
#         rank_lhs = lhs.argsort().argsort().float() / (len(lhs) - 1)
#         rank_rhs = rhs.argsort().argsort().float() / (len(rhs) - 1)
#         return rank_lhs / rank_rhs
#
#
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
#
#
# class Perc_Diff(BinaryOperator):
#     def _apply(self, lhs: Tensor, rhs: Tensor) -> Tensor:
#         if lhs.shape[1] != rhs.shape[1]:
#             print('dim error')
#         return (lhs - rhs) / rhs
#
#
# class Rel_Strength(BinaryOperator):
#     def _apply(self, lhs: Tensor, rhs: Tensor) -> Tensor:
#         return lhs / (lhs + rhs)
#
#
# class IfElse4(BinaryOperator):
#     def _apply(self, lhs: Tensor, rhs: Tensor) -> Tensor:
#         condition = lhs - rhs > 0
#         return torch.where(condition, torch.ones_like(lhs), -torch.ones_like(lhs))
#
#     @property
#     def is_featured(self):
#         return self._lhs.is_featured and self._rhs.is_featured


class Ref(RollingOperator):
    # 获取过去-dt时刻的数据

    def evaluate(self, data: StockData, period: slice = slice(0, 1)) -> Tensor:
        self._delta_time = self._delta_time if not self._operand.is_filtered else 0
        start = period.start - self._delta_time
        stop = period.stop - self._delta_time
        values = self._operand.evaluate(data, slice(start, stop))
        if self._operand.is_filtered:
            return values[:,:,0]
        return values

    def _apply(self, operand: Tensor) -> Tensor:
        # This is just for fulfilling the RollingOperator interface
        ...


class Mean(RollingOperator):
    def _apply(self, operand: Tensor) -> Tensor:
        if self._operand:
            return operand.nanmean(dim=-1)  # 相当于去掉了nan后的数组的均值
        return operand.mean(dim=-1)


class Sum(RollingOperator):
    def _apply(self, operand: Tensor) -> Tensor:
        if self._operand:
            return operand.nansum(dim=-1)  # 相当于去掉了nan后的数组的和
        return operand.sum(dim=-1)


class Std(RollingOperator):
    def _apply(self, operand: Tensor) -> Tensor:
        if self._operand:
            return torch.sqrt(torch.nanmean((operand-operand.nanmean(dim=-1)[...,None])**2,dim=-1))
        return operand.std(dim=-1)

    @property
    def feature_units(self):
        return 'other'

class Var(RollingOperator):
    def _apply(self, operand: Tensor) -> Tensor:
        if self._operand:
            return operand.nanmean((operand-operand.nanmean(dim=-1))**2,dim=-1)
        return operand.var(dim=-1)

    @property
    def feature_units(self):
        return 'other'

class Skew(RollingOperator):
    def _apply(self, operand: Tensor) -> Tensor:
        # skew = m3 / m2^(3/2)
        # if self._operand.is_filtered:
        #     central = operand - operand.nanmean(dim=-1, keepdim=True)
        #     m3 = (central ** 3).nanmean(dim=-1)
        #     m2 = (central ** 2).nanmean(dim=-1)
        #     return m3 / m2 ** 1.5
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
        # if self._operand.is_filtered:
        #     central = operand - operand.nanmean(dim=-1, keepdim=True)
        #     m4 = (central ** 4).nanmean(dim=-1)
        #     var = operand.var(dim=-1)
        #     return m4 / var ** 2 - 3
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
    def _apply(self, operand: Tensor) -> Tensor: return torch.nanmedian(dim=-1)[0]


class Mad(RollingOperator):
    def _apply(self, operand: Tensor) -> Tensor:
        if self._operand.is_filtered:
            central = operand - operand.nanmean(dim=-1, keepdim=True)
            return central.abs().nanmean(dim=-1)
        central = operand - operand.mean(dim=-1, keepdim=True)
        return central.abs().mean(dim=-1)


class Rank(RollingOperator):
    def _apply(self, operand: Tensor) -> Tensor:
        mask = operand.isnan().any(dim=-1)
        n = operand.shape[-1]
        last = operand[:, :, -1, None]
        left = (last < operand).count_nonzero(dim=-1)
        right = (last <= operand).count_nonzero(dim=-1)  # nan会返回0
        result = (right + left + (right > left)) / (2 * n)
        if not self._operand.is_filtered:
            result[mask] = torch.nan  # 只要时序切片里nan有不要这一坨了
        return result

    @property
    def feature_units(self):
        return 'other'

class Delta(RollingOperator):
    # Delta is not *really* a rolling operator, in that other rolling operators
    # deal with the values in (-dt, 0], while Delta only deal with the values
    # at -dt and 0. Nonetheless, it should be classified as rolling since it
    # modifies the time window.

    def evaluate(self, data: StockData, period: slice = slice(0, 1)) -> Tensor:
        self._delta_time = self._delta_time if not self._operand.is_filtered else 0
        start = period.start - self._delta_time
        stop = period.stop
        values = self._operand.evaluate(data, slice(start, stop))
        if not self._operand.is_filtered:
            return values[self._delta_time:] - values[:-self._delta_time]
        elif self._operand.is_filtered:
            return values[...,-1] - values[...,0]

    def _apply(self, operand: Tensor) -> Tensor:
        # This is just for fulfilling the RollingOperator interface
        ...


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
        mask = (min_values == 0.)
        min_values[mask] = 1  # 因为要统一一下，要么都是绝对的，要么都是相对的
        # 计算相对最低位的涨幅
        gain_from_min = (operand[...,-1] - min_values) / min_values
        gain_from_min[mask] = torch.nan
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
        mask = (max_values == 0.)
        max_values[mask] = 1  # 因为要统一一下，要么都是绝对的，要么都是相对的
        drop_from_max = (operand[...,-1] - max_values) / max_values
        drop_from_max[mask] = torch.nan
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


# # d期至今的变化百分比
# class Chg_Perc(RollingOperator):
#     def evaluate(self, data: StockData, period: slice = slice(0, 1)) -> Tensor:
#         start = period.start - self._delta_time
#         stop = period.stop
#         values = self._operand.evaluate(data, slice(start, stop))
#         return (values[self._delta_time:] - values[:-self._delta_time])/ values[:-self._delta_time]
#
#     def _apply(self, operand: Tensor) -> Tensor:
#         # This is just for fulfilling the RollingOperator interface
#         ...
#
#
# # 过去d期的累乘
# class Prod(RollingOperator):
#     def _apply(self, operand: Tensor) -> Tensor:
#         return operand.prod(dim=-1)

# 过去d期的zscore
class ZScore(RollingOperator):
    def _apply(self, operand: Tensor) -> Tensor:
        mean = operand.nanmean(dim=-1)
        std = torch.sqrt(torch.nanmean((operand-mean[...,None])**2,dim=-1))
        return (operand[:,:,-1] - mean) / std

    @property
    def feature_units(self):
        return 'other'

# # 过去d期的变异系数（均值/标准差）
# class CV(RollingOperator):
#     def _apply(self, operand: Tensor) -> Tensor:
#         mean = operand.mean(dim=-1)
#         std = operand.std(dim=-1)
#         return mean / std

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
        nan_mask = nan_mask1 | nan_mask2
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


# # Deprecated!
# Operators: List[Type[Expression]] = [
#     # Unary
#     Abs, Sign, Log,  # Square, SquareRoot, Cube, CubeRoot, Reciprocal, Inverse, Sin, Cos, Tan, Sigmoid, Exp, PercentileRank,IfElse1,IfElse2,IfElse3,
#     # Binary
#     Add, Sub, Mul, Div, Pow, Greater, Less,Rel_Div,Perc_Rank_Diff,Mean_Dis,Perc_Rank_Div,Euc_Dis,Perc_Diff, Rel_Strength,IfElse4,
#     # Rolling
#     Ref, Mean, Sum, Std, Var, Skew, Kurt, Max, Min,
#     Med, Mad, Rank, Delta, WMA, EMA, Chg_Perc, Prod, ZScore, CV, MinPos, MaxPos,
#     # Pair rolling
#     Cov, Corr
# ]
