import pandas as pd
import numpy as np
import psmatching.match as psm
from multiprocessing import Pool
from statsmodels.tools.sm_exceptions import PerfectSeparationError
import os
import warnings
warnings.filterwarnings('ignore')

# 因子标准化
def factor_normalization(data, factors):
    for factor in factors:
        mu = data[factor].mean()
        std = data[factor].std()
        data[factor] = (data[factor] - mu) / std
    return data

def calc_single_factor_causal_effect(begin_date, end_date, data, basic_factors, factor, label, dataset):
    np.random.seed(0) # 进行倾向得分匹配时，若多个对照组样本均能和处理组样本匹配，算法会随机选择一个样本进行匹配，故设置随机种子保证结果可复现
    data_train_factor = data[[factor]+[label]+basic_factors]
    if data_train_factor[factor].corr(data_train_factor[label],method='spearman')>0:
        data_train_factor['CASE'] = data_train_factor[factor] >= np.quantile(data_train_factor[factor],0.65)
    else:
        data_train_factor['CASE'] = data_train_factor[factor] <= np.quantile(data_train_factor[factor],0.35)
    if np.mean(data_train_factor['CASE']) > 0.5:
        data_train_factor['CASE'] = ~data_train_factor['CASE']
    data_train_factor = data_train_factor.reset_index(drop=True)
    data_train_factor['OPTUM_LAB_ID'] = data_train_factor.index
    folder_name =  f'/data/user/023859/factor_framework_analysis/Europa/psm/{dataset}_{label}_{begin_date}_{end_date}'
    os.makedirs(folder_name, exist_ok = True)
    path = folder_name + f'/psm_train_data_1_{factor}.csv'
    data_train_factor.to_csv(path, index=False)
    formu = 'CASE~'+'+'.join(basic_factors)
    k = '1'
    try:
        model = psm.PSMatch(path,formu,k)
        model.prepare_data()
        model.match(caliper=None,replace=False)
        matched_data = model.matched_data.reset_index()
        if np.mean(data_train_factor['CASE']) > 0.5:
            res = -1*matched_data.groupby('CASE').agg({'OPTUM_LAB_ID':np.size,label:np.mean})[label].diff().iloc[-1]
        else:
            res = matched_data.groupby('CASE').agg({'OPTUM_LAB_ID': np.size, label: np.mean})[label].diff().iloc[-1]
    except PerfectSeparationError:
        res = np.nan

    return factor, res

def factors_filter(correlation_matrix,correlation_threshold, causal_effects, causal_threshold=0.0025):
    importance_df = pd.Series(causal_effects).sort_values(ascending=False)
    selected_factors = set()
    discarded_factors = set()
    for factor in importance_df.index:
        if factor in discarded_factors:
            continue
        selected_factors.add(factor)
        high_correlation_factors = correlation_matrix.index[abs(correlation_matrix[factor]) > correlation_threshold].tolist()
        for correlated_factor in high_correlation_factors:
            if correlated_factor != factor:
                discarded_factors.add(correlated_factor)
    factors_filtered = list(selected_factors)
    importance_df = importance_df[importance_df.index.isin(factors_filtered)]
    factors_selected = list(importance_df[importance_df >= importance_df.quantile(0.45)].index)

    return factors_selected

if __name__ == '__main__':
    periods = [('20160101','20200229'),('20160101','20200831')]
    datasets = ['20240828_label_px','20240828_no2_industry2', '20240828_no_under3_market']
    labels = ['label_pct_graded','label_p5_graded','label_p7_graded']
    basic_factors = ['saturn_Flag_SH_SZ','saturn_dt_last_zt_1','saturn_lzt_day_pattern','saturn_free_turn','saturn_t930_T_o2pre','saturn_Circu_Mkt','saturn_pre_close','saturn_t931_pct_sss_ZT_Time_ms','saturn_t931_pct_sss_t_o2pre','saturn_t931_pct_last_buy_rise']
    basic_factors = ['pre_close', 'Flag_SH_SZ', 'pct_20', 'freeturn', 'high_before20', 'ul_price', 'Circu_Mkt','EFS_pct5_T1', 'hml_factor', 'sss_ZT_Time_ms', 'sss_t_o2pre']
    correlation_threshold = 0.7
    for dataset in datasets:
        if dataset == '20240828_label_px':
            data = pd.read_pickle('/data/group/800463/sunss/europa/20240828_label_px/factor_df_all_20160101_20210228.pkl')
            factors_info = pd.read_excel('/data/group/800463/sunss/europa/20240828_label_px/factor_bank_inf_all_period.xlsx')
        if dataset == '20240828_no2_industry2':
            data = pd.read_pickle('/data/group/800463/sunss/europa/20240828_label_px/factor_df_no2_industry2_20160101_20210228.pkl')
            factors_info = pd.read_excel('/data/group/800463/sunss/europa/20240828_label_px/factor_bank_inf_no2_industry2_period.xlsx')
        if dataset == '20240828_no_under3_market':
            data = pd.read_pickle('/data/group/800463/sunss/europa/20240828_label_px/factor_df_no_under3_market_20160101_20210228.pkl')
            factors_info = pd.read_excel('/data/group/800463/sunss/europa/20240828_label_px/factor_bank_inf_no_under3_market_period.xlsx')
        factors_available = list(factors_info[~factors_info['factor_type'].isin(['other', 'label'])].factor_name)
        factors_available = list(set(factors_available) - set(basic_factors))
        for period in periods:
            begin_date = period[0]
            end_date = period[1]
            data_train = data[data.index.get_level_values(0)<=end_date]
            normalized_data = factor_normalization(data_train, factors_available + basic_factors)
            for label in labels:
                with Pool(processes=10) as pool:
                    results = pool.starmap(calc_single_factor_causal_effect,[(begin_date, end_date, normalized_data, basic_factors, factor, label, dataset) for factor in factors_available])

                causal_effects = {}
                for result in results:
                    causal_effects[result[0]] = result[1]

                correlation_matrix = data_train[factors_available].rank().corr()
                factors_selected = factors_filter(correlation_matrix, correlation_threshold, causal_effects)

                factors_info['select'] = 0
                factors_info.loc[factors_info['factor_name'].isin(factors_selected), 'select'] = 1
                factors_info.loc[factors_info['factor_name'].isin(basic_factors), 'select'] = 1
                factors_info.loc[factors_info['factor_type'].isin(['label', 'other']), 'select'] = 0
                factors_info.to_excel(f'/data/user/023859/factor_framework_analysis/Europa/{dataset}/fsci_{label}_{begin_date}_{end_date}.xlsx', index=False)