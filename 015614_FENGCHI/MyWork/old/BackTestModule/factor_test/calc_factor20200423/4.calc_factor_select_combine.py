# coding: utf-8
# Author：fengchi863
# Date ：2020/4/27 8:59
'''
读取全量测试的结果，结果文件夹:
'/data/group/800319/junkData/temp_factor_by_fc/StrategyBackTest/strats_append_with_defalt_factor_20200423/'
对累计超额收益率进行排序，得到前20个因子（不同参数下的如何进行考虑）
按1-10、11-20进行分层，对每一层进行全组合
'''

import pandas as pd, numpy as np
import itertools
from usefulTools import *
import os
import time

COMBINE_NUM = 10
factor_combine_output_path = '/data/group/800319/storeFactor/combine_ffactor20200428/'
factor_top_n_output_path = '/data/group/800319/storeFactor/topN_ffactor20200428/'
factor_rank_input_path = '/data/group/800319/storeFactor/original_intrafactor_rank/'
factor_result_analysis_output_path = '/data/group/800319/junkData/temp_factor_by_fc/StrategyBackTest/strats_append_with_defalt_factor_20200428/'
#
# # 30个因子的排列，并且按顺序
factor_result_analysis = pd.read_excel(factor_result_analysis_output_path + \
                                       '日内因子净值回测结果(20200428全量)_(0.5, 200, 400).xlsx', sheet_name='全量测试结果', index_col=0)
factor_list = factor_result_analysis.sort_values('累计超额收益率', ascending=False).iloc[:20]['因子名称'].tolist()
# factor_description = pd.read_excel('/data/group/800319/junkData/temp_factor_by_fc/StrategyBackTest/'+\
#                             '因子全量测试专用.xlsx')
# factor_list = factor_description['因子名称'][:20].tolist()
combine_dict = dict()

# 为了节约计算时间，生成所有的rank
def get_all_rank():
    file_dir = r'/data/group/800319/storeFactor/original_intrafactor/'
    factor_name_list = sorted([os.path.splitext(x)[0] for x in os.listdir(file_dir)])
    for factor_name in factor_name_list:
        print(factor_name)
        factor = pd.read_hdf(file_dir + factor_name + '.h5', factor_name)
        index, columns = factor.index, factor.columns
        factor = frame2arr(factor)
        factor = cross_rank(factor)
        factor = arr2frame(factor, index, columns)
        factor.to_hdf('/data/group/800319/storeFactor/original_intrafactor_rank/' + \
                      factor_name + '.h5', factor_name)

def get_combinations(factor_list):
    factor_slice_list = [factor_list[:10], factor_list[10:20]]
    df_factor_record = pd.DataFrame(columns=['层级', '组合个数', '序号', '因子序列'])
    for slice_idx, factors in enumerate(factor_slice_list):
        for num in range(1, COMBINE_NUM+1): # 1-10
            combine_list = list(itertools.combinations(range(0,COMBINE_NUM), num))
            combine_dict.update({num: combine_list})

        for combine_num in combine_dict.keys():
            for idx, combine_tuple in enumerate(combine_dict[combine_num]):
                if slice_idx == 1:
                    i=1
                combine_dict[combine_num][idx] = list(map(lambda x: factors[x], combine_tuple))

        # 记录因子名称与组合对应的记录表
        for combine_num in combine_dict.keys():
            for idx, combine_list in enumerate(combine_dict[combine_num]):
                factors = combine_list
                ffactor_name = 'ffactor_%d_%d_%d' % (slice_idx+1, combine_num, idx+1)
                print(ffactor_name, ','.join(combine_list))
                df_factor_record = df_factor_record.append({'层级':slice_idx+1, \
                                         '组合个数':combine_num, \
                                         '序号':idx+1, \
                                         '因子序列':','.join(combine_list)}, ignore_index=True)
                if os.path.exists(factor_combine_output_path + ffactor_name + '.h5'):
                    print(ffactor_name, '已存在')
                    continue
                # 开始计算组合因子
                e = time.clock()
                if combine_num == 1:
                    first_factor = factors[0]
                    res = pd.read_hdf(factor_rank_input_path + first_factor + '.h5', first_factor)
                if combine_num > 1:
                    # 检查是否已经计算了前面的因子，减小时间复杂度
                    last_factor_list = factors[:-1]
                    tmp1, tmp2, tmp3 = \
                        tuple(df_factor_record[df_factor_record['因子序列'] == ','.join(last_factor_list)][['层级', '组合个数', '序号']].iloc[0].tolist())
                    last_ffactor_name = 'ffactor_%d_%d_%d' % (tmp1, tmp2, tmp3)
                    last_factor = pd.read_hdf(factor_combine_output_path + last_ffactor_name + '.h5', last_ffactor_name)
                    index, columns = last_factor.index, last_factor.columns
                    res = frame2arr(last_factor)
                    res += frame2arr(pd.read_hdf(factor_rank_input_path + factors[-1] + '.h5', factors[-1]))
                    res = arr2frame(res, index, columns)
                res.to_hdf(factor_combine_output_path + ffactor_name + '.h5', ffactor_name)
                print(time.clock() - e)
    return df_factor_record

def combine_top_n(factor_list, num):
    """
    对累计收益率排序的前N个因子进行rank相加（等权相加）
    :param num: 前num个
    """
    for num in range(1, num+1):
        combine_list = range(num)
        combine_dict.update({num: combine_list})

    for combine_num in combine_dict.keys():
        combine_dict[combine_num] = list(map(lambda x: factor_list[x], combine_dict[combine_num]))

    # 记录因子名称与组合对应的记录表
    df_factor_record = pd.DataFrame(index=range(1,21), columns=['因子序列'])
    for combine_num in combine_dict.keys():
        combine_list = combine_dict[combine_num]
        factors = combine_list
        ffactor_name = 'topN_ffactor_%d' % combine_num
        print(ffactor_name, ','.join(combine_list))
        df_factor_record.loc[combine_num]['因子序列'] = ','.join(combine_list)
        if os.path.exists(factor_top_n_output_path + ffactor_name + '.h5'):
            print(ffactor_name, '已存在')
            continue
        # 开始计算组合因子
        first_factor = factors[0]
        res = pd.read_hdf(factor_rank_input_path + first_factor + '.h5', first_factor)
        if combine_num > 1:
            index, columns = res.index, res.columns
            res = frame2arr(res)
            for factor in factors[1:]:
                res += frame2arr(pd.read_hdf(factor_rank_input_path + factor + '.h5', factor))
            res = arr2frame(res, index, columns)
        res.to_hdf(factor_top_n_output_path + ffactor_name + '.h5', ffactor_name)
    return df_factor_record

# 解锁开始计算所有原始日内因子的rank排名
if __name__ == "__main__":
    # df_factor_record = combine_top_n(factor_list, 20)
    # df_factor_record.to_excel(factor_result_analysis_output_path + '因子组合-topN对应表.xlsx')
    df_factor_record = get_combinations(factor_list) #13:35
    df_factor_record.to_excel(factor_result_analysis_output_path + '因子组合-全组合对应表.xlsx')

    # get_all_rank() # 获取所有因子的rank值，只需运行一次，一劳永逸