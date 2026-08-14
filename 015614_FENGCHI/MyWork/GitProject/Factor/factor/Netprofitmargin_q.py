from xfactor.BaseFactor import BaseFactor
import numpy as np
import xfactor.Util as ut


class Netprofitmargin_q(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.FDD_CHINA_STOCK_QUARTERLY_WIND.qfa_netprofitmargin"]
    financial_lag = 400
    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    reform_window = 1

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        Quarterly_data = database.depend_data['FactorData.FDD_CHINA_STOCK_QUARTERLY_WIND.qfa_netprofitmargin']
        # print(1)
        temp_data = Quarterly_data['qfa_netprofitmargin'].unstack()
        temp_data = temp_data.fillna(method='ffill')
        return temp_data.iloc[-1]

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean()