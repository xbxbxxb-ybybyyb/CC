from typing import Tuple, Optional
import torch
from torch import nn, Tensor


def masked_mean_std(
    x: Tensor,
    n: Optional[Tensor] = None,
    mask: Optional[Tensor] = None
) -> Tuple[Tensor, Tensor]:
    """
    `x`: [days, stocks], input data
    `n`: [days], should be `(~mask).sum(dim=1)`, provide this to avoid necessary computations
    `mask`: [days, stocks], data masked as `True` will not participate in the computation, \
    defaults to `torch.isnan(x)`
    """
    if mask is None:
        mask = torch.isnan(x)
    if n is None:
        n = (~mask).sum(dim=1)
    x = x.clone()
    x[mask] = 0
    mean = x.sum(dim=1) / n
    if torch.nanmean(torch.abs(x))>1e10:
        mean /= 1e10
        x /= 1e10
    std = ((((x - mean[:, None]) * ~mask) ** 2).sum(dim=1) / n).sqrt()
    x[mask] = torch.nan
    return mean, std, x


def normalize_by_day(value: Tensor) -> Tensor:
    mean, std, value = masked_mean_std(value)
    value = (value - mean[:, None]) / std[:, None]
    # nan_mask = torch.isnan(value)
    # value[nan_mask] = 0.
    return value

import re


# 用于获取filter和binaryfilter的筛选条件列表
def extract_div_rule(expression: str):
    # 匹配最内层的 Filter 或 BinaryFilter 以及括号内的内容
    pattern = r"(Filter|BinaryFilter)\(([^()]*)\)"

    # 存放结果的列表
    result = []

    # 循环处理，直到没有更多的 Filter
    while True:
        # 搜索当前表达式中的所有 Filter 和 BinaryFilter
        match = re.search(pattern, expression)  # 索引

        if not match:
            break

        # 获取括号内的参数列表
        params = match.group(2).split(",")

        # 取最后一个参数并去除空格
        last_param = params[-1].strip()
        result.append(last_param)

        # 替换已经处理过的最内层 Filter 为空
        expression = expression[:match.start()] + expression[match.end():]

    return result

