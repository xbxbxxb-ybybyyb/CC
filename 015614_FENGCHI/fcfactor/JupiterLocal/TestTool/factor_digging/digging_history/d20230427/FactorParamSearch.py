# coding: utf-8
# Author：fengchi863
# Date ：2023/4/6 15:09
import pandas as pd
from JupiterLocal.TestTool.test1_factor_demo import strongFactorTest
from JupiterLocal.TestTool.run_factor_demo import run_factor
import IO
from multiprocessing import Pool
from itertools import product
from xquant.factordata import FactorData
from datetime import datetime
import os
from tqdm import tqdm
import numpy as np
s = FactorData()

def array_corr_np(x, y):
    x[np.isnan(x) | np.isnan(y)] = np.nan
    y[np.isnan(x) | np.isnan(y)] = np.nan
    d_x, d_y = x - np.nanmean(x, axis=0), y - np.nanmean(y, axis=0)
    cov = np.nanmean(d_x * d_y, axis=0)
    var = (np.nanvar(x, axis=0) * np.nanvar(y, axis=0)) ** 0.5
    return cov / var

def array_rcorr_np(x, y):
    rank_x = np.argsort(np.argsort(x, axis=0), axis=0)
    rank_y = np.argsort(np.argsort(y, axis=0), axis=0)
    d_x, d_y = rank_x - np.nanmean(rank_x, axis=0), rank_y - np.nanmean(rank_y, axis=0)
    cov = np.nanmean(d_x * d_y, axis=0)
    var = (np.nanvar(rank_x, axis=0) * np.nanvar(rank_y, axis=0)) ** 0.5
    return cov / var

def multiprocess(kernal_num, func, iterable, *args):
    pool = Pool(kernal_num)
    print('多进程启动')
    pool_apply_async = {}
    parts = len(iterable) // kernal_num
    remainder = len(iterable) % kernal_num
    iter_start = 0
    for j in range(kernal_num):
        if remainder > 0:
            iter_end = iter_start + parts + 1
            remainder = remainder - 1
        else:
            iter_end = iter_start + parts
        sub_iter = iterable[iter_start: iter_end]
        pool_apply_async[j] = pool.apply_async(func, (sub_iter,) + args)
        iter_start = iter_end
    pool.close()
    pool.join()
    print('多进程结束')
    return pool_apply_async


