from factor_generator import FactorGenerator
from operators_wsc import *



class wsc_ti16(FactorGenerator):
    def __init__(self):
        super(wsc_ti16, self).__init__(required_columns=['high', 'low', 'amount', 'recent_month_mask'],
                                       lookback_bars=2000)

    def on_bar(self, data_dict):
        # 大阳线技术指标，当开盘价接近最低价，收盘价显著高于开盘价且接近最高价时出现该图形。指标范围: [0,1]，且指标越高未来上涨概率越大，因此若close<open，则将指标值置为0.
        future_high = data_dict['high']
        future_low = data_dict['low']
        future_amount = data_dict['amount']
        future_mask = data_dict['recent_month_mask']
        price1 = (future_high + future_low) / 2
        mm = ts_delta(price1, 1)
        price2 = future_high - future_low
        price2 = replace_zero(price2)
        cabinet_ratio = future_amount / price2
        cabinet_ratio = replace_zero(cabinet_ratio)
        emv = mm / cabinet_ratio
        factor_raw = emv[future_mask].sum(axis=1)
        factor_mean = ts_mean(ratio1, 120)
        factor = ts_rank(factor_mean, 600)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor