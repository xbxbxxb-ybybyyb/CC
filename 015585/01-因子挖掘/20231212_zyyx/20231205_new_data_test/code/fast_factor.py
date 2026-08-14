import os
import pandas as pd
import numpy as np
from function_factor import *
from xquant.factordata import FactorData
import IO
from itertools import product
print('开始市场热度因子碰撞性测试')
dic_diff =  {
    'diff':f_pro_diff,
    # 'nodiff':f_pro_nodiff,
}
# rolling范围
list_rolling_days = [1,5,20]
# rolling时的筛选方式
dic_rolling_filter = {
                      'nofilter':f_roll_filter_nofilter,
                      'up1':f_roll_filter_up1,
                      'down1':f_roll_filter_down1,
                     }
# rolling计算函数
dic_calc = {
            'max':f_calc_max,
            'min':f_calc_min,
            'avg':f_calc_avg,
            'linearavg':linear_mean,
            # 'med':f_calc_med,
            'cv':f_calc_cv,
            # 'sum':f_calc_sum,
            'cct':f_calc_cct,
            'skew':f_calc_skew,
            'kurt':f_calc_kurt,
            'change':f_calc_change,
            'm2m':f_calc_m2m,
            'pos':f_calc_pos,
            'std':f_calc_std
           }
# 标准化函数：rank/zscore/no
dic_std = {'rank':f_std_rank,
           'zscore':f_std_zscore,
           # 'nostd':f_std_nostd
           }
# combo函数：加减乘除
dic_combo = {
             'add':f_combo_add,
             'minus':f_combo_minus,
             # 'multi':f_combo_multi,
             # 'div':f_combo_div
             }
# 主体函数，在预先准备好df_ori的基础上
def generate_factor(df_ori,
                    diff_ind,
                    diff_ins,
                    rolling_filter_ind,
                    rolling_filter_ins,
                    rolling_days_ind,
                    rolling_days_ins,
                    calc_ind,
                    calc_ins,
                    std_ind,
                    std_ins,
                    combo
                    ):
    # 是否算增长率
    df_ori_ind = dic_diff[diff_ind](df_ori.copy(),'ind')
    df_ori_ins = dic_diff[diff_ins](df_ori.copy(),'ins')
    # 是否rolling时筛选
    df_ori_rolling_filter_ind = dic_rolling_filter[rolling_filter_ind](df_ori_ind.copy(),'ind')
    df_ori_rolling_filter_ins = dic_rolling_filter[rolling_filter_ins](df_ori_ins.copy(),'ins')
    # rolling范围
    if rolling_days_ind>1:
        if calc_ind != 'linearavg':
            df_ori_rolling_ind = pd.DataFrame(df_ori_rolling_filter_ind['factor'].unstack()\
                .rolling(rolling_days_ind,1).apply(lambda x : dic_calc[calc_ind](x)).stack())
            df_ori_rolling_ind.columns = ['factor']
        else:
            df_ori_rolling_ind = pd.DataFrame(linear_mean(df_ori_rolling_filter_ind['factor'].unstack(),rolling_days_ind).stack())
            df_ori_rolling_ind.columns = ['factor']
    else:
        df_ori_rolling_ind = df_ori_rolling_filter_ind[['factor']]
    if rolling_days_ins>1:
        if calc_ins != 'linearavg':
            df_ori_rolling_ins = pd.DataFrame(df_ori_rolling_filter_ins['factor'].unstack()\
                .rolling(rolling_days_ins,1).apply(lambda x : dic_calc[calc_ins](x)).stack())
            df_ori_rolling_ins.columns = ['factor']
        else:
            df_ori_rolling_ins = pd.DataFrame(linear_mean(df_ori_rolling_filter_ins['factor'].unstack(),rolling_days_ins).stack())
            df_ori_rolling_ins.columns = ['factor']
    else:
        df_ori_rolling_ins = df_ori_rolling_filter_ins[['factor']]
    # rank or zscore
    df_std_ind = dic_std[std_ind](df_ori_rolling_ind)
    df_std_ind.columns = ['factor_ind']
    df_std_ins = dic_std[std_ins](df_ori_rolling_ins)
    df_std_ins.columns = ['factor_ins']
    #
    res_df = pd.merge(df_std_ind,df_std_ins,left_index=True,right_index=True)
    res = dic_combo[combo](res_df)
    return res
