from dataApi.tradeDate import get_date_range
from dataApi.stockList import trans_windcode2int
import pandas as pd
import numpy as np

def search_index(x, y, dtype='i4,i4'):

    x = np.asanyarray(x, dtype=dtype)
    y = np.asanyarray(y, dtype=dtype)
    index = np.argsort(x)
    sorted_x = x[index]
    sorted_index = np.searchsorted(sorted_x, y)
    y_index = np.take(index, sorted_index, mode="clip")
    mask = x[y_index] != y
    result = np.ma.array(y_index, mask=mask, fill_value=0)
    return result

class StrategyFactorTest2(object):

    def __init__(self, start_date=20140101, end_date=20191231,
                 back_data_address='/data/group/800319/LimitTickData/HighFreqData/LimitUpPredPoolWhole.pkl'):

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
            stock_pool = pd.read_pickle(stock_pool_address) > 0
            if ('date' in stock_pool.columns) & ('code' in stock_pool.columns) & ('tick' in stock_pool.columns):
                stock_pool = pd.MultiIndex.from_frame(stock_pool[['date', 'code', 'tick']]).values
                index = pd.MultiIndex.from_frame(self.back_data[['date', 'code', 'tick']]).values
                row = search_index(stock_pool, index, dtype='i4,i4,i4')
                row = row.data[~ row.mask]
                self.back_data = self.back_data.iloc[row]

            elif ('date' in stock_pool.columns) & ('code' in stock_pool.columns):
                stock_pool = pd.MultiIndex.from_frame(stock_pool[['date', 'code']]).values
                index = pd.MultiIndex.from_frame(self.back_data[['date', 'code']]).values
                row = search_index(stock_pool, index, dtype='i4,i4')
                row = row.data[~ row.mask]
                self.back_data = self.back_data.iloc[row]

            elif 'date' in stock_pool.columns:
                stock_pool = stock_pool['date'].values
                index = self.back_data['date'].values
                row = search_index(stock_pool, index, dtype='i4')
                row = row.data[~ row.mask]
                self.back_data = self.back_data.iloc[row]
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
                               pd.MultiIndex.from_frame(self.back_data[['date', 'code', 'tick']]).values,
                               dtype='i4,i4,i4')
            factor = factor.values[row]
            factor[row.mask] = np.nan
            factor = pd.Series(factor, self.back_data.index, name='factor')
        elif len(factor.columns) == 4:
            factor = factor.set_index(['date', 'code', 'tick']).iloc[:, 0]
            row = search_index(factor.index.values,
                               pd.MultiIndex.from_frame(self.back_data[['date', 'code', 'tick']]).values,
                               dtype='i4,i4,i4')
            factor = factor.values[row]
            factor[row.mask] = np.nan
            factor = pd.Series(factor, self.back_data.index, name='factor')
        else:
            factor.columns = factor.columns.map(trans_windcode2int)
            factor.columns.name = 'tick'
            factor.index.names = ['date', 'code']

            row = search_index(factor.index.values,
                               pd.MultiIndex.from_frame(self.back_data[['date', 'code']]).values,
                               dtype='i4,i4')
            col = search_index(factor.columns.values, self.back_data['tick'].values, dtype='i4')

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
            fill = np.floor((len(kinds) + 1) / 2)
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
        group_ret.loc['monotone'] = group_ret.corrwith(pd.Series(group_ret.index, group_ret.index))
        return group_ret

    def test_factor(self, factor, address=None, groups=10, output=None):

        factor0, factor1, factor_type = self.preprocess_factor(factor, address)

        corr = {}
        ret = {}
        corr['ALL'] = self.calc_corr(factor0, self.back_data)
        ret['ALL'] = self.calc_group_ret(factor0, self.back_data, groups, factor_type)

        for hf in self.half_years:
            _back_data = self.back_data.query('half_year == @hf')
            _factor1 = factor1.loc[_back_data.index]
            corr[hf] = self.calc_corr(_factor1, _back_data)
            ret[hf] = self.calc_group_ret(_factor1, _back_data, groups, factor_type)
        corr = pd.DataFrame(corr).T
        ret  = pd.concat([ret[x] for x in ret], axis=1, keys=list(ret.keys()))

        if output:
            with pd.ExcelWriter(output) as w:
                corr.to_excel(w, 'corr')
                ret.to_excel(w, 'group')
        return corr, ret


if __name__ == '__main__':

    self = StrategyFactorTest2(start_date=20140101, end_date=20191231)

    self.set_stock_pool(start_tick=94000, stock_pool_address='/data/group/800319/自定义股票池.pkl')
    # self.set_stock_pool(start_tick=94000, stock_pool_address=None)

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
    self.test_factor(factor='test', # 因子名称, 可以传入str文件名, 也可直接传入DataFrame
                     address='/data/group/800319/', # 因子路径, 若直接传DataFrame, 此处需为None
                     groups=10, # 连续型因子分组收益的分组数, 若因子值为离散值则此传参无意义
                     output='/data/group/800319/回测结果.xlsx' # 回测结果输出路径, None表示不输出
                     )
