# coding: utf-8
# Author：fengchi863
# Date ：2022/6/1 9:35

"""
20220601：老版本测试，去除稳定性等因素
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


class SimiMethod1(SimiMethodRollingBase):
    def __init__(self, start_date=20180101, end_date=20211231,
                 method_name=None, concept='SW1', hedge_max_num=12,
                 corr_threshold=(0.6, 1), base_corr=(0.8, 1),
                 history_future_len=(120, 5), pre_calc_days_num=2,
                 weight_kind='v3', discount=95, corr_rolling_nums=10,
                 corr_max_diff=0.1, corr_max_diff2=0.1,
                 real_time=False):
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
            other_pctchg = self.pctchg.loc[_start_date:_end_date][concept_list].fillna(0)
            corr = pd.DataFrame(other_pctchg).corrwith(stk_pctchg).reindex(index=concept_list)
            corr_res = pd.concat([corr_res, corr], axis=1, ignore_index=True)
        corr_stats = pd.DataFrame(index=concept_list)
        corr_max = corr_res.max().max()
        corr_stats['最大值是否介于基础阈值'] = ((corr_max > self.base_corr[0]) & (corr_max <= self.base_corr[1]))
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
        corr_base_low, corr_base_high = self.base_corr[0], self.base_corr[1]
        corr_low, corr_high = self.corr_threshold[0], self.corr_threshold[1]
        first_flag = True  # 记录第几次进入循环
        last_hedge_corr_dict = dict()
        for date_tuple in date_tuple_list:
            calc_date, start_date, end_date, train_start_date, train_end_date = date_tuple
            concept_list = self.get_concept_list(stk_id, calc_date)
            weight_list = weight_dict[self.weight_kind]

            corr_res, corr_stats = self.judge_corr_stability(stk_id, train_start_date, train_end_date, concept_list,
                                                             pre_times=self.corr_rolling_nums)

            if first_flag:
                if corr_stats['最大值是否介于基础阈值'].iloc[0] == 0:  # 若不满足基本条件，返回空
                    return list()
            corr = corr_stats['_mean'].reindex(self.barra_code_list).values
            corr_copy = corr_stats['_mean'].reindex(index=concept_list).copy()
            s_corr = corr_copy.sort_values(ascending=False)
            remove_stk_list = corr_stats.query(f'max_diff > 0.1 & _min < {self.corr_threshold[0] - 0.1}').index.tolist()

            # %% 叠加风格部分
            lncap = bf.get_1factor('LNCAP', calc_date)
            lncap_diff = abs(lncap - lncap[self.barra_code_list.index(stk_id)])
            lncap_diff = self.arr_min_max_transfer(lncap_diff)
            dastd = bf.get_1factor('DASTD', calc_date)
            dastd_diff = abs(dastd - dastd[self.barra_code_list.index(stk_id)])
            dastd_diff = self.arr_min_max_transfer(dastd_diff)

            ret = corr * weight_list[0] - lncap_diff * weight_list[1] - dastd_diff * weight_list[2]
            ret_s = pd.Series(ret, index=self.barra_code_list)

            ret_s = ret_s[concept_list].sort_values(ascending=False)
            tmp_list1 = ret_s.index.tolist()

            # %% 隔断分层
            # corr_diff = s_corr.shift(1) - s_corr
            # manzu_list = corr_diff[corr_diff > self.corr_max_diff2].index.tolist()
            # if manzu_list:
            #     for manzu in manzu_list:
            #         if corr_low < s_corr[manzu] < 0.8:
            #             manzu_idx = s_corr.index.tolist().index(manzu)
            #             corr_low = s_corr.iloc[manzu_idx]

            tmp_list2 = s_corr[(s_corr > corr_low) & (s_corr <= corr_high)].index.tolist()
            tmp_list2 = list(set(tmp_list2).difference(set(remove_stk_list)))
            ret_list = [x for x in tmp_list1 for y in tmp_list2 if x == y]

            # 用hedge_max_num截断
            if len(ret_list) >= self.hedge_max_num:
                ret_list = ret_list[:self.hedge_max_num]
            # 如果第一次进入循环就生成空的对冲标的，那么这个样本直接丢掉
            if first_flag and len(ret_list) == 0:
                return list()

            append_dict = {'calc_date': calc_date,
                           'start_date': start_date,
                           'end_date': end_date,
                           'hedge_list': ret_list,
                           'hedge_value': list(s_corr[ret_list])}
            hedge_list.append(append_dict)

            first_flag = False

        return hedge_list


if __name__ == '__main__':
    param_dict = {'method_name': ['报告用新版本'],
                  'concept': ['SW1'],
                  'hedge_max_num': [14],
                  # 'corr_threshold': [(0.6, 0.8), (0.7, 0.8)],
                  # 'base_corr': [(0.7, 0.8)],
                  # 'corr_threshold': [(0.6, 1)],
                  # 'base_corr': [(0.7, 1)],
                  'corr_threshold': [(0.5, 1)],
                  'base_corr': [(0.5, 1)],
                  'history_future_len': [(120, 120)],   # 5、历史的训练长度和未来的预测长度
                  'pre_calc_days_num': [2],
                  'weight_kind': ['v3'],
                  'discount': [95],
                  'corr_rolling_nums': [10],
                  'corr_max_diff': [0.1],   # 10、滚动时用的阈值判断参数
                  'corr_max_diff2': [0.1],   # 断层时用的阈值判断参数
                  'real_time': [False]   # 为True时要把start_date和end_date换掉
                  }
    param_list = list(product(*[param_dict[key] for key in param_dict.keys()]))
    for param in param_list:
        param = list(param)
        # start_date_ = 20170101
        # end_date_ = 20201231
        start_date_ = 20210101
        end_date_ = 20211031
        now_param_dict = dict(zip(param_dict.keys(), param))

        """设置real_time，为True时"""
        smt1 = SimiMethod1(start_date=start_date_, end_date=end_date_, **now_param_dict)
        filename = smt1.trans_param2filename(param, exclude=[1, 6, 7, 9, 10, 11, 12])

        result = smt1.get_hedge_list(mode='multi', kernal_num=24)
        # result = smt1.get_hedge_list(mode='serial', kernal_num=24)
        # result = smt1.get_simi_stock(600711, 20200102)

        save_name = f'{filename}_result.pkl'
        util.save_list2pkl(result, txTest_path, save_name)