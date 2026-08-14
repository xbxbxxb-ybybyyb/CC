# coding: utf-8
# Author：fengchi863
# Date ：2022/11/23 16:11

"""
研究相较于v1版本引起大回撤的原因

"""
import pandas as pd
from scipy import stats
from tqdm import tqdm

import matplotlib.pyplot as plt
import pandas as pd
import os
import seaborn as sns

from LucienUtil.FileUtil import FileUtil
from Zeus.Europa.v1_0_16.path_conf import saturn_data_test_fpath, factor_path, filter_factor_fpath, junk_path

root_path = '/data/user/015614/shared/backtest_result/20221120回测结果_Europa_fac_20221116三个区间上回测结果汇总/'
xgb_imptc_df = pd.read_excel(filter_factor_fpath, index_col=0).set_index('factor_name')

period1_test = '20191002~20200630_Europa_fac_20221116_FSRS_all_pct_graded_all_merge_test_模型评价_20221120.xlsx'
period2_test = '20200401~20201231_Europa_fac_20221116_FSRS_all_pct_graded_all_merge_test_模型评价_20221120.xlsx'
period3_test = '20201001~20210630_Europa_fac_20221116_FSRS_all_pct_graded_all_merge_test_模型评价_20221120.xlsx'
period1_fit = '20200701~20201231_Europa_fac_20221116_FSRS_all_pct_graded_all_merge_fit_模型评价_20221121.xlsx'
period2_fit = '20210101~20210630_Europa_fac_20221116_FSRS_all_pct_graded_all_merge_fit_模型评价_20221121.xlsx'
period3_fit = '20210701~20211231_Europa_fac_20221116_FSRS_all_pct_graded_all_merge_fit_模型评价_20221121.xlsx'

bt_res_fpath_list = [period1_test, period1_fit, period2_test, period2_fit, period3_test, period3_fit]
bt_res_name = ['period1_test', 'period1_fit', 'period2_test', 'period2_fit', 'period3_test', 'period3_fit']

res_df = pd.DataFrame(index=['lgb_reg_model'])
plot_output_path = junk_path + '20221124test/'
os.makedirs(plot_output_path, exist_ok=True)
for idx in [4, 5]:  # [1, 4]
    tmp_bt_res_name = bt_res_name[idx]
    res = pd.read_excel(root_path + bt_res_fpath_list[idx], sheet_name='按日', index_col=0)
    profit = res['累计盈亏(扣除成本)_LgbV8FcModel']

    factor = pd.read_pickle(saturn_data_test_fpath)
    label_list = factor.filter(regex='label*').columns.tolist()
    factor = factor.drop(label_list, axis=1)

    # 读取根据重要性选出来的因子
    strategy_name = 'Europa'
    version = 'v1_0_16'
    model_name = 'lgb_reg_model'
    output_path = factor_path + f'{strategy_name}/{model_name}/{version}/'
    selected_factor_list = FileUtil.read_list(output_path, 'factor_list.pkl')

    factor = factor[selected_factor_list]
    factor['trade_date'] = factor.index.get_level_values(0).strftime('%Y%m%d').astype(int).tolist()
    factor_median = factor.groupby('trade_date').median()
    factor_mean = factor.groupby('trade_date').mean()

    factor_median = factor_median.reindex(index=profit.index)
    factor_mean = factor_mean.reindex(index=profit.index)
    corr_df = pd.DataFrame(index=factor_median.columns.tolist(), columns=['factor_median', 'factor_mean'])
    for single_factor in tqdm(factor_median.columns.tolist()):
        corr_df.loc[single_factor, 'factor_median'] = stats.pearsonr(factor_median[single_factor].values, profit.values)[0]
        corr_df.loc[single_factor, 'factor_mean'] = stats.pearsonr(factor_mean[single_factor].values, profit.values)[0]

    high_corr_list = corr_df.applymap(abs).query('factor_median > 0.45').sort_values('factor_median', ascending=False).index.tolist()
    high_corr_list = high_corr_list[:min(len(high_corr_list), 5)]
    print(high_corr_list)
    fig, axes = plt.subplots(1, len(high_corr_list), figsize=(45, 6))  # 第一个参数表示有几行
    for _idx, _factor in enumerate(high_corr_list):
        factor_s = (factor_median[_factor] - factor_median[_factor].min()) / (factor_median[_factor].max() - factor_median[_factor].min())
        profit_s = (profit - profit.min()) / (profit.max() - profit.min())
        factor_s.index = factor_s.index.astype(str)
        profit_s.index = profit_s.index.astype(str)
        factor_s.plot(title=_factor, ax=axes[_idx])
        profit_s.plot(ax=axes[_idx])
    fig.savefig(plot_output_path + f'{idx}.png', bbox_inches='tight', pad_inches=0.1)


# 在第三个test/fit区间上的结果，筛选和收益曲线相关性大于0.45的因子
factor_list2 = ['mf_delp_ma_dsp_max60', 'mf_sl_ms_ss_ms60', 'yzhan_mf_g1_7']    # mf_sl_ms_ss_ms60 yzhan_mf_g1_7
factor_list5 = ['mf_sl_ms_ss_ms60',
                 'mf_dela_d_dsa_min_mean60',
                 'yzhan_mf_f7_7',
                 'Max_cum_one_two_ratio',
                 'mf_sla_d_sma_std60',
                 'mf_bmp_d_sma_range20',
                 'mf_bma_ma_smp_mean20',
                 'mf_bmp_d_sma_mean60',
                 'mf_bmp_d_bsp_max20',
                 'mf_dela_ma_dsa_range5',
                 'yzhan_hf_b11_38',
                 'cnirvl_mean60',
                 'yzhan_taq_f2_10_2_7']
high_corr_hf = pd.DataFrame(index=factor_list2)
check = high_corr_hf.join(xgb_imptc_df)

drop_test = ['cnirvl_mean60', 'mf_delp_ma_dsp_max60', 'mf_bma_ma_smp_mean20', 'mf_sl_ms_ss_ms60', 'mf_bmp_d_bsp_max20']

# factor_list2 = 'EF_profit_coss_ratio_real_3', 'mf_bmp_d_bsp_max20', 'mf_blp_d_bsp_max5', 'ma_compared', \
#                'gtja_alpha_2', 'sundc_t_1_pv_7', 'mf_selp_ma_slp_mean20', 'mf_belp_ma_bela_min_mean20', \
#                'High_small_ratio', 'wd_t_big_pct_max', 'wd_bea_ms_bsa_m5_rank'
# factor_list5 = ['mf_sl_ms_ss_ms60', 'mf_delp_ma_dsp_max60', 'yzhan_mf_g1_7']