class FactorParamSearch:
    def __init__(self, note=None):
        self.start_date = 20160101
        self.end_date = 20191231
        note = note
        self.basic_file_path = '/data/group/800463/data/project1_public/factor_lib_v2/Basic_zt_001.h5'

        cur_datetime = datetime.today().strftime('%Y%m%d%H%M%S')
        self.res_path = f'/data/user/015614/factor/factor_digging_{cur_datetime}_{note}/'
        os.makedirs(self.res_path)

    def wrapper(self, param_list):
        for param_tuple in tqdm(param_list):
            factor_name = str(param_tuple)
            # TODO: 第三个参数因子类型需要根据回测需求进行更改
            factor_df = run_factor(self.calc_factor, factor_name, 'T-1_factor',
                           self.start_date, self.end_date, self.basic_file_path, self.res_path, param_tuple=param_tuple, interval_res=False)
            # factor_df = self.calc_factor(self.start_date, self.end_date, param_tuple) # 这个计算出来的因子有问题，比如没有填充、没有平移
            self.start_backtest(factor_df, param_tuple)

    def start_backtest(self, factor_df, param_tuple):
        bt_columns = ['nan_num', 'same_rate', 'value_diff_score', 'value_stability_score', 'mixed_diff_score',
                      'mixed_stability_score', 'score', 'corr_tot', 'mic_tot', 'high_corr_factor', 'high_corr_factor_corr']
        res_df = pd.DataFrame(columns=bt_columns)

        sft = strongFactorTest(self.start_date, self.end_date)
        res_dict = sft.factor_test(factor_df, result_path=self.res_path, factor_corr_test=True, generate_pdf=True)

        nan_num = res_dict['factor_information'].loc['Nan|Inf Count', 'Factor Info']
        same_rate = res_dict['other_sta'].loc['', 'same_rate']
        value_diff_score = res_dict['check_score_res'].loc['score', 'value_diff_score']
        value_stability_score = res_dict['check_score_res'].loc['score', 'value_stability_score']
        mixed_diff_score = res_dict['check_score_res'].loc['score', 'mixed_diff_score']
        mixed_stability_score = res_dict['check_score_res'].loc['score', 'mixed_stability_score']
        score = res_dict['check_score_res'].loc['score', 'tot_score']
        corr_tot = res_dict['corr_sta'].loc['corr_tot', 'value']
        mic_tot = res_dict['corr_sta'].loc['mic_tot', 'value']

        high_corr_s = res_dict['factor_corr'].query('factor_corr >= 0.7')
        if len(high_corr_s) == 0:
            high_corr_s = res_dict['factor_corr'].iloc[:2]
        else:
            high_corr_s = res_dict['factor_corr'].iloc[:len(high_corr_s) + 2]

        high_corr_factor_list_str = '，'.join(high_corr_s.index.tolist())
        high_corr_factor_corr_list_str = '，'.join(high_corr_s['factor_corr'].map(lambda x: round(x, 4)).map(str).tolist())

        res_df.loc[str(param_tuple)] = [nan_num, same_rate, value_diff_score, value_stability_score,
                                   mixed_diff_score, mixed_stability_score, score, corr_tot, mic_tot, high_corr_factor_list_str, high_corr_factor_corr_list_str]
        print(str(param_tuple), ': ', score)
        res_df.to_excel(self.res_path + f'{str(param_tuple)}.xlsx')
        factor_df.to_pickle(self.res_path + f'{str(param_tuple)}.pkl')

    @staticmethod
    def calc_factor(start_date, end_date, IO, param_tuple, return_fillna_dic=False):
        # [[param1, param2], [func1, func2, func3], [param1, param2]]
        factor_name = str(param_tuple)

        if return_fillna_dic:
            return {factor_name: 0, 'data': ['MD', 'AIndexEODPrices']}

        param0, func1, param1 = param_tuple

        start_date_ = int(s.tradingday(str(start_date), -250)[0])
        md_data = IO.read_data([start_date_, end_date], columns=['open', 'close', 'pre_close', 'adjfactor']
                               , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
        opn = md_data['open'] * md_data['adjfactor']
        close = md_data['close'] * md_data['adjfactor']
        pre_close = md_data['pre_close'] * md_data['adjfactor']

        index_data = IO.read_data([start_date_, end_date], columns=['S_DQ_CLOSE', 'S_DQ_OPEN']
                                  , alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AIndexEODPrices/AIndexEODPrices.h5')
        index_data = index_data.query(f'Ticker == "{param1}"')
        index_opn = index_data['S_DQ_OPEN']
        index_close = index_data['S_DQ_CLOSE']
        ret = (close - opn) / pre_close

        # 注册制调整
        mask = ret.index.map(lambda x: (x[1][0] == '3' and x[0].strftime('%Y%m%d') >= '20200824') or x[1][:2] == '68')
        ret[mask] = ret[mask] / 2

        ret_market = (index_close - index_opn) / index_close.shift(1)
        ret = ret.unstack().stack(dropna=False)  # 保证所有天的股票数量一致

        # 播放式计算
        factor = pd.DataFrame(index=opn.unstack().columns)
        start_date = s.tradingday(start_date, -1)[0]  # 往前多算一天
        for dat in s.tradingday(start_date, end_date):
            format_dat = pd.to_datetime(dat)
            tmp_ret = ret.loc[:format_dat].unstack()
            tmp_market = ret_market.loc[:format_dat].unstack()

            if func1 == 'corr':
                cov_ret = array_corr_np(tmp_ret.values[-param0:], tmp_market.values.repeat(tmp_ret.shape[1], -1)[-param0:])
            else:
                cov_ret = array_rcorr_np(tmp_ret.values[-param0:], tmp_market.values.repeat(tmp_ret.shape[1], -1)[-param0:])

            factor[format_dat] = cov_ret

        ret = factor.T.stack()
        mad = np.median(ret)
        ret = ret.fillna(mad)   # 默认都填充中位值
        factor_df = pd.DataFrame()
        factor_df[factor_name] = ret

        return factor_df


if __name__ == '__main__':
    note = '修复bug后市场相关性因子&填充中位值&添加新的指数'
    fps = FactorParamSearch(note=note)
    param_list = [[5, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100, 120, 240],  # param0
                  ['corr', 'rank_corr'],
                  ['000852.SH', '000016.SH', '000300.SH', '000001.SH', '000905.SH', '399001.SZ']]  # func1
    # param_list = [[5],  # param0
    #               ['corr']]  # func1
    param_list = list(product(*param_list))
    multiprocess(20, fps.wrapper, param_list)
    # multiprocess(1, fps.wrapper, param_list)
    # fps.wrapper([(5, 'corr')]) # 用于调试

    # check1 = IO.read_data([20160101, 20181231], alt='/data/user/018107/share_file/for_fc/fc_stk_zz1000_r_5.h5')
    # check2 = IO.read_data([20160101, 20181231], alt='/data/user/015614/factor/factor_digging_20230424160441新框架下与市场相关性测试/(5, \'corr\').h5')
    # check3 = IO.read_data([20160101, 20181231], alt='/data/user/015614/factor/factor_digging_20230424204144第二次跑并行测试一致性/(5, \'corr\').h5')
    # cmp = pd.concat([check1, check2], axis=1)
    # check1.mean()
    # check2.mean()