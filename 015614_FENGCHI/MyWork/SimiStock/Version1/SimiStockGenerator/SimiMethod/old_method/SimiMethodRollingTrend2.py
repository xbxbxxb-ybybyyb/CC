# coding: utf-8
# Author：fengchi863
# Date ：2022/4/8 0:25

"""
滚动样例，继承自SimiMethodRollingBase，滚动都是叠加风格之后的，参数为0.6，0.2，0.2
20220412:
进行一定规则的选取，规则如下：
1、	大宗历史样本选择上，采用在95%样本下有0.8以上对冲标的的样本，共1121个；
2、	滚动计算时，更换标准如下：
1）	第一轮选取排名靠前的3个对冲标的，并记录其相关性；
2）	下一轮与上一轮进行比较：
若上一轮使用的三个个股任意一只的相关性下降超过0.1，进行全部替换，替换时仍以满足条件的排名靠前的3个为准，若一个也没有，则输出空；
若都不超过0.1，则保持不变，并更新相关性的最大值；
"""

from itertools import product

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, Imputer

from SimiStock.DataPrepare.BarraFactor import BarraFactor
from SimiStockGenerator.SimiMethodBase.SimiMethodRollingBase import SimiMethodRollingBase
from SimiStock.SimiStockGenerator.util import util
from SimiStock.config.path_config import *
from SimiStock.dataApi import getData

"""皮尔逊相似度、规模、波动"""
weight_dict = {'v0': [1, 0, 0],
               'v1': [0.6, 0.4, 0],
               'v2': [0.8, 0.2, 0],
               'v3': [0.6, 0.2, 0.2]}
bf = BarraFactor()


class SimiMethodRollingTrend2(SimiMethodRollingBase):
    def __init__(self, start_date=20180101, end_date=20211231, concept='SW1', pre_days_num=252, hedge_max_num=14,
                 corr_threshold=(8, 10), weight_kind='v3', method_name=None, discount=95, corr_base=(8, 10),
                 corr_base_flag=False, corr_base_file=None, history_future_len=(240, 5)):
        super().__init__(start_date, end_date, concept=concept, discount=discount,
                         history_future_len=history_future_len)
        pctchg = getData.get_daily_1factor('pct_chg', date_list=self.shift_date_list)
        date_list = np.load(barra_path2 + 'date_list.npy')
        code_list = np.load(barra_path2 + 'code_list.npy')

        self.method_name = method_name
        self.pre_days_num = pre_days_num

        self.pctchg = pctchg
        self.barra_date_list = list(date_list)
        self.barra_code_list = list(code_list)
        self.hedge_max_num = hedge_max_num
        self.corr_threshold = corr_threshold
        self.weight_kind = weight_kind
        self.corr_base = corr_base
        self.corr_base_flag = corr_base_flag
        self.corr_base_file = pd.read_pickle(hedge_path + corr_base_file)

    def min_max_transfer(self, df: pd.DataFrame):
        tmp_df = df.copy()
        scaler = MinMaxScaler()
        im = Imputer(missing_values='NaN', strategy='mean', axis=1)
        tmp_df = im.fit_transform(tmp_df)
        ret = scaler.fit_transform(tmp_df.T)
        ret = ret.T
        ret = pd.DataFrame(ret, columns=df.columns, index=df.index)
        return ret

    def arr_min_max_transfer(self, arr: np.array):
        tmp_df = arr.copy()
        scaler = MinMaxScaler()
        im = Imputer(missing_values='NaN', strategy='mean', axis=1)
        tmp_df = im.fit_transform(pd.DataFrame(tmp_df).T)
        ret = scaler.fit_transform(tmp_df.T)
        return ret[:, 0]

    def simi_strategy(self, stk_id, date_tuple_list):
        hedge_list = list()
        corr_base_low, corr_base_high = self.corr_base[0] / 10, self.corr_base[1] / 10
        corr_low, corr_high = self.corr_threshold[0] / 10, self.corr_threshold[1] / 10
        first_flag = True   # 记录第几次进入循环
        last_hedge_corr_dict = dict()
        for date_tuple in date_tuple_list:
            calc_date, start_date, end_date, train_start_date, train_end_date = date_tuple
            if self.corr_base_flag:
                if first_flag and (start_date, stk_id) not in self.corr_base_file:
                    return list()
                else:
                    first_flag = False
            concept_list = self.get_concept_list(stk_id, calc_date)
            weight_list = weight_dict[self.weight_kind]

            # 计算相关性等
            stk_pctchg = self.pctchg.loc[train_start_date:train_end_date][stk_id]
            # other_pctchg = self.pctchg.loc[train_start_date:train_end_date][concept_list]
            # corr = pd.DataFrame(other_pctchg).corrwith(stk_pctchg)
            # corr2 = corr.reindex(index=concept_list).copy()
            # corr = corr.values
            # corr = self.arr_min_max_transfer(corr[:, None])
            # corr = pd.Series(corr, index=concept_list).reindex(self.barra_code_list).values
            other_pctchg = self.pctchg.loc[train_start_date:train_end_date]
            corr = pd.DataFrame(other_pctchg[self.barra_code_list]).corrwith(stk_pctchg)
            corr2 = corr.reindex(index=concept_list).copy()
            corr = corr.values
            corr = self.arr_min_max_transfer(corr[:, None])
            corr = pd.Series(corr, index=self.barra_code_list).values
            lncap = bf.get_1factor('LNCAP', calc_date)
            lncap_diff = abs(lncap - lncap[self.barra_code_list.index(stk_id)])
            lncap_diff = self.arr_min_max_transfer(lncap_diff[:, None])
            dastd = bf.get_1factor('DASTD', calc_date)
            dastd_diff = abs(dastd - dastd[self.barra_code_list.index(stk_id)])
            dastd_diff = self.arr_min_max_transfer(dastd_diff[:, None])

            ret = corr * weight_list[0] - \
                  lncap_diff * weight_list[1] - \
                  dastd_diff * weight_list[2]
            ret_s = pd.Series(ret, index=self.barra_code_list)

            ret_s = ret_s[concept_list].sort_values(ascending=False)
            tmp_list1 = ret_s.index.tolist()
            s_corr = corr2.sort_values(ascending=False)

            # 隔断分层
            corr_diff = s_corr.shift(1) - s_corr
            manzu_list = corr_diff[corr_diff > 0.1].index.tolist()
            if manzu_list:
                for manzu in manzu_list:
                    if corr_low < s_corr[manzu] < corr_base_low:
                        manzu_idx = s_corr.index.tolist().index(manzu)
                        corr_low = s_corr.iloc[manzu_idx]

            tmp_list2 = s_corr[(s_corr > corr_low) & (s_corr <= corr_high)].index.tolist()
            ret_list = [x for x in tmp_list1 for y in tmp_list2 if x == y]

            # 用hedge_max_num截断
            if len(ret_list) >= self.hedge_max_num:
                ret_list = ret_list[:self.hedge_max_num]

            # 处理输出的标的部分
            append_hedge_list = ret_list[:min(3, len(ret_list))]
            replace_flag = False
            if append_hedge_list:   # 如果有值
                if not last_hedge_corr_dict:    # 如果上次是空，直接加入
                    for stk in append_hedge_list:
                        last_hedge_corr_dict.update({stk: corr2[stk]})
                # 判断是否存在差距过大问题
                else:   # 如果上次不是空，依次判断是否超过阈值
                    for stk in list(last_hedge_corr_dict.keys()):
                        # 处理停复牌或者行业变更，因为返回的concept_list里不再包含这个股票
                        if stk not in corr2.index:
                            replace_flag = True
                            break
                        corr_diff = corr2[stk] - last_hedge_corr_dict[stk]
                        if corr_diff < -0.1:    # 如果有任意一个超过阈值，替换
                            replace_flag = True
                            break
                        # 对没有超过阈值的进行更新
                        last_hedge_corr_dict.update({stk: max(last_hedge_corr_dict[stk], corr2[stk])})
                    if replace_flag:
                        last_hedge_corr_dict = dict()   # 清空原有字典
                        append_hedge_list = ret_list[:min(3, len(ret_list))]
                        for stk in append_hedge_list:
                            last_hedge_corr_dict.update({stk: corr2[stk]})
                    else:
                        append_hedge_list = list(last_hedge_corr_dict.keys())   # 不替换，使用上一次的
            else:   # 如果新的是空的
                for stk in list(last_hedge_corr_dict.keys()):
                    # 处理停复牌或者行业变更，因为返回的concept_list里不再包含这个股票
                    if stk not in corr2.index:
                        replace_flag = True
                        break
                    corr_diff = corr2[stk] - last_hedge_corr_dict[stk]
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
                           'hedge_list': append_hedge_list}
            hedge_list.append(append_dict)
        return hedge_list


