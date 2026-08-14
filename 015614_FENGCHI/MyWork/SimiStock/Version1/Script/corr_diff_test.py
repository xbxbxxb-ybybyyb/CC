# coding: utf-8
# Author：fengchi863
# Date ：2022/3/28 10:44

from SimiStockGenerator.SimiMethodBase.SimiMethodBase import SimiMethodBase
from SimiStock.dataApi import getData, tradeDate
from SimiStock.SimiStockGenerator.util import util
from SimiStock.config.path_config import *
import numpy as np
import pandas as pd
from itertools import product
from tqdm import tqdm


class SimiMethodTrend2(SimiMethodBase):
    def __init__(self, start_date=20180101, end_date=20211231, concept='SW1', pre_days_num=252):
        super().__init__(start_date, end_date, concept=concept)
        pctchg = getData.get_daily_1factor('pct_chg', date_list=self.shift_date_list)

        self.method_name = '日频pctchg相关性'
        self.pctchg = pctchg
        self.pre_days_num = pre_days_num

    def simi_strategy(self, stk_id, trade_date, concept_list):
        res_dict = dict()

        start_date = tradeDate.get_pre_trade_date(trade_date, self.pre_days_num)
        end_date = tradeDate.get_pre_trade_date(trade_date, 1)
        date_list = tradeDate.get_date_range(start_date, end_date)

        close = self.pctchg[stk_id][date_list].values

        ascend_flag = False
        for stk_id in concept_list:
            compare = self.pctchg[stk_id][date_list].values
            if np.isfinite(compare).sum() == 0:
                continue
            corr, ascend_flag = self.corr(close, compare, method='日频pctchg皮尔逊相关性')
            res_dict[stk_id] = corr
        corr = pd.Series(res_dict)
        corr = corr.sort_values(ascending=ascend_flag).dropna()
        # return corr.index.tolist(), [np.nan] * len(corr)
        return corr.index.tolist(), [1] * len(corr), corr.values.tolist()

    @staticmethod
    def corr(arr1, arr2, method=None):
        if method == '日频pctchg皮尔逊相关性':
            return np.corrcoef(arr1, arr2)[0, 1], False
        elif method == '日频pctchg欧式相关性':
            return np.linalg.norm(arr1 - arr2, ord=2), True
        elif method == '日频pctchg曼哈顿相关性':
            return np.linalg.norm(arr1 - arr2, ord=1), True
        elif method == '日频pctchg生物距离':
            up = np.sum(np.abs(arr1 - arr2))
            down = np.sum(arr1) + np.sum(arr2)
            down = 1e-5 if down == 0 else down
            return up / down

    def corr_calc(self):
        pbar = tqdm(range(len(self.block_data)))
        res_list = list()
        for idx in pbar:
            row = self.block_data.iloc[idx]
            stk_id = row['股票代码']
            trade_date = row['交易日期']
            pbar.set_description('串行生成中|%s|%s' % (int(stk_id), int(trade_date)))

            # 计算相关性
            start_date = tradeDate.get_pre_trade_date(trade_date, self.pre_days_num)
            end_date = tradeDate.get_pre_trade_date(trade_date, 1)
            date_list = tradeDate.get_date_range(start_date, end_date)
            pctchg = self.pctchg[stk_id][date_list].values
            concept_list = self.get_concept_list(stk_id, trade_date)
            for stk in concept_list:
                compare = self.pctchg[stk][date_list].values
                if np.isfinite(compare).sum() == 0:
                    continue
                corr = np.corrcoef(pctchg, compare)[0, 1]
                if corr >= 0.7:
                    tmp_list = [trade_date, stk_id, corr]
                    for N in [1, 2, 3, 4, 5]:
                        start_date2 = tradeDate.get_pre_trade_date(trade_date, self.pre_days_num + N)
                        end_date2 = tradeDate.get_pre_trade_date(trade_date, 1 + N)
                        date_list = tradeDate.get_date_range(start_date2, end_date2)
                        pctchg = self.pctchg[stk_id][date_list].values
                        compare = self.pctchg[stk][date_list].values
                        corr2 = np.corrcoef(pctchg, compare)[0, 1]
                        tmp_list.append(corr2)
                    res_list.append(tmp_list)
        df = pd.DataFrame(res_list)
        df.columns = ['stk_id', 'trade_date', 'corr', 'corr2', 'corr3', 'corr4', 'corr5', 'corr6']
        # df['diff'] = df['corr2'] - df['corr']
        # df['diff_sum'] = df['diff'].sum()
        # df['diff_abs_sum'] = df['diff'].map(abs).sum()
        # df['diff_mean'] = df['diff_sum'] / len(df)
        for N in [1, 2, 3, 4, 5]:
            df[f'diff_abs_mean{N}'] = (df[f'corr{N+1}'] - df['corr']).map(abs).sum() / len(df)
            df[f'diff_abs_std{N}'] = (df[f'corr{N+1}'] - df['corr']).map(abs).std()
            df[f'diff_abs_max{N}'] = (df[f'corr{N+1}'] - df['corr']).map(abs).max()
            df[f'diff_abs_min{N}'] = (df[f'corr{N + 1}'] - df['corr']).map(abs).min()
        return df


if __name__ == '__main__':
    param_dict = {'concept': ['SW1'],
                   'pre_days_num': [120]}
    param_list = list(product(param_dict['concept'], param_dict['pre_days_num']))
    for param in param_list:
        concept = param[0]
        pre_days_num = param[1]
        # smt1 = SimiMethodTrend2(start_date=20200620, end_date=20200631, concept=concept, pre_days_num=pre_days_num)
        smt1 = SimiMethodTrend2(start_date=20180101, end_date=20200631, concept=concept, pre_days_num=pre_days_num)
        result = smt1.corr_calc()
        save_name = '测试相关性稳定性_0.7_result.xlsx'
        util.save_df2xls(result, other_stats_path, save_name)
