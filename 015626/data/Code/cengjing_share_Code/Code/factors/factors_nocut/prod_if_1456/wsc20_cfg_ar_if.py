from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc20_cfg_ar_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc20_cfg_ar_if, self).__init__(required_columns=['close_hs300', 'amount_hs300', 'weight_boolean_hs300'],
                                            lookback_bars=4000)

    def on_bar(self, data):
        # mask
        stk_amount = data['amount_hs300']
        bool_mask = data['weight_boolean_hs300']
        amount_mask = stk_amount[bool_mask]
        amount_rank_mask = 2 * amount_mask.rank(axis=1, pct=True) - 1

        # 长江金工高频因子八，偏度因子
        # 计算close的偏度，偏度＞0时，大于价格均值的价格比小于价格均值的价格少，个股成交集中在价格相对较低的水平，反之亦然，因此认为偏度越小的股票未来价格更可能上升。
        # 取当分钟rolling_skew前50%的股票，计算它们的过去一分钟return，作为因子值，再套相应的mask，因为每期选出的票都不一样，所以为了时序上可比，要做一定的归一化处理。
        stk_close = data['close_hs300']
        stk_ret = ts_pct_change(stk_close, 1)[bool_mask]
        stk_skew = ts_skew(stk_close, 30)[bool_mask]
        skew_long = stk_skew.gt(stk_skew.quantile(0.5, axis=1), axis=0)
        factor_init = stk_ret[skew_long]

        factor_raw = (factor_init * stk_amount).sum(axis=1) / (stk_amount * skew_long).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 55)
        factor = rolling_norm(factor_mean, 240*5)
        
        factor = factor.to_frame() 
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= 0] = 0
        #factor[factor>=0.5] = np.nan
        return factor