from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import xfactor.Util as ut


class RTC(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.amt_minute", "FactorData.Basic_factor.close_minute"]
    # 依赖的个人因子库的因子，默认为空，可不设置
    # depend_factors = ["SampleFactor"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0

    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    reform_window = 12

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        minute_amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        minute_close = database.depend_data['FactorData.Basic_factor.close_minute']
        fmt = '%Y-%m-%d'
        date_list = np.unique(minute_amt.index.strftime(fmt))
        result_df = pd.DataFrame(index=[pd.Timestamp(date) for date in date_list], columns=minute_amt.columns)

        for date in date_list:
            cr = minute_close.loc[date].pct_change()
            tr = minute_amt.loc[date].replace(0., np.nan).pct_change()
            result_df.loc[date] = ut.array_coef(tr.iloc[-60:], cr.iloc[-60:])
        ans = result_df.iloc[-1]
        return -ans

    def reform(self, temp_result):
        return temp_result