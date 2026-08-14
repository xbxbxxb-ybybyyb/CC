from xfactor.BaseFactor import BaseFactor
import xfactor.Util as ut
import numpy as np


class IVR_000300_20(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.pct_chg", "FactorData.Basic_factor.amt_by_yuan", "FactorData.Basic_factor.mkt_cap_ard",
                   "FactorData.Basic_factor.s_val_pb_new", "FactorData.Basic_factor.pct_chg-000300.SH"]
    #依赖的个人因子库的因子，默认为空，可不设置
    # depend_factors = ["MinCloseCallAmtRatio"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 20
    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    # reform_window = 10

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        stock_pct_chg = database.depend_data['FactorData.Basic_factor.pct_chg']
        amt = database.depend_data['FactorData.Basic_factor.amt_by_yuan']
        mkt_cap = database.depend_data['FactorData.Basic_factor.mkt_cap_ard']
        pb = database.depend_data['FactorData.Basic_factor.s_val_pb_new']
        index_pct_chg = database.depend_data['FactorData.Basic_factor.pct_chg-000300.SH']
        mkt_cap_rank = mkt_cap.shift(1)[amt > 0].rank(axis=1)
        stock_num = (amt > 0).sum(axis=1)
        pb[pb <= 0] = np.nan
        pb_rank = pb.shift(1)[amt > 0].rank(axis=1)
        stock_num_pb = (pb > 0)[amt > 0].sum(axis=1)
        SMB = stock_pct_chg[mkt_cap_rank.apply(lambda x: x <= round(stock_num * 0.3))].mean(axis=1) - \
                        stock_pct_chg[mkt_cap_rank.apply(lambda x: x > round(stock_num * 0.7))].mean(axis=1)
        HML = stock_pct_chg[pb_rank.apply(lambda x: x > round(stock_num_pb * 0.7))].mean(axis=1) - \
                        stock_pct_chg[pb_rank.apply(lambda x: x <= round(stock_num_pb * 0.3))].mean(axis=1)
        ff = np.vstack([np.array(index_pct_chg[-20:]['pct_chg']['000300.SH']), np.array(SMB[-20:]),
                        np.array(HML[-20:]), np.ones(len(index_pct_chg[-20:]))])
        reg_result = np.linalg.inv(ff.dot(ff.T)).dot(ff).dot(np.array(stock_pct_chg[-20:]))
        stock_res = stock_pct_chg[-20:] - ff.T.dot(reg_result)
        sse = np.square(stock_res).sum(axis=0)
        sst = np.square(stock_pct_chg[-20:].sub(stock_pct_chg[-20:].mean(axis=0), axis=1)).sum()
        ans = sse / sst
        return -ans

    # 针对播放后的结果，进行相关的rolling等操作。所用的前序数据长度应为reform_window。默认不修改temp_result， 可不重写。
    # def reform(self, temp_result):
    #     return temp_result.rolling(self.reform_window).mean()
