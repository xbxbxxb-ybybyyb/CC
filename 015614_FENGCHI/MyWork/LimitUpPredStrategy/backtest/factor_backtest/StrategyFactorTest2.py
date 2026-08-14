from dataApi.tradeDate import get_date_range
from dataApi.stockList import trans_windcode2int
import pandas as pd
import numpy as np

def search_index(x, y):

    index = np.argsort(x)
    sorted_x = x[index]
    sorted_index = np.searchsorted(sorted_x, y)
    y_index = np.take(index, sorted_index, mode="clip")
    mask = x[y_index] != y
    result = np.ma.array(y_index, mask=mask, fill_value=0)
    return result

class StrategyFactorTest2(object):

    def __init__(self, start_date=20140101, end_date=20191231,
                 back_data_address='/data/group/800442/800319/LimitTickData/HighFreqData/LimitUpPredPoolWhole.pkl'):

        date_list = get_date_range(start_date, end_date)
        start_date = date_list[0]
        end_date = date_list[-1]
        back_data = pd.read_pickle(back_data_address)
        back_data.query('date >= @start_date & date <= @end_date', inplace=True)
        half_years = back_data['half_year'].drop_duplicates().to_list()

        self.date_list = date_list
        self.start_date = start_date
        self.end_date = end_date
        self.__back_data = back_data
        self.back_data = back_data
        self.half_years = half_years

    def set_stock_pool(self, start_tick=91503, stock_pool_address=None):

        if start_tick > 91503:
            self.back_data = self.__back_data.query('tick >= @start_tick')
        else:
            self.back_data = self.__back_data
        if stock_pool_address:
            stock_pool = pd.read_pickle(stock_pool_address)
            cols = [x for x in stock_pool.columns if x not in ['date', 'code', 'tick']]
            stock_pool[cols] = stock_pool[cols] > 0
            if ('date' in stock_pool.columns) & ('code' in stock_pool.columns) & ('tick' in stock_pool.columns):
                stock_pool = pd.MultiIndex.from_frame(stock_pool[['date', 'code', 'tick']]).values
                index = pd.MultiIndex.from_frame(self.back_data[['date', 'code', 'tick']]).values
                row = search_index(stock_pool, index)
                self.back_data = self.back_data[~ row.mask]

            elif ('date' in stock_pool.columns) & ('code' in stock_pool.columns):
                stock_pool = pd.MultiIndex.from_frame(stock_pool[['date', 'code']]).values
                index = pd.MultiIndex.from_frame(self.back_data[['date', 'code']]).values
                row = search_index(stock_pool, index)
                self.back_data = self.back_data[~ row.mask]

            elif 'date' in stock_pool.columns:
                stock_pool = stock_pool['date'].values
                index = self.back_data['date'].values
                row = search_index(stock_pool, index)
                self.back_data = self.back_data[~ row.mask]
            else:
                raise ValueError("date must be in stock_pool.columns")

    def set_test_params(self, strength_limit=1., close_limit_up=True):

        if close_limit_up:
            self.back_data['strength_if'] = (self.back_data['strength'] >= strength_limit) \
                                            & self.back_data['close_limit_up']
        else:
            self.back_data['strength_if'] = self.back_data['strength'] >= strength_limit
        self.strength_limit = strength_limit

    def preprocess_factor(self, factor, address=None):

        if address and isinstance(factor, str):
            factor = pd.read_pickle('%s/%s.pkl' % (address, factor))

        if isinstance(factor, pd.Series):
            row = search_index(factor.index.values,
                               pd.MultiIndex.from_frame(self.back_data[['date', 'code', 'tick']]).values)
            factor = factor.values[row]
            factor[row.mask] = np.nan
            factor = pd.Series(factor, self.back_data.index, name='factor')
        elif len(factor.columns) == 4:
            factor = factor.set_index(['date', 'code', 'tick']).iloc[:, 0]
            row = search_index(factor.index.values,
                               pd.MultiIndex.from_frame(self.back_data[['date', 'code', 'tick']]).values)
            factor = factor.values[row]
            factor[row.mask] = np.nan
            factor = pd.Series(factor, self.back_data.index, name='factor')
        else:
            factor.columns = factor.columns.map(trans_windcode2int)
            factor.columns.name = 'tick'
            factor.index.names = ['date', 'code']

            row = search_index(factor.index.values,
                               pd.MultiIndex.from_frame(self.back_data[['date', 'code']]).values)
            col = search_index(factor.columns.values, self.back_data['tick'].values)

            factor = factor.values[row, col]
            factor[row.mask | col.mask] = np.nan
            factor = pd.Series(factor, self.back_data.index, name='factor')

        kinds = factor.values[np.isfinite(factor.values)]
        if np.unique(kinds[:min(kinds.shape[0], 1000)]).shape[0] > 10:
            factor_type = 'reg'
        else:
            kinds = np.unique(kinds).shape[0]
            if kinds > 10:
                factor_type = 'reg'
            else:
                factor_type = 'cls'

        if factor_type == 'reg':
            factor0 = ((factor - factor.mean()) / factor.std()).fillna(0)
            factor1 = pd.Series(factor.values, index=self.back_data['half_year']).groupby('half_year').apply(
                lambda x: ((x - x.mean()) / x.std()).fillna(0))
            factor1.index = factor0.index
        else:
            fill = np.floor((kinds + 1) / 2)
            factor0 = factor.rank(method='dense').fillna(fill).map(int) - 1
            factor1 = factor0.copy()
        factor0.name = 'factor'
        factor1.name = 'factor'
        return factor0, factor1, factor_type

    @staticmethod
    def calc_corr(factor, back_data):

        corr = back_data[['strength_if', 'strength', 'ret_tmr0', 'ret_tmr5',
                          'ret_tmr10', 'ret_tmr20', 'ret_tmr30']].corrwith(factor)
        corr.index.name = 'corr'
        return corr

    @staticmethod
    def calc_group_ret(factor, back_data, groups=10, factor_type='reg'):

        if factor_type == 'reg':
            factor = np.ceil(factor.rank(pct=True) * groups) - 1

        group_ret = pd.concat([factor, back_data[['strength_if', 'strength', 'ret_tmr0', 'ret_tmr5',
                          'ret_tmr10', 'ret_tmr20', 'ret_tmr30']]], axis=1)
        group_ret = group_ret.groupby('factor').mean()
        group_ret.index = group_ret.index.map(int)
        group_ret.index.name = 'group'
        max_group = group_ret.index[-1]
        group_ret.loc['monotone'] = group_ret.corrwith(pd.Series(group_ret.index, group_ret.index))
        tail_amt = back_data['buyable_amt'][factor == max_group].describe(percentiles=np.arange(0.05, 1, 0.05))
        tail_amt.index = tail_amt.index.map(lambda x: x.replace('.0', ''))
        head_amt = back_data['buyable_amt'][factor == 0].describe(percentiles=np.arange(0.05, 1, 0.05))
        head_amt.index = tail_amt.index.map(lambda x: x.replace('.0', ''))

        return group_ret, tail_amt, head_amt

    def test_factor(self, factor, address=None, groups=10, output=None):

        factor0, factor1, factor_type = self.preprocess_factor(factor, address)

        corr = {}
        ret = {}
        tail_amt = {}
        head_amt = {}
        corr['ALL'] = self.calc_corr(factor0, self.back_data)
        _group_ret, _tail_amt, _head_amt = self.calc_group_ret(factor0, self.back_data, groups, factor_type)
        ret['ALL'] = _group_ret
        tail_amt['ALL'] = _tail_amt
        head_amt['ALL'] = _head_amt

        for hf in self.half_years:
            _back_data = self.back_data.query('half_year == @hf')
            _factor1 = factor1.loc[_back_data.index]
            corr[hf] = self.calc_corr(_factor1, _back_data)
            _group_ret, _tail_amt, _head_amt = self.calc_group_ret(_factor1, _back_data, groups, factor_type)
            ret[hf] = _group_ret
            tail_amt[hf] = _tail_amt
            head_amt[hf] = _head_amt

        corr = pd.DataFrame(corr).T
        ret  = pd.concat([ret[x] for x in ret], axis=1, keys=list(ret.keys()))
        tail_amt  = pd.concat([tail_amt[x] for x in tail_amt], axis=1, keys=list(tail_amt.keys()))
        head_amt  = pd.concat([head_amt[x] for x in head_amt], axis=1, keys=list(head_amt.keys()))

        if output:
            with pd.ExcelWriter(output) as w:
                corr.to_excel(w, 'corr')
                ret.to_excel(w, 'group_ret')
                tail_amt.to_excel(w, 'tail_amt')
                head_amt.to_excel(w, 'head_amt')
        return corr, ret, tail_amt, head_amt


