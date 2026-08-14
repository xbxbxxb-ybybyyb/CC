from typing import List, Union, Optional, Tuple
from enum import IntEnum
import numpy as np
import pandas as pd
import torch
import bisect
import gc



class FeatureType(IntEnum):
    NumTrades = 0
    TotalVolumeTrade = 1
    TotalValueTrade = 2
    LastPx = 3
    HighPx = 4
    LowPx = 5
    TotalBidQty = 6
    TotalOfferQty = 7
    WeightedAvgBidPx = 8
    WeightedAvgOfferPx = 9
    Buy1Price = 10
    Buy2Price = 11
    Sell1Price = 12
    Sell2Price = 13
    Buy1OrderQty = 14
    Buy2OrderQty = 15
    Sell1OrderQty = 16
    Sell2OrderQty = 17
    Buy1NumOrders = 18
    Buy2NumOrders = 19
    Sell1NumOrders = 20
    Sell2NumOrders = 21
    pre_close = 22
    ff_shares = 23


class TargetType(IntEnum):
    label = 24  # 这个是收益率


class StockData:
    _qlib_initialized: bool = False

    def __init__(
        self,
        start_time: str,
        end_time: str,
        file_path: str,
        target_path: str,
        n_windows :int,
        max_backtrack_days: int = 0,
        max_future_days: int = 0,
        features: Optional[List[FeatureType]] = None,
        device: torch.device = torch.device("cuda:0"),
    ) -> None:

        self.max_backtrack_days = max_backtrack_days
        self.max_future_days = max_future_days
        self._start_time = start_time
        self._end_time = end_time
        self._features = features if features is not None else list(FeatureType)
        self.target_path = target_path
        self.device = device
        self.file_path = file_path
        self.n_windows = n_windows
        self.data, self.target, self._dates, self._stock_ids = self._get_data()


    def _Dataloader(self, exprs, trade_date):
        # 先加载一下因子名列，因为我存的数据是numpy，所以我要知道在哪一列
        col = [f.name for f in self._features] + [
            f.name for f in list(TargetType)
        ]
        # df = pd.read_pickle(self.file_path)
        values = np.load(self.file_path)
        # dates = list(np.load('/data/user/000021/gjx/dates.npy'))
        target = pd.read_pickle(self.target_path)
        dates = sorted((set(target.index.get_level_values(0))))
        dates = [date.strftime("%Y-%m-%d") for date in dates]
        idx1 = dates.index(trade_date[0])
        idx2 = dates.index(trade_date[-1])
        filter_values = values[idx1:idx2+1,...]
        # filter_df = df.loc[df.index.get_level_values(0).isin(trade_date)].copy()
        gc.collect()
        # df = df[col]
        # 这边要对齐一下数据，我想知道它的nan怎么处理的--在计算相关性哪些指标的时候才用mask等处理一下，但是没有改变数据集，感觉这样其实是最理想的
        return filter_values, target.loc[target.index.get_level_values(0).isin(trade_date)]

    def read_and_sort_dates(self, file_path):
        dates = []
        with open(file_path, "r") as file:
            for line in file:
                # 读取每行的日期字符串，并去除可能的空白字符
                date_str = line.strip()
                # 将日期字符串添加到列表中
                dates.append(date_str)

        # 对日期字符串列表进行排序
        dates.sort()
        return dates

    def _load_exprs(self, exprs: Union[str, List[str]]) -> pd.DataFrame:
        # This evaluates an expression on the data and returns the dataframe
        # It might throw on illegal expressions like "Ref(constant, dtime)"
        if not isinstance(exprs, list):
            exprs = [exprs]
        # 替换成获取交易日的代码
        filename = '/data/user/000021/gjx/day.txt'
        # 使用pandas的read_csv函数来读取文件，然后将日期列转换为Timestamp对象
        date = self.read_and_sort_dates(filename)
        start_index = bisect.bisect_right(date, self._start_time)
        end_index = bisect.bisect_right(date, self._end_time)
        if date[end_index] != self._end_time:
            end_index -= 1
        trade_date = date[start_index : end_index + 1]
        return self._Dataloader(exprs, trade_date)

    def _get_data(self) -> Tuple[torch.Tensor, pd.Index, pd.Index]:
        features = [f.name for f in self._features]
        values, target = self._load_exprs(features)
        dates = sorted((set(target.index.get_level_values(0))))  # 不能用下面这个，把切片前的也放进来了
        stock_ids = target.index.levels[1]
        self.n_stocks = 500

        # values = df.values
        values = values.reshape((len(dates), self.n_stocks, -1,len(features)))  # type: ignore
        values = values.transpose(0,1,3,2)
        return (
            torch.tensor(values, dtype=torch.float, device=self.device),
            torch.tensor(target.values.reshape(len(dates), self.n_stocks), dtype=torch.float, device=self.device),
            dates,
            stock_ids,
        )
        # 日期 时刻 特征数 股票数

    @property
    def n_features(self) -> int:
        return len(self._features)

    @property
    def n_days(self) -> int:
        return self.data.shape[0] - self.max_backtrack_days - self.max_future_days

    def get_idx(self, t: str) -> int:
        # 根据时刻t返回索引【实际上原数据在第三维的索引值】
        time_group = [('9:30', '9:31'), ('9:31', '9:39'), ('9:39', '9:40')]
        interval = ['3s', '15s', '3s']
        time_filter = []
        for i in range(0, 3):
            times = pd.date_range(start=time_group[i][0], end=time_group[i][1], freq=interval[i]).time
            times = [time for time in times if time != pd.Timestamp('9:15').time()]

            # 将时间转换为9150000这种形式
            times = [int(time.strftime('%H%M%S%f')[:-3]) for time in times]
            time_filter += times[:-1]

        t = int(t + '000')
        return time_filter.index(t)

    def get_time_idx(self, t1: str, t2: str) -> List[int]:
        # 根据时刻t1和t2返回索引范围
        idx1 = self.get_idx(t1)
        idx2 = self.get_idx(t2)
        return idx1,idx2 # 左开右闭的区间，里面的每个都是要取得

    def make_dataframe(
        self,
        data: Union[torch.Tensor, List[torch.Tensor]],
        columns: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Parameters:
        - `data`: a tensor of size `(n_days, n_stocks[, n_columns])`, or
        a list of tensors of size `(n_days, n_stocks)`
        - `columns`: an optional list of column names
        """
        if isinstance(data, list):
            data = torch.stack(data, dim=2)
        if len(data.shape) == 2:
            data = data.unsqueeze(2)
        if columns is None:
            columns = [str(i) for i in range(data.shape[2])]
        n_days, n_stocks, n_columns = data.shape
        if self.n_days != n_days:
            raise ValueError(
                f"number of days in the provided tensor ({n_days}) doesn't "
                f"match that of the current StockData ({self.n_days})"
            )
        if self.n_stocks != n_stocks:
            raise ValueError(
                f"number of stocks in the provided tensor ({n_stocks}) doesn't "
                f"match that of the current StockData ({self.n_stocks})"
            )
        if len(columns) != n_columns:
            raise ValueError(
                f"size of columns ({len(columns)}) doesn't match with "
                f"tensor feature count ({data.shape[2]})"
            )
        if self.max_future_days == 0:
            date_index = self._dates[self.max_backtrack_days :]
        else:
            date_index = self._dates[self.max_backtrack_days : -self.max_future_days]
        index = pd.MultiIndex.from_product([date_index, self._stock_ids])
        data = data.reshape(-1, n_columns)
        return pd.DataFrame(data.detach().cpu().numpy(), index=index, columns=columns)
