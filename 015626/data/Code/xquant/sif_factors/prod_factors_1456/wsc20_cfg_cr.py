from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc20_cfg_cr(FactorGeneratorComplex):
    def __init__(self):
        super(wsc20_cfg_cr, self).__init__(required_columns=['close_zz500', 'close_spot', 'stk_index_corr_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data):
        # mask
        corr_mask = data['stk_index_corr_zz500']
        corr_rank_mask = 2 * corr_mask.rank(axis=1, pct=True) - 1

        # 比较过去一段时间成分股和指数收益率大小，统计那一分钟涨幅小于指数的成分股平均波动率打分
        index_return = data['close_spot'].pct_change(periods=45, fill_method=None)
        stock_return = data['close_zz500'].pct_change(periods=45, fill_method=None)
        excess_return = stock_return.subtract(index_return, axis=0)
        excess_return_weight = corr_rank_mask[excess_return < 0].sum(axis=1)
        excess_return_weight = -ts_mean(excess_return_weight, 25)
        factor = ts_rank(excess_return_weight, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<0] = 0
        #factor[factor>=0.5] = 0
        return factor
