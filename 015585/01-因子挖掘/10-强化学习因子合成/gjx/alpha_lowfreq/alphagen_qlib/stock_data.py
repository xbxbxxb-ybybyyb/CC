from typing import List, Union, Optional, Tuple
from enum import IntEnum
import numpy as np
import pandas as pd
import torch
import bisect


class FeatureType(IntEnum):
    pre_close = 0

    # 都是幅度
    close = 1
    vwap = 2
    high = 3
    low = 4
    open = 5

    turn = 6

    # 元
    amt = 7
    mkt_cap_ard = 8

    # 股
    free_float_shares = 9
    volume = 10

class TargetType(IntEnum):
    label = 11


class StockData:
    _qlib_initialized: bool = False

    def __init__(self,
                 start_time: str,
                 end_time: str,
                 file_path: str,
                 target_path: str,
                 max_backtrack_days: int = 40,
                 max_future_days: int = 1,
                 features: Optional[List[FeatureType]] = None,
                 device: torch.device = torch.device('cuda:0')) -> None:

        self.max_backtrack_days = max_backtrack_days
        self.max_future_days = max_future_days
        self._start_time = start_time
        self._end_time = end_time
        self._features = features if features is not None else list(FeatureType)
        self.device = device
        self.file_path = file_path
        self.target_path = target_path
        self.data, self.target, self.idx, self._dates, self._stock_ids = self.get_data()

    def _Dataloader(self, trade_date):
        # 先加载一下因子名列，因为我存的数据是numpy，所以我要知道在哪一列
        col = [f.name.lower() for f in self._features]
        # col[col.index('price940')] = '940'
        df = pd.read_pickle(self.file_path)
        df = df[(df.index.get_level_values(0)>='2018-01-02')&(df.index.get_level_values(0)<='2019-12-30')]
        target = pd.read_pickle(self.target_path)
        df['to_close'] = df['close'] # 487
        filtered_df = df.loc[df.index.get_level_values(0).isin(trade_date)]
        filtered_target = target.loc[target.index.get_level_values(0).isin(trade_date)]
        # 构造一个元组存下，第二个元素是一个矩阵
        filtered_df = filtered_df[col]
        # 这边要对齐一下数据，我想知道它的nan怎么处理的--在计算相关性哪些指标的时候才用mask等处理一下，但是没有改变数据集，感觉这样其实是最理想的
        return filtered_df, filtered_target

    def read_and_sort_dates(self, file_path):
        dates = []
        with open(file_path, 'r') as file:
            for line in file:
                # 读取每行的日期字符串，并去除可能的空白字符
                date_str = line.strip()
                # 将日期字符串添加到列表中
                dates.append(date_str)

        # 对日期字符串列表进行排序
        dates.sort()
        return dates

    def load_exprs(self) -> pd.DataFrame:
        # This evaluates an expression on the data and returns the dataframe
        # It might throw on illegal expressions like "Ref(constant, dtime)"
        # 替换成获取交易日的代码
        filename = "/data/user/000021/gjx/day.txt"
        # 使用pandas的read_csv函数来读取文件，然后将日期列转换为Timestamp对象
        date = self.read_and_sort_dates(filename)
        start_index = bisect.bisect_right(date, self._start_time)
        end_index = bisect.bisect_right(date, self._end_time)
        if date[end_index] != self._end_time:
            end_index -= 1
        trade_date = date[start_index-self.max_backtrack_days:end_index + 1]
        return self._Dataloader(trade_date)

    def get_data(self) -> Tuple[torch.Tensor, pd.Index, pd.Index]:
        features = [f.name.lower() for f in self._features]
        df, target = self.load_exprs()
        df['high'] = (df['high']-df['pre_close'])/df['pre_close']
        df['low'] = (df['low'] - df['pre_close']) / df['pre_close']
        df['open'] = (df['open'] - df['pre_close']) / df['pre_close']
        # df['940'] = (df['940'] - df['pre_close']) / df['pre_close']
        df['vwap'] = (df['vwap'] - df['pre_close']) / df['pre_close']
        df['close'] = (df['close'] - df['pre_close']) / df['pre_close']

        df = df.stack().unstack(level=1)
        dates = list(df.index.levels[0])  # type: ignore
        stock_ids = list(df.columns)

        # df1 = df.unstack(level=-1)  # 将第三层行索引转换为列索引
        # df1 = df1.stack(level=0).sort_index(level=0)  # 将原列索引变为行索引并交换
        # 找到target里每天的股票在df里的位置
        # df_idx = pd.DataFrame(index=pd.MultiIndex.from_product([list(dates),list(stock_ids)], names=['dt', 'Tickers']))
        # df_idx = df_idx.sort_index(level=None)
        # df_idx['idx'] = df_idx.groupby(level=0).cumcount()
        # target = pd.DataFrame(target, index=target.index)
        # result = target.merge(df_idx[['idx']], left_index=True, right_index=True, how='left')
        # idx = torch.tensor(result['idx'].values.reshape(len(dates), -1),dtype=int,device=self.device)
        indices_list = []

        # 遍历DataFrame的每一行，获取股票代码在股票列表中的索引
        for date in dates:
            daily_indices = []
            for stock in target.loc[(date,),:].index.get_level_values(1):
                if stock in stock_ids:
                    daily_indices.append(stock_ids.index(stock))
            if len(daily_indices) == 499:
                print('wrong')
            indices_list.append(daily_indices)
        idx = torch.tensor(indices_list,dtype=int,device=self.device)

        target = target.values
        target = target.reshape(len(dates),-1)
        values = df.values
        values = values.reshape((-1, len(features), values.shape[-1]))  # type: ignore
        return torch.tensor(values, dtype=torch.float, device=self.device), \
               torch.tensor(target, dtype=torch.float, device=self.device) , idx, dates, stock_ids
        # 日期 特征数 股票数

    @property
    def n_features(self) -> int:
        return len(self._features)

    @property
    def n_stocks(self) -> int:
        return self.data.shape[-1]

    @property
    def n_days(self) -> int:
        return self.data.shape[0] - self.max_backtrack_days - self.max_future_days

    def make_dataframe(
            self,
            data: Union[torch.Tensor, List[torch.Tensor]],
            columns: Optional[List[str]] = None
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
            columns = ['factor' + str(i) for i in range(data.shape[2])]
        n_days, n_stocks, n_columns = data.shape
        # if self.n_days != n_days:
        #     raise ValueError(f"number of days in the provided tensor ({n_days}) doesn't "
        #                      f"match that of the current StockData ({self.n_days})")
        # if self.n_stocks != n_stocks:
        #     raise ValueError(f"number of stocks in the provided tensor ({n_stocks}) doesn't "
        #                      f"match that of the current StockData ({self.n_stocks})")
        # if len(columns) != n_columns:
        #     raise ValueError(f"size of columns ({len(columns)}) doesn't match with "
        #                      f"tensor feature count ({data.shape[2]})")
        if self.max_future_days == 0:
            date_index = self._dates[self.max_backtrack_days:]
        else:
            date_index = self._dates[self.max_backtrack_days:-self.max_future_days]
        index = pd.MultiIndex.from_product([date_index, range(0,500)])
        data = data.reshape(-1, n_columns)
        return pd.DataFrame(data.detach().cpu().numpy(), index=index, columns=columns)
