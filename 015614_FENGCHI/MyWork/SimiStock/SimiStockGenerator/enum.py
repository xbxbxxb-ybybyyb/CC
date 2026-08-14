# coding: utf-8
# Author：fengchi863
# Date ：2022/3/8 15:17

from typing import List
from dataclasses import dataclass


@dataclass
class Hedge:
    stk_id: int
    date: int
    hedge_list: List[int]
    hedge_weight: List[float]