if __name__ == '__main__':

    self = StrategyFactorTest2(start_date=20140101, end_date=20191231)


    # self.set_stock_pool(start_tick=94000, stock_pool_address='/data/group/800442/800319/自定义股票池.pkl')
    self.set_stock_pool(start_tick=94000, stock_pool_address='/data/group/800442/800319/LimitUpStrategy/NoSTPool.pkl')

    '''
    start_tick为开始回测的tick, 默认为开盘91503
    stock_pool_address传入一个DataFrame的pkl文件地址, DataFrame格式支持三种:
    (1)日期池：columns=['date':int]
    (2)日间池: columns=['date':int, 'code':int]
    (3)日内池: columns=['date':int, 'code':int, 'tick':int]
    修改股票池后建议保存类属性back_data到pkl文件中，便于下次直接在类初始化时传入
    '''

    self.set_test_params(strength_limit=1., close_limit_up=True) # 封板定义为第一次涨停后, 收盘前nTick有mTick涨停, 比值m/n, 且收盘涨停

    # 以上条件不变时，因子回测可多次连续进行
    result = self.test_factor(factor='tx_TickRet4_diff', # 因子名称, 可以传入str文件名, 也可直接传入DataFrame
                     address='/data/group/800442/800319/ZTfactors/', # 因子路径, 若直接传DataFrame, 此处需为None
                     groups=10, # 连续型因子分组收益的分组数, 若因子值为离散值则此传参无意义
                     output='/data/group/800442/800319/回测结果tx_TickRet4_diff.xlsx' # 回测结果输出路径, None表示不输出
                     )