#预先准备好测试函数和基础数据
start_date = 20201105
end_date = 20231130
s = FactorData()
df_ori = pd.read_pickle('/data/user/015585/01-因子挖掘/20231205_new_data_test/test_data_2023.pkl')
df_ori.columns = ['dt','Ticker','ins','ind']
df_ori['dt'] = df_ori['dt'].apply(lambda x : pd.Timestamp(str(x)))
df_ori['ins'] = df_ori['ins'].astype(float)
df_ori['ind'] = df_ori['ind'].astype(float)
df_ori = df_ori.set_index(['dt','Ticker'])
df_ori = df_ori.sort_values(['dt','Ticker'])
df_wind_ori = IO.read_data([start_date, end_date],
                      columns=['pct_chg'],
                      alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')

tmp_test = []
# for diff_ind,diff_ins,rolling_filter_ind,rolling_filter_ins,rolling_days_ind,rolling_days_ins,\
#     calc_ind,calc_ins,std_ind,std_ins,combo\
#     in product(dic_diff,dic_diff,dic_rolling_filter,dic_rolling_filter,list_rolling_days,list_rolling_days,
#                dic_calc,dic_calc,dic_std,dic_std,dic_combo):
def calc_factor(diff_ind,diff_ins,rolling_filter_ind,rolling_filter_ins,rolling_days_ind,rolling_days_ins,calc_ind,calc_ins,std_ind,std_ins,combo):
    factor_name = 'ind-{}_{}_{}_{}_{}-ins-{}_{}_{}_{}_{}-{}'.format(diff_ind,rolling_filter_ind,rolling_days_ind,calc_ind,std_ind,
                                                                 diff_ins,rolling_filter_ins,rolling_days_ins,calc_ins,std_ins,
                                                                    combo)
    tmp_test.append(factor_name)
    if (rolling_days_ins == 1) & (calc_ins != 'max'): # 回溯1天且非相除，不涉及calc
        return
    if (rolling_days_ind == 1) & (calc_ind != 'max'): # 回溯1天且非相除，不涉及calc
        return
    # if factor_name != 'ind-diff_nofilter_20_linearavg_zscore-ins-diff_nofilter_20_linearavg_zscore-minus':
    #     return
    print(factor_name)
    df_factor = generate_factor(df_ori.copy(),
                            diff_ind,
                            diff_ins,
                            rolling_filter_ind,
                            rolling_filter_ins,
                            rolling_days_ind,
                            rolling_days_ins,
                            calc_ind,
                            calc_ins,
                            std_ind,
                            std_ins,
                            combo
                            )
    df_factor.columns = [factor_name]
    df_wind = df_wind_ori.copy()
    df_wind[factor_name] = df_factor[factor_name].unstack().shift(2).stack()
    # IC 和 首末组的平均每日收益率
    res_factor = {}
    res_factor['IC'] = df_wind.groupby('dt').apply(lambda x : x.corr(method = 'spearman').iloc[0,1]).mean()
    df_wind['rank'] = rank_(df_wind[factor_name])
    res_factor['0.9-1'] = df_wind[df_wind['rank']>=0.9]['pct_chg'].groupby('dt').mean().mean()
    res_factor['0-0.1'] = df_wind[df_wind['rank']<=0.1]['pct_chg'].groupby('dt').mean().mean()
    print(res_factor)
    save_pickle(res_factor, save_path='/dfs/user/015585/20240408-市场热度因子测试/res_20240408/{}.pkl'.format(factor_name))
from joblib import Parallel, delayed
factor_df_list = Parallel(n_jobs=16)(delayed(calc_factor)(diff_ind,diff_ins,rolling_filter_ind,rolling_filter_ins,rolling_days_ind,rolling_days_ins,calc_ind,calc_ins,std_ind,std_ins,combo)
                                     for diff_ind,diff_ins,rolling_filter_ind,rolling_filter_ins,rolling_days_ind,rolling_days_ins,calc_ind,calc_ins,std_ind,std_ins,combo
                                     in product(dic_diff,dic_diff,dic_rolling_filter,dic_rolling_filter,list_rolling_days,list_rolling_days,
                                                dic_calc,dic_calc,dic_std,dic_std,dic_combo))