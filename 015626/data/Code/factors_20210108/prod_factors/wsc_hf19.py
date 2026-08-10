from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *
# from help_functions_wsc import replace_zero


    
class wsc_hf19(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_hf19, self).__init__(required_columns=['PxStd_500', 'VolStd_500', 'amount_500'],
                                       lookback_bars=3000)

    def on_bar(self, hf_data):
        # 股票1分钟内价格波动和成交量波动的相关性，这个因子的逻辑暂时还想不清楚，只得到结论是价格和交易量不同时高波动时看涨
        # 引入amount时因为原因子表现不够强
        # rolling15分钟是因为原因子在持仓时间变长后迅速失效
        amount_500 = hf_data['amount_500']
        data1 = ts_mean(hf_data['PxStd_500'], 15).corrwith(ts_mean(hf_data['VolStd_500'], 15), axis=1)
        factor_raw = data1 * ts_mean(amount_500.sum(axis=1), 15)
        factor_mean = -ts_mean(factor_raw, 1)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= 0] = 0
        # factor[factor>=0] = 0
        return factor