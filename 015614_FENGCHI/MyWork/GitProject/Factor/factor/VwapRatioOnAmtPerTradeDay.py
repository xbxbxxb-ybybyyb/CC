import numpy as np
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
from xfactor.Util import data_filter


class VwapRatioOnAmtPerTradeDay(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # fix_times = ["1000", "1030", '1100', '1300', '1330', '1400', '1430']
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ['FactorData.Basic_factor.buytradeamt_minute',
                   'FactorData.Basic_factor.buytradenum_minute',
                   'FactorData.Basic_factor.amt_minute',
                   'FactorData.Basic_factor.volume_minute',
                   'FactorData.Basic_factor.limit_status_minute', ]
    # 依赖的个人因子库的因子，默认为空，可不设置
    depend_factors = []
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0

    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    reform_window = 3
    
    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop1', 'drop4'])
        limit_status = database.depend_data["FactorData.Basic_factor.limit_status_minute"].copy()
        b_amt = database.depend_data["FactorData.Basic_factor.buytradeamt_minute"].copy().iloc[-237 * self.lag:, :]
        b_amt = data_filter(b_amt, limit_status, method='minute')
        b_num = database.depend_data["FactorData.Basic_factor.buytradenum_minute"].copy().iloc[-237 * self.lag:, :]
        b_num = data_filter(b_num, limit_status, method='minute')
        b_amt_per_trade = b_amt / b_num
        b_amt_per_trade_quantile = b_amt_per_trade.quantile(0.7, axis=0)
        filter_index = np.zeros(b_amt_per_trade.shape)
        filter_index[(b_amt_per_trade.values - b_amt_per_trade_quantile.values) > 0] = 1
        amt = database.depend_data["FactorData.Basic_factor.amt_minute"].copy().iloc[-237 * self.lag:, :]
        amt = data_filter(amt,limit_status,method='minute')
        vol = database.depend_data["FactorData.Basic_factor.volume_minute"].copy().iloc[-237 * self.lag:, :]
        vol = data_filter(vol,limit_status,method='minute')
        vwap = amt/vol
        ans = (vwap*filter_index/filter_index).mean() / vwap.mean()
        return -ans

        # 针对播放后的结果，进行相关的rolling等操作。所用的前序数据长度应为reform_window。默认不修改temp_result， 可不重写。
    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean()
