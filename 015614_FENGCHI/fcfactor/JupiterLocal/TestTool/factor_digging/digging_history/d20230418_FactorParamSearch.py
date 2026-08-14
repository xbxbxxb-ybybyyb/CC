# coding: utf-8
# Author：fengchi863
# Date ：2023/4/6 15:09
import pandas as pd
from JupiterLocal.TestTool.test1_factor_demo import strongFactorTest
import IO
from multiprocessing import Pool
from itertools import product
from xquant.factordata import FactorData
from datetime import datetime
import os
s = FactorData()


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
    def __init__(self):
        self.start_date = 20160101
        self.end_date = 20181231

        cur_datetime = datetime.today().strftime('%Y%m%d%H%M%S')
        self.res_path = f'/data/user/015614/factor/factor_digging_{cur_datetime}/'
        os.makedirs(self.res_path)

    def wrapper(self, param_list):
        for param_tuple in param_list:
            factor_df = self.calc_factor(self.start_date, self.end_date, param_tuple)
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
    def calc_factor(start_date, end_date, param_tuple):
        # [[param1, param2], [func1, func2, func3], [param1, param2]]
        param0, param1, func1 = param_tuple

        start_date_ = int(s.tradingday(str(start_date), -250)[0])
        md_data = IO.read_data([start_date_, end_date], columns=['pct_chg'], alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')

        md_data['stock_code'] = md_data.index.get_level_values(1)
        md_data['datelist'] = md_data.reset_index()['dt'].map(lambda x: x.to_pydatetime().strftime('%Y%m%d')).values
        md_data.loc[(md_data['stock_code'].str.startswith('3')) & (md_data['datelist'] >= '20200824'), 'pct_chg'] = md_data.loc[
                                                                                                                        (md_data['stock_code'].str.startswith('3')) & (
                                                                                                                                md_data['datelist'] >= '20200824'), 'pct_chg'] / 2

        flag = md_data['pct_chg'].unstack() > param0
        ret = eval(f'flag.rolling({param1}).{func1}().stack()')

        factor_df = pd.DataFrame()
        factor_df[str(param_tuple)] = ret

        return factor_df


if __name__ == '__main__':

    fps = FactorParamSearch()
    # param_list = [[0.06, 0.07, 0.08, 0.09, 0.098],
    #               [240, 120, 60, 30, 15]]
    param_list = [[0.06, 0.07, 0.08, 0.09, 0.098],    # param0
                  [240, 120, 80, 60, 30, 15, 10, 5, 3], # param1
                  ['std', 'skew', 'kurt', 'sum', 'mean']]  # func1
    param_list = list(product(*param_list))
    multiprocess(24, fps.wrapper, param_list)