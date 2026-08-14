from typing import List, Optional, Tuple
from torch import Tensor
import torch
from alphagen.data.calculator import AlphaCalculator
from alphagen.data.expression import Expression
from alphagen.utils.correlation import batch_pearsonr, batch_spearmanr
from alphagen.utils.pytorch_utils import normalize_by_day
from alphagen_qlib.stock_data import StockData
import numpy as np


class QLibStockDataCalculator(AlphaCalculator):
    def __init__(self, data: StockData, target: Optional[Expression]):
        self.data = data

        if target is None:  # Combination-only mode
            self.target_value = None
        else:
            start1 = self.data.max_backtrack_days
            stop1 = self.data.max_backtrack_days + data.n_days
            self.target_value = normalize_by_day(self.data.target[start1:stop1,:])

    def _calc_alpha(self, expr: Expression) -> Tensor:
        return normalize_by_day(expr.evaluate(self.data))  # 因为period已经在定义类的时候算过了[在tree.py中合在一起的时候就是定义类了]，所以这里是默认的slice就行了

    def _calc_IC(self, value1: Tensor, value2: Tensor) -> float:
        return batch_pearsonr(value1, value2).mean().item()

    def _calc_rIC(self, value1: Tensor, value2: Tensor) -> float:
        return batch_spearmanr(value1, value2).mean().item()

    def _calc_rICIR(self, value1: Tensor, value2: Tensor) -> float:
        return batch_spearmanr(value1, value2).mean().item()/ batch_spearmanr(value1, value2).std().item()

    def make_ensemble_alpha(self, exprs: List[Expression], weights: List[float]) -> Tensor:
        n = len(exprs)
        factors: List[Tensor] = [self._calc_alpha(exprs[i]) * weights[i] for i in range(n)]
        return sum(factors)  # type: ignore

    def calc_single_rIC(self, exprs: List[Expression]) -> Tensor:
        n = len(exprs)
        factors: List[Tensor] = [batch_spearmanr(self._calc_alpha(exprs[i]), self.target_value) for i in range(n)]
        return factors  # type: ignore

    def calc_single_rICIR(self, expr: Expression) -> Tensor:
        factor = self._calc_rICIR(self._calc_alpha(expr), self.target_value)
        return factor  # type: ignore

    def calc_single_alpha(self, exprs: List[Expression]) -> Tensor:
        n = len(exprs)
        factors: List[Tensor] = [self._calc_alpha(exprs[i]) for i in range(n)]
        return factors  # type: ignore

    def calc_single_IC_ret(self, expr: Expression) -> float:
        value = self._calc_alpha(expr)
        return self._calc_IC(value, self.target_value)

    def calc_single_rIC_ret(self, expr: Expression) -> float:
        value = self._calc_alpha(expr)
        return self._calc_rIC(value, self.target_value)

    def calc_single_all_ret(self, expr: Expression) -> Tuple[float, float]:
        value = self._calc_alpha(expr)
        return self._calc_IC(value, self.target_value), self._calc_rIC(value, self.target_value)

    def calc_mutual_IC(self, expr1: Expression, expr2: Expression) -> float:
        value1, value2 = self._calc_alpha(expr1), self._calc_alpha(expr2)
        return self._calc_IC(value1, value2)

    def calc_pool_IC_ret(self, exprs: List[Expression], weights: List[float]) -> float:
        with torch.no_grad():
            ensemble_value = self.make_ensemble_alpha(exprs, weights)
            return self._calc_IC(ensemble_value, self.target_value)

    def calc_pool_rIC_ret(self, exprs: List[Expression], weights: List[float]) -> float:
        with torch.no_grad():
            ensemble_value = self.make_ensemble_alpha(exprs, weights)
            return self._calc_rIC(ensemble_value, self.target_value)

    def calc_pool_all_ret(self, exprs: List[Expression], weights: List[float]) -> Tuple[float, float]:
        with torch.no_grad():
            ensemble_value = self.make_ensemble_alpha(exprs, weights)
            return self._calc_IC(ensemble_value, self.target_value), self._calc_rIC(ensemble_value, self.target_value)

    def calc_turnover(self, expr: Expression) -> List[float]:
        value = self._calc_alpha(expr)
        turn_group = []
        pre_groups_idx = None
        for row in value:
            idx = torch.range(0, len(row) - 1)
            row1 = row[~row.isnan()]
            idx1 = idx[~row.isnan()]

            sorted_row = row1.argsort()
            sorted_idx = idx1[sorted_row]

            groups_idx = np.array_split(sorted_idx, 10)
            if pre_groups_idx is not None:
                list_groups_sets = [set(group) for group in pre_groups_idx]
                list1_groups_sets = [set(group1) for group1 in groups_idx]

                # 计算每一组的变化率
                diff_counts = np.array(
                    [len(group1 - group) for group, group1 in zip(list_groups_sets, list1_groups_sets)])
                group_lengths = np.array([len(group) for group in list_groups_sets])
                change_rates = diff_counts / group_lengths
                turn_group.append(change_rates)

            pre_groups_idx = groups_idx

        return list(np.mean(turn_group, axis=0))  # turn_group的维度是(日期，10)

