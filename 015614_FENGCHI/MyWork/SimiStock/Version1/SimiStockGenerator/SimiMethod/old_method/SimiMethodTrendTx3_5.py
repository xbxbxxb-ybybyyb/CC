# coding: utf-8
# Author：fengchi863
# Date ：2022/4/8 0:25

"""
20220412
叠加风格5的基础上，使用95折样本（此处新修改了Base)
使用了SimiMethodTrendTx3_4生成的大于0.8的样本，选取其中的样本进行保存，然后替换到这个上面
其中样本内是1121个样本，样本外是419个样本
"""

from SimiStockGenerator.SimiMethodBase.SimiMethodBase import SimiMethodBase
from sklearn.preprocessing import MinMaxScaler, Imputer
from SimiStock.SimiStockGenerator.util import util
from SimiStock.config.path_config import *
import pandas as pd
from itertools import product

"""皮尔逊相似度、规模、波动、动量、质量"""
weight_dict = {'v0': [1, 0, 0],
               'v1': [0.6, 0.4, 0],
               'v2': [0.8, 0.2, 0],
               'v3': [0.6, 0.2, 0.2]}

def get_date_stk_list(filename):
    print(filename)
    result = pd.read_pickle(hedge_path + filename)
    ret_list = list()
    for hedge in result:
        stk_id = hedge['stk_id']
        trade_date = hedge['date']
        ret_list.append((trade_date, stk_id))
    util.save_list2pkl(ret_list, hedge_path, f'{filename}_include_stk.pkl')


class SimiStyleMethod(SimiMethodBase):
    def __init__(self, start_date=20180101, end_date=20211231, concept='SW1', pre_days_num=120, hedge_max_num=12,
                 corr_threshold: tuple=(0.8, 1), weight_kind='v1', method_name=None, base_file_name=None,
                 discount=95):
        super().__init__(start_date, end_date, concept=concept, discount=discount)
        corr = pd.read_pickle(factor_path + 'pct_pearson_corr_120_20171201_20210730.pkl')
        corr2 = pd.read_pickle(factor_path + 'pct_pearson_corr_120_20171201_20210730.pkl')
        dastd = pd.read_pickle(factor_path + 'DASTD.pkl')
        lncap = pd.read_pickle(factor_path + 'LNCAP.pkl')
        if base_file_name:
            base_sample = pd.read_pickle(hedge_path + base_file_name)
            self.base_sample = base_sample
            self.base_threshold = eval(base_file_name.split('_')[2])
        else:
            self.base_sample = None

        self.method_name = method_name
        self.pre_days_num = pre_days_num
        self.corr2 = corr2
        self.corr = self.min_max_transfer(corr)
        self.lncap = self.min_max_transfer(lncap)
        self.dastd = self.min_max_transfer(dastd)

        self.hedge_max_num = hedge_max_num
        self.corr_threshold = corr_threshold
        self.weight_kind = weight_kind

    def min_max_transfer(self, df: pd.DataFrame):
        tmp_df = df.copy()
        scaler = MinMaxScaler()
        im = Imputer(missing_values='NaN', strategy='mean', axis=1)
        tmp_df = im.fit_transform(tmp_df)
        ret = scaler.fit_transform(tmp_df.T)
        ret = ret.T
        ret = pd.DataFrame(ret, columns=df.columns, index=df.index)
        return ret

    def simi_strategy(self, stk_id, trade_date, concept_list):
        if self.base_sample and ((trade_date, stk_id) not in self.base_sample):
            return list(), list(), list()
        corr_low, corr_high = self.corr_threshold[0] / 10, self.corr_threshold[1] / 10
        corr_base_low, corr_base_high = self.base_threshold[0] / 10, self.base_threshold[1] / 10
        weight_list = weight_dict[self.weight_kind]
        ret_df = self.corr.loc[(trade_date, stk_id), :] * weight_list[0] - \
            self.lncap.loc[(trade_date, stk_id), :] * weight_list[1] - \
            self.dastd.loc[(trade_date, stk_id), :] * weight_list[2]

        ret_df = ret_df[concept_list].sort_values(ascending=False)
        tmp_list1 = ret_df.index.tolist()
        s_corr = self.corr2.loc[(trade_date, stk_id)][concept_list].sort_values(ascending=False)

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

        if len(ret_list) >= self.hedge_max_num:
            ret_list = ret_list[:self.hedge_max_num]

        # 根据第一个最相似筛选样本
        if len(ret_list) > 0 and corr_low < s_corr.iloc[0] <= corr_high:
            return ret_list, [1] * len(ret_list), ret_df[ret_list].tolist()
        else:
            return list(), list(), list()


if __name__ == '__main__':
    param_dict = {'method_name': ['叠加风格5'],
                  'concept': ['SW1'],
                  'pre_days_num': [120],
                  'hedge_max_num': [14],
                  # 'corr_threshold': [(8, 10), (7, 8), (6, 7), (5, 6)],
                  # 'corr_threshold': [(7, 10), (6, 10), (5, 10)],
                  'corr_threshold': [(6, 10)],
                  'base_file': [(8, 10)],
#                  'corr_threshold': [(6, 8), (5, 8)],
#                  'base_file': [(7, 8)],
#                  'corr_threshold': [(5, 7)],
#                   'base_file': [(6, 7)],
                  'weight_kind': ['v3']}
    param_list = list(product(param_dict['method_name'],
                              param_dict['concept'],
                              param_dict['pre_days_num'],
                              param_dict['hedge_max_num'],
                              param_dict['corr_threshold'],
                              param_dict['weight_kind'],
                              param_dict['base_file']))
    for param in param_list:
        # start_date = 20180101
        # end_date = 20200630
        start_date = 20200701
        end_date = 20210630
        method_name = param[0]
        concept = param[1]
        pre_days_num = param[2]
        hedge_max_num = param[3]
        corr_threshold = param[4]
        weight_kind = param[5]
        base_file = param[6]
        base_name = f'{method_name}_{hedge_max_num}_{base_file}_{weight_kind}_95_{start_date}_{end_date}_result.pkl'
        smt1 = SimiStyleMethod(start_date=start_date, end_date=end_date, concept=concept, pre_days_num=pre_days_num,
                               hedge_max_num=hedge_max_num, corr_threshold=corr_threshold, weight_kind=weight_kind,
                               method_name=method_name, discount=95, base_file_name=f'{base_name}_include_stk.pkl')
        # result = smt1.get_hedge_list(mode='multi', kernal_num=24)
        result = smt1.get_hedge_list(mode='serial', kernal_num=24)
        # result = smt1.get_simi_stock(783, 20180103)
        save_name = f'{method_name}_{hedge_max_num}_{corr_threshold}_{weight_kind}_95_{start_date}_{end_date}_result.pkl'
        # get_date_stk_list(save_name)
        util.save_list2pkl(result, hedge_path, save_name)