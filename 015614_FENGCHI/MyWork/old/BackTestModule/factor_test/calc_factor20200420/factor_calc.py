# coding: utf-8
# Author：fengchi863
# Date ：2020/4/20 14:36
'''
0420这一个迭代的版本因为一些原因出现了问题，导致测试作废
'''
import pandas as pd, numpy as np
from multiprocessing import Pool
import itertools
from dataApi.getData import *
from dataApi.stockList import *
from dataApi.usefulTools import *
from tqdm import tqdm

output_root_path = '/data/group/800319/junkData/temp_factor_by_fc/StrategyBackTest/strats_append_with_defalt_factor_20200420/'
factor_root_path = '/data/group/800319/storeFactor/'

start_date = 20170103
end_date = 20191231
date_list = get_date_range(start_date, end_date)

stock_pool = clean_stock_list('COMMON')
stock_list = clean_stock_list(no_limit_down=True, no_limit_up=True).shift(1).reindex(date_list)
stock_list = (stock_list > 0.5) & (
            stock_pool.shift(1).reindex_like(stock_list) > 0.5) if stock_pool is not None else stock_list
stock_list = stock_list.reindex(columns=sorted(stock_list.sum()[stock_list.sum() > 0.5].index.tolist()))

def calc_qrr():
    vol = get_minute_1factor('vol', start_date, end_date, code_list=stock_list.columns.tolist())

    index, columns = vol.index, vol.columns
    vol = frame2arr(vol)
    qrr = ts_mean(vol, 5) / ts_mean(vol, 20)

    factor_name_list = 'boll3	alpha123	boll4	alpha23	alpha184	boll6	factor_dev02	boll5	alpha56	factor119	alpha16	factor_dev08	alpha168	boll7	alpha46	alpha153	alpha17	factor78	alpha52	alpha40	boll8	factor110	factor83	factor64	factor98	alpha31	alpha7	alpha13	alpha145	alpha9	factor74	alpha36	alpha18	factor_dev05	alpha126_2	factor91	factor99	factor105	alpha32	alpha47	alpha179	alpha41	factor101	factor69	factor_dev07	factor62	alpha19	alpha11	alpha45	alpha142	factor113	alpha181	factor68	factor72	alpha29	alpha191	alpha171	factor61	alpha151	alpha166	alpha5	alpha21	alpha35	factor90	alpha178	alpha48	alpha50	alpha14	alpha37	alpha3	alpha163	alpha42	factor63	alpha28	alpha1	alpha147	factor114	alpha135	boll10	factor_dev03	alpha25	alpha49	factor73	alpha176	alpha38	alpha22	alpha24	alpha139	alpha39	factor71	alpha141	alpha12	alpha59	alpha122	alpha134	factor118	factor112	alpha8	boll9	factor116	alpha6	boll12	alpha169	boll11	factor86	factor94	factor106	factor106	factor107	alpha43	alpha133_1	alpha156	factor92	alpha27'
    factor_name_list = factor_name_list.split('\t')

    bar = tqdm(factor_name_list)

    for factor in bar:
        bar.set_description(factor)
        if os.path.exists(factor_root_path + factor + '.h5'):
            factor_df = pd.read_hdf(factor_root_path + factor + '.h5', factor)
        else:
            factor_df = pd.read_hdf(factor_root_path + factor + ' .h5', factor + ' ')
        factor_arr = frame2arr(factor_df)
        combine_factor = factor_arr * qrr
        combine_factor = arr2frame(combine_factor, index, columns)
        combine_factor.to_hdf(factor_root_path + 'qrr_combine_factor20200420/' + factor + '.h5', factor)

def calc_ffactor():
    factor_name_list = ['boll3','alpha123','alpha23','boll6','alpha56','alpha16']
    combine_list_2 = list(itertools.combinations([0,1,2,3,4,5], 2))
    combine_list_3 = list(itertools.combinations([0,1,2,3,4,5], 3))
    for combine_way in combine_list_2:
        target1, target2 = combine_way
        factor_name1, factor_name2 = factor_name_list[target1], factor_name_list[target2]

        if os.path.exists(factor_root_path + factor_name1 + '.h5'):
            factor1 = pd.read_hdf(factor_root_path + factor_name1 + '.h5', factor_name1)
        else:
            factor1 = pd.read_hdf(factor_root_path + factor_name1 + ' .h5', factor_name1 + ' ')

        if os.path.exists(factor_root_path + factor_name2 + '.h5'):
            factor2 = pd.read_hdf(factor_root_path + factor_name2 + '.h5', factor_name2)
        else:
            factor2 = pd.read_hdf(factor_root_path + factor_name2 + ' .h5', factor_name2 + ' ')

        index, columns = factor1.index, factor1.columns

        factor1 = frame2arr(factor1)
        factor2 = frame2arr(factor2)

        factor1_rank = cross_rank(factor1)
        factor2_rank = cross_rank(factor2)

        factor_combine = factor1_rank + factor2_rank
        factor_combine = arr2frame(factor_combine, index, columns)
        factor_combine.to_hdf(factor_root_path + 'combine_ffactor20200421/%s_%s_rank_sum' % (factor_name1, factor_name2) + '.h5', \
                              '%s_%s_rank_sum' % (factor_name1, factor_name2))
        print('%s_%s_rank_sum' % (factor_name1, factor_name2))

    for combine_way in combine_list_3:
        target1, target2, target3 = combine_way
        factor_name1, factor_name2, factor_name3 = \
            factor_name_list[target1], factor_name_list[target2], factor_name_list[target3]

        if os.path.exists(factor_root_path + factor_name1 + '.h5'):
            factor1 = pd.read_hdf(factor_root_path + factor_name1 + '.h5', factor_name1)
        else:
            factor1 = pd.read_hdf(factor_root_path + factor_name1 + ' .h5', factor_name1 + ' ')

        if os.path.exists(factor_root_path + factor_name2 + '.h5'):
            factor2 = pd.read_hdf(factor_root_path + factor_name2 + '.h5', factor_name2)
        else:
            factor2 = pd.read_hdf(factor_root_path + factor_name2 + ' .h5', factor_name2 + ' ')

        if os.path.exists(factor_root_path + factor_name3 + '.h5'):
            factor3 = pd.read_hdf(factor_root_path + factor_name3 + '.h5', factor_name3)
        else:
            factor3 = pd.read_hdf(factor_root_path + factor_name3 + ' .h5', factor_name3 + ' ')

        index, columns = factor1.index, factor1.columns

        factor1 = frame2arr(factor1)
        factor2 = frame2arr(factor2)
        factor3 = frame2arr(factor3)

        factor1_rank = cross_rank(factor1)
        factor2_rank = cross_rank(factor2)
        factor3_rank = cross_rank(factor3)

        factor_combine = factor1_rank + factor2_rank + factor3_rank
        factor_combine = arr2frame(factor_combine, index, columns)
        factor_combine.to_hdf(
            factor_root_path + 'combine_ffactor20200421/%s_%s_%s_rank_sum' % (factor_name1, factor_name2, factor_name3) + '.h5', \
            '%s_%s_%s_rank_sum' % (factor_name1, factor_name2, factor_name3))
        print('%s_%s_%s_rank_sum' % (factor_name1, factor_name2, factor_name3))

if __name__=="__main__":
    calc_ffactor()