if __name__ == '__main__':
    param_dict = {'method_name': ['滚动'],
                  'concept': ['SW1'],
                  'pre_days_num': [120],
                  'hedge_max_num': [7],
                  'corr_threshold': [(8, 10)],
                  'corr_base': [(8, 10)],
                  'weight_kind': ['v3'],
                  'discount': [95],
                  'history_future_len': [(240, 5)]}
    param_list = list(product(param_dict['method_name'],
                              param_dict['concept'],
                              param_dict['pre_days_num'],
                              param_dict['hedge_max_num'],
                              param_dict['corr_threshold'],
                              param_dict['weight_kind'],
                              param_dict['discount'],
                              param_dict['history_future_len']))
    for param in param_list:
        start_date = 20210628
        end_date = 20210630
        method_name = param[0]
        concept = param[1]
        pre_days_num = param[2]
        hedge_max_num = param[3]
        corr_threshold = param[4]
        weight_kind = param[5]
        discount = param[6]
        history_future_len = param[7]
        corr_base_file = '叠加风格5_14_(8, 10)_v3_95_20200701_20210630_result.pkl_include_stk.pkl'
        smt1 = SimiMethodRollingTrend2(start_date=start_date, end_date=end_date, concept=concept, pre_days_num=pre_days_num,
                               hedge_max_num=hedge_max_num, corr_threshold=corr_threshold, weight_kind=weight_kind,
                               method_name=method_name, discount=discount, corr_base=(8, 10), corr_base_flag=True,
                               corr_base_file=corr_base_file, history_future_len=history_future_len)
        # result = smt1.get_hedge_list(mode='serial', kernal_num=24)
        result = smt1.get_hedge_list(mode='multi', kernal_num=24)
        # result = smt1.get_simi_stock(783, 20180103)
        save_name = f'{method_name}_{hedge_max_num}_{corr_threshold}_{history_future_len}_{weight_kind}_{discount}_{start_date}_{end_date}_result.pkl'
        util.save_list2pkl(result, hedge_path, save_name)