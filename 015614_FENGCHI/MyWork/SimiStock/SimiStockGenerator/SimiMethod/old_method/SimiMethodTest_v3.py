# coding: utf-8
# Author：fengchi863
# Date ：2022/4/14 15:25

"""
20220425：
对历史和未来的相关性计算相关性以及秩相关性
"""

from itertools import product

import numpy as np
import pandas as pd

from SimiStock.DataPrepare.BarraFactor import BarraFactor
from SimiStock.SimiStockGenerator.util import util
from SimiStock.config.path_config import *
from SimiStock.dataApi import getData
from SimiStock.dataApi import tradeDate
from SimiStockGenerator.SimiMethodBase.SimiMethodRollingBase import SimiMethodRollingBase

np.random.seed(2022)

"""皮尔逊相似度、规模、波动、动量、质量"""
weight_dict = {'v0': [1, 0, 0],
               'v1': [0.6, 0.4, 0],
               'v2': [0.8, 0.2, 0],
               'v3': [0.6, 0.2, 0.2]}
bf = BarraFactor()


class SimiMethodTest(SimiMethodRollingBase):
    def __init__(self, start_date=20180101, end_date=20211231,
                 method_name=None, concept='SW1', hedge_max_num=12,
                 corr_threshold=(0.6, 1), base_corr=(0.8, 1),
                 history_future_len=(120, 5), pre_calc_days_num=2,
                 weight_kind='v3', discount=95, corr_rolling_nums=10,
                 corr_max_diff=0.1, corr_max_diff2=0.1,
                 real_time=False, top_n=5):
        super().__init__(start_date, end_date, concept=concept, discount=discount,
                         history_future_len=history_future_len, pre_calc_days_num=pre_calc_days_num)
        pctchg = getData.get_daily_1factor('pct_chg', date_list=self.shift_date_list)
        date_list = np.load(barra_path2 + 'date_list.npy')
        code_list = np.load(barra_path2 + 'code_list.npy')

        self.pctchg = pctchg
        self.barra_date_list = list(date_list)
        self.barra_code_list = list(code_list)

        self.method_name = method_name
        self.concept = concept
        self.hedge_max_num = hedge_max_num
        self.corr_threshold = corr_threshold
        self.corr_rolling_nums = corr_rolling_nums
        self.base_corr = base_corr
        self.weight_kind = weight_kind
        self.corr_max_diff = corr_max_diff
        self.corr_max_diff2 = corr_max_diff2
        self.real_time = real_time
        self.top_n = top_n

        if real_time:
            self.block_data = pd.read_pickle(data_path + 'recent_block_data.pkl')

    @staticmethod
    def arr_min_max_transfer(arr: np.array):
        tmp_arr = arr.copy()
        min_arr = np.nanmin(tmp_arr)
        max_arr = np.nanmax(tmp_arr)
        tmp_arr = (tmp_arr - min_arr) / (max_arr - min_arr)
        return tmp_arr

    def judge_corr_stability(self, stk_id, start_date, end_date, concept_list, pre_times=10):
        """这里考虑后期每间隔一天进行一次统计"""
        corr_res = pd.DataFrame(index=concept_list)
        for idx in range(pre_times):
            _start_date = tradeDate.get_pre_trade_date(start_date, idx)
            _end_date = tradeDate.get_pre_trade_date(end_date, idx)
            stk_pctchg = self.pctchg.loc[_start_date:_end_date][stk_id]
            other_pctchg = self.pctchg.loc[_start_date:_end_date][concept_list]
            corr = pd.DataFrame(other_pctchg).corrwith(stk_pctchg).reindex(index=concept_list)
            corr_res = pd.concat([corr_res, corr], axis=1, ignore_index=True)
        corr_stats = pd.DataFrame(index=concept_list)
        corr_stats['大于基础阈值次数'] = (corr_res >= self.base_corr[0]).sum(axis=1)
        corr_stats['_mean'] = corr_res.mean(axis=1)
        corr_stats['_max'] = corr_res.max(axis=1)
        corr_stats['_min'] = corr_res.min(axis=1)
        corr_stats['max_diff'] = corr_stats['_max'] - corr_stats['_min']
        return corr_res, corr_stats

    def trans_param2filename(self, _param, exclude: list):
        _param = _param + [self.start_date, self.end_date]
        tmp_param = list()
        for idx, value in enumerate(_param):
            if idx not in exclude:
                tmp_param.append(str(value))
        filename_ = '_'.join(tmp_param)
        return filename_

    def simi_strategy(self, stk_id, date_tuple_list):
        hedge_list = list()
        for date_tuple in date_tuple_list:
            calc_date, start_date, end_date, train_start_date, train_end_date = date_tuple
            concept_list = self.get_concept_list(stk_id, calc_date)
            _, corr_stats = self.judge_corr_stability(stk_id, train_start_date, train_end_date, concept_list,
                                                      pre_times=self.corr_rolling_nums)
            stk_list = corr_stats['_mean'].sort_values(ascending=False).index.tolist()[:self.top_n]
            history_corr = pd.DataFrame(corr_stats['_mean'][stk_list], index=stk_list)
            _, future_corr_stats = self.judge_corr_stability(stk_id, start_date, end_date,
                                                             concept_list, pre_times=self.corr_rolling_nums)
            future_corr = pd.DataFrame(future_corr_stats['_mean'][stk_list], index=stk_list)

            corr = history_corr.corrwith(future_corr)
            rank_corr = history_corr.rank().corrwith(future_corr.rank())
            append_dict = {'calc_date': calc_date,
                           'start_date': start_date,
                           'end_date': end_date,
                           'hedge_list': stk_list,
                           'hedge_value': [self.top_n, corr[0], rank_corr[0]]}
            hedge_list.append(append_dict)
        return hedge_list


if __name__ == '__main__':
    param_dict = {'method_name': ['新版本'],
                  'concept': ['SW1'],
                  'hedge_max_num': [1],
                  'corr_threshold': [(-1, 1)],
                  'base_corr': [(-1, 1)],
                  'history_future_len': [(120, 120)],   # 5、历史的训练长度和未来的预测长度
                  'pre_calc_days_num': [2],
                  'weight_kind': ['v3'],
                  'discount': [95],
                  'corr_rolling_nums': [10],
                  'corr_max_diff': [0.1],   # 10、滚动时用的阈值判断参数
                  'corr_max_diff2': [0.1],   # 断层时用的阈值判断参数
                  'real_time': [False],   # 为True时要把start_date和end_date换掉
                  'top_n': [5]  # 筛选均值最高的前几名
                  }
    param_list = list(product(*[param_dict[key] for key in param_dict.keys()]))
    for param in param_list:
        param = list(param)
        # start_date_ = 20170101
        # end_date_ = 20201231
        start_date_ = 20210101
        end_date_ = 20210930
        # start_date_ = 20220421
        # end_date_ = 20220421
        now_param_dict = dict(zip(param_dict.keys(), param))

        """设置real_time，为True时"""
        smt1 = SimiMethodTest(start_date=start_date_, end_date=end_date_, **now_param_dict)
        filename = smt1.trans_param2filename(param, exclude=[1, 6, 7, 9, 10, 11, 12])

        result = smt1.get_hedge_list(mode='multi', kernal_num=24)
        # result = smt1.get_hedge_list(mode='serial', kernal_num=24)
        # result = smt1.get_simi_stock(600711, 20200102)

        save_name = f'{filename}_corrResultV3.pkl'
        util.save_list2pkl(result, hedge_path, save_name)
