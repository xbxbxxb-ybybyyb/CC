from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc1_cfg_ar_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc1_cfg_ar_if, self).__init__(required_columns=['close_hs300', 'close_spot_if', 'weight_boolean_hs300', 'amount_hs300'],
                                             lookback_bars=2000)

    def on_bar(self, data):
        # mask
        bool_mask = data['weight_boolean_hs300']
        amount_mask = data['amount_hs300'][bool_mask]
        amount_rank_mask = 2 * amount_mask.rank(axis=1, pct=True) - 1

        # 比较过去一段时间成分股和指数收益率大小，统计那一分钟涨幅小于指数的成分股平均交易额打分
        index_return = data['close_spot_if'].pct_change(periods=60, fill_method=None)
        stock_return = data['close_hs300'].pct_change(periods=60, fill_method=None)
        excess_return = (stock_return.subtract(index_return, axis=0))
        excess_return_weight = -amount_rank_mask[excess_return < 0].mean(axis=1)
        excess_return_weight = ts_mean(excess_return_weight, 15)
        factor = ts_rank(excess_return_weight, 600)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
