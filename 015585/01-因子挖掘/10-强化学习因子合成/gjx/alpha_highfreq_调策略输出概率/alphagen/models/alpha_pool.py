from itertools import count
import math
from typing import List, Optional, Tuple, Set
from abc import ABCMeta, abstractmethod

import numpy as np
import torch
import re
from torch import Tensor
from alphagen.data.calculator import AlphaCalculator

from alphagen.data.expression import Expression
from alphagen.utils.correlation import batch_pearsonr, batch_spearmanr
from alphagen.utils.pytorch_utils import masked_mean_std
from alphagen_qlib.stock_data import StockData


class AlphaPoolBase(metaclass=ABCMeta):
    def __init__(
        self,
        capacity: int,
        calculator: AlphaCalculator,
        device: torch.device = torch.device('cpu')
    ):
        self.capacity = capacity
        self.calculator = calculator
        self.device = device

    @abstractmethod
    def to_dict(self) -> dict: ...

    @abstractmethod
    def try_new_expr(self, expr: Expression, num_step: int) -> float: ...

    @abstractmethod
    def test_pool(self, calculator: AlphaCalculator) -> Tuple[float, float, float]: ...


class AlphaPool(AlphaPoolBase):
    def __init__(
        self,
        capacity: int,
        calculator: AlphaCalculator,
        ic_lower_bound: Optional[float] = None,
        l1_alpha: float = 5e-3,
        device: torch.device = torch.device('cpu')
    ):
        super().__init__(capacity, calculator, device)

        self.size: int = 0
        self.exprs: List[Optional[Expression]] = [None for _ in range(capacity + 1)]
        self.single_ics: np.ndarray = np.zeros(capacity + 1)
        self.mutual_ics: np.ndarray = np.identity(capacity + 1)
        self.weights: np.ndarray = np.zeros(capacity + 1)
        self.best_ic_ret: float = -1.
        self.worst_ic_ret: float = -1.
        self.abs_mean_ic_ret: float = -1.

        self.ic_lower_bound = ic_lower_bound or -1.
        self.l1_alpha = l1_alpha

        self.eval_cnt = 0

    @property
    def state(self) -> dict:
        return {
            "exprs": list(self.exprs[:self.size]),
            "ics_ret": list(self.single_ics[:self.size]),
            "best_ic_ret": self.best_ic_ret
        }

    def to_dict(self) -> dict:
        return {
            "exprs": [str(expr) for expr in self.exprs[:self.size]],
        }

    def try_new_expr(self, expr: Expression, num_step: int) -> float:
        instance_str = str(expr)
        # 使用 split 方法根据 () 和 , 分割字符串
        split_str = re.split(r'[(),$]', instance_str)
        if len(split_str) == 2: # 不允许一个截面算子一个特征输出
            return -0.5
        ric_ret, ic_mut = self._calc_ics(expr, ic_mut_threshold=0.7)

        if ric_ret is None or ic_mut is None or np.isnan(ric_ret) or np.isnan(ic_mut).any():
            return 0.  # 返回的是rewardwo,

        if expr in self.exprs:
            return np.abs(ric_ret)

        if np.abs(ric_ret)<self.ic_lower_bound:
            return np.abs(ric_ret)

        self._add_factor(expr, ric_ret, ic_mut)
        if self.size > 1:
            self._pop()

        # self.weights = 1/self.size * np.where(self.single_ics[:self.size] > 0, 1, -1)

        # 记录最优单因子和最低单因子
        single_ics = self.single_ics[:self.size]
        self.best_ic_ret = single_ics[np.argmax(np.abs(single_ics))]
        self.worst_ic_ret = single_ics[np.argmin(np.abs(single_ics))]
        self.abs_mean_ic_ret = np.mean(np.abs(single_ics))
        self.eval_cnt += 1

        reward = np.abs(ric_ret)
        # if (num_step//2048)%3 == 0:
        #     reward = np.abs(ric_ret)
        # elif (num_step//2048)%3 == 1:
        #     ricir_ret = self.calculator.calc_single_rICIR(expr)
        #     reward = np.abs(ricir_ret)
        # else:
        #     turnover = self.calculator.calc_turnover(expr)
        #     reward = 0.1-(turnover[0] + turnover[-1])/2
        return reward

    def test_pool(self, calculator: AlphaCalculator) -> Tuple[float, float, float]:
        if self.size == 0:
            return 0,0,0
        single_ics = [calculator.calc_single_rIC_ret(f) for f in self.exprs[:self.size]]  # 改成了取均值s
        best_ic_ret = single_ics[np.argmax(np.abs(single_ics))]
        worst_ic_ret = single_ics[np.argmin(np.abs(single_ics))]
        abs_mean_ic_ret = np.mean(np.abs(single_ics))
        return best_ic_ret, worst_ic_ret, abs_mean_ic_ret

    # def force_load_exprs(self, exprs: List[Expression]) -> None:
    #     for expr in exprs:
    #         ic_ret, ic_mut = self._calc_ics(expr, ic_mut_threshold=None)
    #         assert ic_ret is not None and ic_mut is not None
    #         self._add_factor(expr, ic_ret, ic_mut)
    #         assert self.size <= self.capacity
    #     self._optimize(alpha=self.l1_alpha, lr=5e-4, n_iter=500)


    # def test_ensemble(self, calculator: AlphaCalculator) -> Tuple[float, float]:
    #     ic, rank_ic = calculator.calc_pool_all_ret(self.exprs[:self.size], self.weights)  # 改成了取均值s
    #     return ic, rank_ic
    #
    # def evaluate_ensemble(self) -> float:
    #     rank_ic = self.calculator. calc_single_rIC_ret(self.exprs[:self.size])  # 改成了取均值
    #     return rank_ic

    @property
    def _under_thres_alpha(self) -> bool:
        if self.ic_lower_bound is None or self.size > 1:
            return False
        return self.size == 0 or abs(self.single_ics[0]) < self.ic_lower_bound

    def _calc_ics(
        self,
        expr: Expression,
        ic_mut_threshold: Optional[float] = None
    ) -> Tuple[float, Optional[List[float]]]:
        single_ric = self.calculator.calc_single_rIC_ret(expr)
        if not self._under_thres_alpha and single_ric < self.ic_lower_bound:
            return single_ric, None

        mutual_ics = []
        for i in range(self.size):
            mutual_ic = self.calculator.calc_mutual_IC(expr, self.exprs[i])
            if ic_mut_threshold is not None and mutual_ic > ic_mut_threshold:
                return single_ric, None
            mutual_ics.append(mutual_ic)

        return single_ric, mutual_ics

    def _add_factor(
        self,
        expr: Expression,
        ic_ret: float,
        ic_mut: List[float]
    ):
        n = self.size
        self.exprs[n] = expr
        self.single_ics[n] = ic_ret
        for i in range(n):
            self.mutual_ics[i][n] = self.mutual_ics[n][i] = ic_mut[i]
        # self.weights[n] = ic_ret  # An arbitrary init value
        self.size += 1

    def _pop(self) -> None:
        if self.size <= self.capacity:
            return
        idx = np.argmin(np.abs(self.single_ics)) # 相当于淘汰101个里面最差的，放在最外端，但是size是限制好不包括最后一个的
        self._swap_idx(idx, self.capacity)  # 每次都会把要淘汰的放在最后一个，长度都是size+1，只有size范围内的是合法的
        self.size = self.capacity # 超过一个就会变成这样

    def _swap_idx(self, i, j) -> None:
        if i == j:
            return
        self.exprs[i], self.exprs[j] = self.exprs[j], self.exprs[i]
        self.single_ics[i], self.single_ics[j] = self.single_ics[j], self.single_ics[i]
        self.mutual_ics[:, [i, j]] = self.mutual_ics[:, [j, i]]
        self.mutual_ics[[i, j], :] = self.mutual_ics[[j, i], :]
        # self.weights[i], self.weights[j] = self.weights[j], self.weights[i]

