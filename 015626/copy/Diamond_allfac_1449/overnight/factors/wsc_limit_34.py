from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *


class wsc_limit_34(FactorGenerator):

    def __init__(self, *args, **kwargs):
        name1 = 'open_alla_daily_' + minute_to_daily_tag
        required_columns=[name1, 'close_alla_daily', 'limit_alla_daily', 'stopping_alla_daily', 'preclose_alla_daily']
        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=30, **kwargs)

    def on_bar(self, data_dict):
        # 前一个交易日涨停的股票当天开盘收益率之和与前一个交易日跌停的股票当天开盘收益率之和相加
        open_alla_daily_trun = data_dict['open_alla_daily_' + minute_to_daily_tag]
        close_alla_daily = data_dict['close_alla_daily']
        limit_alla_daily = data_dict['limit_alla_daily']
        stopping_alla_daily = data_dict['stopping_alla_daily']
        preclose_alla_daily = data_dict['preclose_alla_daily']

        limit_judgement1 = (close_alla_daily == limit_alla_daily)  # 判断当天股票是否涨停
        limit_judgement2 = (close_alla_daily == stopping_alla_daily)  # 判断当天股票是否跌停
        # limit_judgement1[limit_judgement1<1] = np.nan  # FALSE那部分不置为nan不会影响求和结果
        stk_ret = open_alla_daily_trun / preclose_alla_daily - 1  # 股票开盘收益率


        factor = -((limit_judgement1 | limit_judgement2).shift(1) * stk_ret).sum(axis=1) / stopping_alla_daily.count(axis=1)
        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor