from factor_generator import FactorGenerator
from operators_wsc import *
from help_functions_wsc import multi_processing_joblib



class wsc_gp3_spot_if(FactorGenerator):
    def __init__(self):
        super().__init__(required_columns=['low_spot_if'], lookback_bars=2000)

    def on_bar(self, data_dict):
        # gp搜索因子，搜索时间段：20170101-20181231，验证时间段：20190101-20190630
        # low的收益率作差后取中位数，收益率涨幅越大因子值越大，属于动量因子。
        index_low = data_dict['low_spot_if']
        factor_raw = ts_median(ts_delta(ts_pct_change(index_low, 120), 115), 25)
        factor = ts_rank(factor_raw, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor