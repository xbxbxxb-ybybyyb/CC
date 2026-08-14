# coding: utf-8
# Author：fengchi863
# Date ：2022/5/16 10:25

import sys
sys.path.append('/data/user/015614/MyWork')
sys.path.append('/data/user/015614/MyWork/SimiStock')

"""
此版本分三个部分，三个不同的part
1）80%以上有3只的
2）80%以上有3只以下的，阈值放宽到60%，且数量≥3只
3）70%-80%的，阈值放宽到60%，且数量≥3只

2022.5.16日更新
新增一个part4，0.5-1，0.5-1，不隔断，使用K线相似度，原来的part1、part2、part3不变
"""

from itertools import product

import numpy as np
import pandas as pd

from SimiStock.DataPrepare.BarraFactor import BarraFactor
from SimiStock.SimiStockGenerator.util import util
from SimiStock.config.path_config import *
from SimiStock.dataApi import getData
from SimiStock.dataApi import tradeDate
from SimiStock.dataApi import indName
from SimiStockGenerator.SimiMethodBase.SimiMethodRollingBase import SimiMethodRollingBase

np.random.seed(2022)

"""皮尔逊相似度、形态相似度、走势"""
#weight_dict = {'v3': [0.3, 0.3, -0.4]}
weight_dict = {'v3': [0.6, -0.4]}
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

        close = getData.get_daily_1factor('close_badj', date_list=train_date_list)
        open = getData.get_daily_1factor('open_badj', date_list=train_date_list)

        intra_pct = close / open - 1
        up_down_position = intra_pct > 0
        up_down_position = (up_down_position[concept_list].T == up_down_position[stk_id]).T
        diff_pct = abs(self.pctchg.loc[train_date_list, concept_list].T - self.pctchg.loc[train_date_list, stk_id]).T
        diff_pct = (20 - diff_pct) / 20
        shape_corr = (up_down_position * diff_pct).sum() / self.history_period

        kline_score = trend_corr * shape_corr
        kline_score = kline_score.reindex(self.barra_code_list).values
        kline_score = self.arr_min_max_transfer(kline_score)

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
        corr_base_low, corr_base_high = self.base_corr[0], self.base_corr[1]
        corr_low, corr_high = self.corr_threshold[0], self.corr_threshold[1]
        first_flag = True  # 记录第几次进入循环
        last_hedge_corr_dict = dict()
        for date_tuple in date_tuple_list:
            calc_date, start_date, end_date, train_start_date, train_end_date = date_tuple

            # 只选择部分行业
            ind_name = indName.sw_level1[self.concept_df.loc[calc_date, stk_id]]
            if ind_name not in ['银行','非银金融', '钢铁', '公用事业', '家用电器',
                                '建筑装饰', '房地产', '汽车', '商业贸易', '采掘']:
                return list()

            concept_list = self.get_concept_list(stk_id, calc_date)
            weight_list = weight_dict[self.weight_kind]

            corr_res, corr_stats = self.judge_corr_stability(stk_id, train_start_date, train_end_date, concept_list,
                                                             pre_times=self.corr_rolling_nums)

            if first_flag:
                if corr_stats['最大值是否介于基础阈值'].iloc[0] == 0:  # 若不满足基本条件，返回空
                    return list()

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
            tmp_list2 = list(set(tmp_list2).difference(set(remove_stk_list)))
            ret_list = [x for x in tmp_list1 for y in tmp_list2 if x == y]

            # 用hedge_max_num截断
            if len(ret_list) >= self.hedge_max_num:
                ret_list = ret_list[:self.hedge_max_num]
            if len(ret_list) < 3:
                return list()   # [Warning]!!!这个条件只限于添加在非滚动的版本上!!!

            #%% 处理输出的标的部分，只有在不等于120时才输出3个，这样更新
            if self.future_period != 120:
                append_hedge_list = ret_list[:min(3, len(ret_list))]
                replace_flag = False
                if append_hedge_list:  # 如果有值
                    if not last_hedge_corr_dict:  # 如果上次是空，直接加入
                        for stk in append_hedge_list:
                            last_hedge_corr_dict.update({stk: corr_copy[stk]})
                    # 判断是否存在差距过大问题
                    else:  # 如果上次不是空，依次判断是否超过阈值
                        for stk in list(last_hedge_corr_dict.keys()):
                            # 处理停复牌或者行业变更，因为返回的concept_list里不再包含这个股票
                            if stk not in corr_copy.index:
                                replace_flag = True
                                break
                            corr_diff = corr_copy[stk] - last_hedge_corr_dict[stk]
                            if corr_diff < -self.corr_max_diff:  # 如果有任意一个超过阈值，替换
                                replace_flag = True
                                break
                            # 对没有超过阈值的进行更新
                            last_hedge_corr_dict.update({stk: max(last_hedge_corr_dict[stk], corr_copy[stk])})
                        if replace_flag:
                            last_hedge_corr_dict = dict()  # 清空原有字典
                            append_hedge_list = ret_list[:min(3, len(ret_list))]
                            for stk in append_hedge_list:
                                last_hedge_corr_dict.update({stk: corr_copy[stk]})
                        else:
                            last_num = len(last_hedge_corr_dict.keys())
                            if len(append_hedge_list) <= last_num:
                                append_hedge_list = list(last_hedge_corr_dict.keys())  # 不替换，使用上一次的
                            else:
                                for stk in append_hedge_list:
                                    if stk not in list(last_hedge_corr_dict.keys()):
                                        append_hedge_list.append(stk)
                                        last_hedge_corr_dict.update({stk: corr_copy[stk]})
                                        if len(append_hedge_list) == 3:
                                            break
                else:  # 如果新的是空的
                    for stk in list(last_hedge_corr_dict.keys()):
                        # 处理停复牌或者行业变更，因为返回的concept_list里不再包含这个股票
                        if stk not in corr_copy.index:
                            replace_flag = True
                            break
                        corr_diff = corr_copy[stk] - last_hedge_corr_dict[stk]
                        if corr_diff < -0.1:  # 如果有任意一个超过阈值，替换
                            replace_flag = True
                            break
                    if replace_flag:
                        last_hedge_corr_dict = dict()  # 清空原有字典
                        append_hedge_list = append_hedge_list
                    else:  # 不替换，使用上一次的
                        append_hedge_list = list(last_hedge_corr_dict.keys())

                append_dict = {'calc_date': calc_date,
                               'start_date': start_date,
                               'end_date': end_date,
                               'hedge_list': append_hedge_list,
                               'hedge_value': list(s_corr[append_hedge_list])}
                hedge_list.append(append_dict)
            else:
                append_dict = {'calc_date': calc_date,
                               'start_date': start_date,
                               'end_date': end_date,
                               'hedge_list': ret_list,
                               'hedge_value': list(s_corr[ret_list])}
                hedge_list.append(append_dict)
                first_flag = False
        return hedge_list


if __name__ == '__main__':
    param_dict = {'method_name': ['新版本'],
                  'concept': ['SW1'],
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
        # start_date_ = 20220421
        # end_date_ = 20220421
        now_param_dict = dict(zip(param_dict.keys(), param))

        """设置real_time，为True时"""
        smt1 = SimiMethod1(start_date=start_date_, end_date=end_date_, **now_param_dict)
        filename = smt1.trans_param2filename(param, exclude=[1, 6, 7, 9, 10, 11, 12])

        # result = smt1.get_hedge_list(mode='multi', kernal_num=24)
        result = smt1.get_hedge_list(mode='serial', kernal_num=24)
        # result = smt1.get_simi_stock(300070, 20220425)

        filename1 = f'新版本_7_(0.8, 1)_(0.8, 1)_(120, 120)_95_{start_date_}_{start_date_}_part1_result.pkl'
        filename2 = f'新版本_7_(0.6, 1)_(0.8, 1)_(120, 120)_95_{start_date_}_{start_date_}_part2_result.pkl'
        filename3 = f'新版本_7_(0.6, 1)_(0.7, 0.8)_(120, 120)_95_{start_date_}_{start_date_}_part3_result.pkl'
        part1 = pd.read_pickle(hedge_path + filename1)
        part2 = pd.read_pickle(hedge_path + filename2)
        part3 = pd.read_pickle(hedge_path + filename3)
        part1_stk_list = [x['stk_id'] for x in part1]
        part2_stk_list = [x['stk_id'] for x in part2]
        part3_stk_list = [x['stk_id'] for x in part3]
        haved_stk_list = list(set(part1_stk_list + part2_stk_list + part3_stk_list))
        filtered_result = [x for x in result if x['stk_id'] not in haved_stk_list]

        save_name = f'{filename}_part4_result.pkl'
        util.save_list2pkl(filtered_result, txTest_path, save_name)