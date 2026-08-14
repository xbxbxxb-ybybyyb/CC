# coding: utf-8
# Author：fengchi863
# Date ：2022/5/30 13:31

"""
第三套版本，在对冲标的上的剔除条件上进行测试
"""

import sys
sys.path.append('/data/user/015614/MyWork')
sys.path.append('/data/user/015614/MyWork/SimiStock')

from itertools import product
import numpy as np
import pandas as pd
from tqdm import tqdm
from SimiStock.DataPrepare.BarraFactor import BarraFactor
from SimiStock.SimiStockGenerator.util import util
from SimiStock.config.path_config import *
from SimiStock.dataApi import getData
from SimiStock.dataApi import tradeDate
from SimiStockGenerator.SimiMethodBase.SimiMethodRollingBase import SimiMethodRollingBase
from SimiStock.DataPrepare.filtered_blcok_data import FileterMethod

np.random.seed(2022)

"""K线相似度、形态相似度、走势"""
weight_dict = {'v3': [0.6, -0.4]}
bf = BarraFactor()
fm = FileterMethod(tradeDate.get_recent_trade_date(dividing_point=23))  # 23点前都是用前一天的数据

LONG_PERIOD = 240
MID_PERIOD = 120
SHORT_PERIOD = 60


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

    def judge_stk_std(self, stk_id, start_date, end_date):
        startDate4Long = tradeDate.get_pre_trade_date(start_date, LONG_PERIOD)
        startDate4Short = tradeDate.get_pre_trade_date(start_date, SHORT_PERIOD)
        long_std = self.pctchg.loc[startDate4Long:start_date, stk_id].apply(lambda x: x.rolling(LONG_PERIOD).dropna().std())
        short_std = self.pctchg.loc[startDate4Short:start_date, stk_id].apply(lambda x: x.rolling(SHORT_PERIOD).dropna().std())
        long_std_quantile = long_std.iloc[-1].quantile(90)
        short_std_quantile = short_std.iloc[-1].quantile(90)
        _flag1 = long_std > long_std_quantile
        _flag2 = short_std > short_std_quantile
        _stk_list1 = _flag1[_flag1].index.tolist()
        _stk_list2 = _flag2[_flag2].index.tolist()
        return list(set(_stk_list1 + _stk_list2))

    def trans_param2filename(self, _param, exclude: list):
        _param = _param + [self.start_date, self.end_date]
        tmp_param = list()
        for idx, value in enumerate(_param):
            if idx not in exclude:
                tmp_param.append(str(value))
        filename_ = '_'.join(tmp_param)
        return filename_

    def get_kline_score(self, stk_id, train_date_list, concept_list):
        pre_close = getData.get_daily_1factor('pre_close_badj', date_list=train_date_list)
        close = getData.get_daily_1factor('close_badj', date_list=train_date_list) / pre_close - 1
        open = getData.get_daily_1factor('open_badj', date_list=train_date_list) / pre_close - 1
        high = getData.get_daily_1factor('high_badj', date_list=train_date_list) / pre_close - 1
        low = getData.get_daily_1factor('low_badj', date_list=train_date_list) / pre_close - 1

        close = close.fillna(0)
        open = open.fillna(0)
        high = high.fillna(0)
        low = low.fillna(0)

        close_corr = pd.DataFrame(close[concept_list]).corrwith(close[stk_id])
        open_corr = pd.DataFrame(open[concept_list]).corrwith(open[stk_id])
        high_corr = pd.DataFrame(high[concept_list]).corrwith(high[stk_id])
        low_corr = pd.DataFrame(low[concept_list]).corrwith(low[stk_id])
        trend_corr = (close_corr + open_corr + low_corr + high_corr) / 4

        # 这里修改为只用K线中的趋势相似度
        trend_corr = trend_corr.reindex(self.barra_code_list).values
        kline_score = self.arr_min_max_transfer(trend_corr)

        return kline_score

    def get_barra_score(self, stk_id, calc_date, concept_list):
        lncap = bf.get_1factor('LNCAP', calc_date)
        lncap_diff = abs(lncap - lncap[self.barra_code_list.index(stk_id)])
        lncap_diff = self.arr_min_max_transfer(lncap_diff)
        dastd = bf.get_1factor('DASTD', calc_date)
        dastd_diff = abs(dastd - dastd[self.barra_code_list.index(stk_id)])
        dastd_diff = self.arr_min_max_transfer(dastd_diff)
        return lncap_diff * 0.5 + dastd_diff * 0.5

    def simi_strategy(self, stk_id, date_tuple_list):
        hedge_list = list()
        corr_low, corr_high = self.corr_threshold[0], self.corr_threshold[1]
        first_flag = True  # 记录第几次进入循环
        for date_tuple in date_tuple_list:
            calc_date, start_date, end_date, train_start_date, train_end_date = date_tuple
            concept_list = self.get_concept_list(stk_id, calc_date)
            weight_list = weight_dict[self.weight_kind]

            corr_res, corr_stats = self.judge_corr_stability(stk_id, train_start_date, train_end_date, concept_list,
                                                             pre_times=self.corr_rolling_nums)

            if first_flag:
                if corr_stats['最大值是否介于基础阈值'].iloc[0] == 0:  # 若不满足基本条件，返回空
                    return list()
            # corr = corr_stats['_mean'].reindex(self.barra_code_list).values
            corr_copy = corr_stats['_mean'].reindex(index=concept_list).copy()
            s_corr = corr_copy.sort_values(ascending=False)
            remove_stk_list = corr_stats.query(f'max_diff > 0.1 & _min < {self.corr_threshold[0] - 0.1}').index.tolist()

            # %% 叠加风格部分 以及 K线相似度
            date_list = tradeDate.get_date_range(train_start_date, train_end_date)
            kline_score = self.get_kline_score(stk_id, date_list, concept_list)
            barra_score = self.get_barra_score(stk_id, calc_date, concept_list)
            ret = kline_score * weight_list[0] + barra_score * weight_list[1]
            ret_s = pd.Series(ret, index=self.barra_code_list)

            ret_s = ret_s[concept_list].sort_values(ascending=False)
            tmp_list1 = ret_s.index.tolist()

            tmp_list2 = s_corr[(s_corr > corr_low) & (s_corr <= corr_high)].index.tolist()

            # 用于增加剔除的代码


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
    param_dict = {'method_name': ['模拟跟踪'],
                  'concept': ['SW20211'],
                  'hedge_max_num': [7],
                  'corr_threshold': [(0.5, 1)],
                  'base_corr': [(0.5, 1)],
                  'history_future_len': [(120, 120)],   # 5、历史的训练长度和未来的预测长度
                  'pre_calc_days_num': [2],
                  'weight_kind': ['v3'],
                  'discount': [95],
                  'corr_rolling_nums': [10],
                  'corr_max_diff': [0.1],   # 10、滚动时用的阈值判断参数
                  'corr_max_diff2': [0.1],   # 断层时用的阈值判断参数
                  'real_time': [True]   # 为True时要把start_date和end_date换掉
                  }
    param_list = list(product(*[param_dict[key] for key in param_dict.keys()]))
    for param in param_list:
        param = list(param)
        start_date_ = tradeDate.get_pre_trade_date(tradeDate.get_today(), -2)
        end_date_ = tradeDate.get_pre_trade_date(tradeDate.get_today(), -2)
        now_param_dict = dict(zip(param_dict.keys(), param))

        """设置real_time，为True时"""
        smt1 = SimiMethod1(start_date=start_date_, end_date=end_date_, **now_param_dict)
        filename = smt1.trans_param2filename(param, exclude=[6, 7, 9, 10, 11, 12])

        result = smt1.get_hedge_list(mode='multi', kernal_num=24)
        # result = smt1.get_hedge_list(mode='serial', kernal_num=24)
        # result = smt1.get_simi_stock(600711, 20200102)

        result_copy = list()
        for tmp_result in tqdm(result):
            stk_id = tmp_result['stk_id']
            trade_date = tmp_result['date']
            if not fm.judge_filter(stk_id):
                result_copy.append(tmp_result)
        result = result_copy
        save_name = f'{filename}_result.pkl'

        # save_name = f'{filename}_剔除_result.pkl'
        util.save_list2pkl(result, txTest_path, save_name)
