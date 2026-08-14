from backtest.factor_backtest.StrategyFactorTest2 import StrategyFactorTest2, search_index
from dataApi.tradeDate import *
from dataApi.getData import *
from dataApi.stockList import *
import pandas as pd
import numpy as np
import pickle
from tqdm import tqdm


class FactorTest(object):

    def __init__(self, start_date=20140101, backtest_start_date=20140701, end_date=20191231,
                 stock_pool_address='/data/group/800442/800319/LimitUpStrategy/FilteredTick.pkl'):

        date_list = get_date_range(start_date, end_date)
        backtest_date_list = get_date_range(backtest_start_date, end_date)

        start_date = date_list[0]
        end_date = date_list[-1]
        backtest_start_date = backtest_date_list[0]

        stock_pool = pd.read_pickle(stock_pool_address)
        stock_pool.query('date >= @start_date & date <= @end_date', inplace=True)

        self.date_list = date_list
        self.backtest_date_list = backtest_date_list
        self.start_date = start_date
        self.end_date = end_date
        self.backtest_start_date = backtest_start_date
        self.stock_pool = stock_pool
        self.stock_pool_address = stock_pool_address

    def factor_std(self, factor_s, n=60):

        factor_s = factor_s.loc[self.stock_pool.set_index(['date', 'code', 'tick']).index]
        factor_s.index = self.stock_pool.set_index(['date', 'code', 'tick']).index
        factor_s.name = 'value'
        factor_s = factor_s.loc[(factor_s.index.get_level_values('date') >= self.start_date) &
                                (factor_s.index.get_level_values('date') <= self.end_date)]

        null_pct = factor_s.isnull().sum() / len(factor_s)
        inf_pct = (np.isinf(factor_s)).sum() / len(factor_s)
        zero_pct = (factor_s == 0).sum() / len(factor_s)

        factor_s = factor_s.fillna(0)

        num = factor_s.groupby('date').count()
        f1 = factor_s.groupby('date').sum().fillna(0)
        f2 = (factor_s ** 2).groupby('date').sum().fillna(0)

        factor_mean = f1.rolling(n).sum() / num.rolling(n).sum()
        factor_mean.name = 'mean'
        factor_std = np.sqrt(
            (f2.rolling(n).sum() - (num.rolling(n).sum()) * (factor_mean ** 2)) / (num.rolling(n).sum() - 1))
        factor_std.name = 'std'

        factor_mean_tick = pd.merge(factor_s.reset_index(), factor_mean.shift(1).reset_index(), how='left',
                                    on='date')[['date', 'code', 'tick', 'mean']].set_index(['date', 'code', 'tick'])
        factor_std_tick = pd.merge(factor_s.reset_index(), factor_std.shift(1).reset_index(), how='left',
                                   on='date')[['date', 'code', 'tick', 'std']].set_index(['date', 'code', 'tick'])

        factor_std = (factor_s - factor_mean_tick['mean']) / factor_std_tick['std']
        factor_std = factor_std.loc[(factor_std.index.get_level_values('date') >= self.backtest_start_date) &
                                    (factor_std.index.get_level_values('date') <= self.end_date)]

        return factor_std

    def factor_test(self, factor,expression,n=10):

        factor_raw = pd.read_pickle('/data/group/800442/800319/ZTfactors/Untested/%s.pkl' % factor)
        #factor_raw = pd.read_pickle('/data/group/800442/800319/ZTfactors/Approved/%s.pkl' % factor)['factor_value']
        factor_s = factor_raw.loc[(factor_raw.index.get_level_values('date') >= self.backtest_start_date) &
                                  (factor_raw.index.get_level_values('date') <= self.end_date)]
        null_pct = factor_s.isnull().sum() / len(factor_s)
        inf_pct = (np.isinf(factor_s)).sum() / len(factor_s)
        zero_pct = (factor_s == 0).sum() / len(factor_s)

        factor_std = self.factor_std(factor_raw)

        if null_pct > 0.2 or inf_pct > 0.2 or zero_pct > 0.4 or null_pct + inf_pct + zero_pct > 0.5:
            print('缺失值/无穷值/0值占比太高')

        else:
            sft = StrategyFactorTest2(start_date=self.backtest_start_date, end_date=self.end_date)
            sft.set_stock_pool(start_tick=93000, stock_pool_address=self.stock_pool_address)
            sft.set_test_params(strength_limit=1., close_limit_up=True)
            try:

                ft = sft.test_factor(factor=factor_std,  # 因子名称, 可以传入str文件名, 也可直接传入DataFrame
                                     address=None,  # 因子路径, 若直接传DataFrame, 此处需为None
                                     groups=10,  # 连续型因子分组收益的分组数, 若因子值为离散值则此传参无意义
                                     output=None  # 回测结果输出路径, None表示不输出
                                     )

                corr = ft[0]
                ret = ft[1]
                tail_amt = ft[2]
                head_amt = ft[3]

                corr_tmr30 = corr['ret_tmr30']
                ret_tmr30 = pd.DataFrame(ret.loc[ret.index, (slice(None), 'ret_tmr30')].values,
                                         index=ret.index,
                                         columns=ret.loc[ret.index, (slice(None), 'ret_tmr30')].columns.levels[0])
                head_ret_tmr30 = ret_tmr30.apply(lambda x: x.tolist()[-2] if x.tolist()[-1] > 0 else x.tolist()[0],
                                                 axis=0)

                if abs(corr_tmr30.loc['ALL']) >= 0.01 and (abs(corr_tmr30) >= 0.01).sum() >= 6:
                    print('IC test pass!')
                else:
                    print('IC test failed.')

                if head_ret_tmr30.loc['ALL'] > 0 or (
                        ((head_ret_tmr30 > 0).sum() >= 3) and ((head_ret_tmr30[4:] > 0).sum() > 0)):
                    print('Ret test pass!')
                else:
                    print('Ret test failed.')

                if abs(corr_tmr30.loc['ALL']) >= 0.01 and (abs(corr_tmr30) >= 0.01).sum() >= 6 and (
                        head_ret_tmr30.loc['ALL'] > 0 or (
                        ((head_ret_tmr30 > 0).sum() >= 3) and ((head_ret_tmr30[4:] > 0).sum() > 0))):

                    if len(os.listdir('/data/group/800442/800319/ZTfactors/Approved/')) == 0:

                        factor_dict = {'factor_name': factor, 'factor_value': factor_raw,
                                       'head_ret_tmr30': head_ret_tmr30, 'ret_tmr30': ret_tmr30,
                                       'corr_tmr30': corr_tmr30, 'tail_amt': tail_amt, 'head_amt': head_amt,
                                       'null_pct': null_pct, 'inf_pct': inf_pct, 'zero_pct': zero_pct}
                        print('Congratulations! Factor approved!')
                        with open('/data/group/800442/800319/ZTfactors/Approved/%s.pkl' % factor, 'wb') as f:
                            pickle.dump(factor_dict, f)

                    else:

                        factor_value = []
                        factor_list = []
                        factor_ret = []
                        factor_value.append(factor_raw)
                        factor_list.append(factor)
                        factor_ret.append(head_ret_tmr30.loc['ALL'])

                        for name in os.listdir('/data/group/800442/800319/ZTfactors/Approved/'):
                            with open('/data/group/800442/800319/ZTfactors/Approved/%s' % name, 'rb') as f:
                                candidate = pickle.load(f)
                                factor_value.append(candidate['factor_value'])
                                factor_list.append(candidate['factor_name'])
                                factor_ret.append(candidate['head_ret_tmr30'].loc['ALL'])

                        candidate_factor = np.asanyarray(factor_value)
                        candidate_factor = candidate_factor[:, 20000:]
                        candidate_factor[~np.isfinite(candidate_factor)] = 0
                        candidate_corr = np.corrcoef(candidate_factor)

                        factor_result = pd.DataFrame({'factor': factor_list, 'all_ret': factor_ret}).set_index('factor')
                        corr_df = pd.DataFrame(candidate_corr, index=factor_list, columns=factor_list)
                        corr_factor = corr_df.loc[corr_df.index != factor, factor]
                        ret_factor = factor_result.loc[corr_factor.loc[abs(corr_factor) > 0.8].index]

                        if len(ret_factor) == 0 or factor_result.loc[factor, 'all_ret'] > ret_factor['all_ret'].max():
                            print('Corr test pass!')
                            factor_dict = {'factor_name': factor, 'factor_value': factor_raw,
                                           'head_ret_tmr30': head_ret_tmr30, 'ret_tmr30': ret_tmr30,
                                           'corr_tmr30': corr_tmr30, 'tail_amt': tail_amt, 'head_amt': head_amt,
                                           'null_pct': null_pct, 'inf_pct': inf_pct, 'zero_pct': zero_pct,'expression':expression}
                            print('Congratulations! Factor approved!')
                            if n%10==0:
                                with open('/data/group/800442/800319/ZTfactors/Approved/%s.pkl' % factor, 'wb') as f:
                                    pickle.dump(factor_dict, f)
                                for f in ret_factor.index:
                                    os.remove('/data/group/800442/800319/ZTfactors/Approved/%s.pkl' % f)
                                return True
                            else:
                                if (n%10==1) or (n%10==2):
                                    with open('/data/group/800442/800319/zxf/xq/%s.pkl' % factor, 'wb') as f:
                                        pickle.dump(factor_dict, f)
                                elif (n%10==3) or (n%10==4):
                                    with open('/data/group/800442/800319/zxf/tx/%s.pkl' % factor, 'wb') as f:
                                        pickle.dump(factor_dict, f)
                                else:
                                    with open('/data/group/800442/800319/zxf/ZTuntestedfactors/%s.pkl' % factor, 'wb') as f:
                                        pickle.dump(factor_dict, f)
                                return True
                        else:
                            print('Corr test failed.')

            except:
                pass


if __name__ == '__main__':
    self = FactorTest(start_date=20140101,
                      backtest_start_date=20140701, end_date=20191231,
                      stock_pool_address='/data/group/800442/800319/LimitUpStrategy/FilteredTick.pkl')

    for factor in ['t_tender_pct_mean', 't_tender_pct_std', 't_tender_max_up',
                   't_tender_max_down', 't_tender_bid', 't_tender_ask','t_tender_bidmask']:
        print('——————————————————')
        print(factor)
        self.factor_test(factor)
