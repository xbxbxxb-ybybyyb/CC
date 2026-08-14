import datetime
import json
from typing import List, Tuple
from alphagen.data.expression import *
from alphagen_generic.features import *

from alphagen_qlib.stock_data import StockData


def load_recent_data(instrument: str,
                     window_size: int = 365,
                     offset: int = 1,
                     **kwargs) -> Tuple[StockData, str]:
    today = datetime.date.today()
    start_date = str(today - datetime.timedelta(days=window_size))
    end_date = str(today - datetime.timedelta(days=offset))

    return StockData(instrument=instrument,
                     start_time=start_date,
                     end_time=end_date,
                     max_future_days=0,
                     **kwargs), end_date

import re

def add_quotes_around_substrings(list1, list2):
    list2_sorted = sorted(list2, key=len, reverse=True)

    result = []
    for item in list1:
        for sub in list2_sorted:
            # 使用正则表达式进行替换，确保每个子字符串只被替换一次
            item = re.sub(f'(?<!")({re.escape(sub)})(?!")', r'"\1"', item)
        result.append(item)
    return result


def load_alpha_pool(raw) -> Tuple[List[Expression], List[float]]:
    exprs_raw = raw['exprs']
    spec = ['[93000,93100]', '[93900,93957]', '[93000,93500]', '[93500,93957]','<mkt_mean', '>mkt_mean', '>ts_mean', '<ts_mean', '<const_0',
                '>const_0', 'when_y>0', 'when_y<0', 'when_y<1/4[y]', 'when_y>3/4[y]']
    exprs = [expr_raw.replace('$open', 'open_').replace('$', '') for expr_raw in exprs_raw]

    # 调用函数
    exprs = add_quotes_around_substrings(exprs, spec)
    exprs = [eval(expr_raw) for expr_raw in exprs]
    # weights = raw['weights']
    return exprs#, weights


def load_alpha_pool_by_path(path: str) -> Tuple[List[Expression], List[float]]:
    with open(path, encoding='utf-8') as f:
        raw = json.load(f)
        return load_alpha_pool(raw)

