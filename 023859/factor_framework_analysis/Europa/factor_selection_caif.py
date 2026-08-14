import pandas as pd
import numpy as np
import psmatching.match as psm
import warnings
warnings.filterwarnings('ignore')

data = pd.read_pickle('/data/user/018107/share_file/for_tsq/europa/20240630/factor_df_all_20160101_20191130.pkl')
factors_info_all = pd.read_excel('/data/user/018107/share_file/for_tsq/europa/20240630/factor_bank_inf_all.xlsx')
factors_info = pd.read_excel('/data/user/018107/share_file/for_tsq/europa/20240630/factor_bank_inf_all_period.xlsx')
factors_all = list(factors_info_all[~factors_info_all['factor_type'].isin(['label'])].factor_name)
factors_available = list(factors_info[~factors_info['factor_type'].isin(['other', 'label'])].factor_name)

for factor in factors_all:
    mu = data[factor].mean()
    std = data[factor].std()
    data[factor] = (data[factor]-mu)/std

basic_factors = ['pre_close','Flag_SH_SZ','pct_20','freeturn','high_before20','ul_price','Circu_Mkt','EFS_pct5_T1','hml_factor','sss_ZT_Time_ms','sss_t_o2pre']
label = 'label_pct_graded'


def calc_causal_effect(data, factor):
    try:
        data_train_factor = data[[factor] + [label] + basic_factors]
        if data_train_factor[factor].corr(data_train_factor[label], method='spearman') > 0:
            data_train_factor['CASE'] = data_train_factor[factor] >= np.quantile(data_train_factor[factor], 0.65)
        else:
            data_train_factor['CASE'] = data_train_factor[factor] <= np.quantile(data_train_factor[factor], 0.35)
        if np.mean(data_train_factor['CASE']) > 0.5:
            data_train_factor['CASE'] = ~data_train_factor['CASE']
            data_train_factor = data_train_factor.reset_index(drop=True)
            data_train_factor['OPTUM_LAB_ID'] = data_train_factor.index
            data_train_factor.to_csv(
                f'/data/user/023859/factor_framework_analysis/Europa/psm/psm_train_data_1_{factor}.csv', index=False)
            path = f'/data/user/023859/factor_framework_analysis/Europa/psm/psm_train_data_1_{factor}.csv'
            formu = 'CASE~' + '+'.join(basic_factors)
            k = '1'
            model = psm.PSMatch(path, formu, k)
            model.prepare_data()
            model.match(caliper=None, replace=False)
            matched_data = model.matched_data.reset_index()
            res = -1 * matched_data.groupby('CASE').agg({'OPTUM_LAB_ID': np.size, label: np.mean})[label].diff().iloc[
                -1]
        else:
            data_train_factor = data_train_factor.reset_index(drop=True)
            data_train_factor['OPTUM_LAB_ID'] = data_train_factor.index
            data_train_factor.to_csv(
                f'/data/user/023859/factor_framework_analysis/Europa/psm/psm_train_data_1_{factor}.csv', index=False)
            path = f'/data/user/023859/factor_framework_analysis/Europa/psm/psm_train_data_1_{factor}.csv'
            formu = 'CASE~' + '+'.join(basic_factors)
            k = '1'
            model = psm.PSMatch(path, formu, k)
            model.prepare_data()
            model.match(caliper=None, replace=False)
            matched_data = model.matched_data.reset_index()
            res = matched_data.groupby('CASE').agg({'OPTUM_LAB_ID': np.size, label: np.mean})[label].diff().iloc[-1]
    except:
        res = np.nan

    return factor, res

if __name__ == '__main__': # 即使在jupyter中这行代码  也必不可少
    warnings.filterwarnings('ignore')
    causal_effects_train = {}
    with Pool(processes=10) as pool:
        results = pool.starmap(calc_causal_effect,[(data, factor) for factor in factors_available])

    for result in results:
        causal_effects_train[result[0]] = result[1]

    correlation_matrix_train = pd.read_pickle('/data/user/023859/factor_framework_analysis/Europa/europa_correlation_matrix_20160101_20191130.pkl')
    correlation_threshold = 0.7
    importance_df = pd.Series(causal_effects_train).sort_values(ascending=False)

    selected_factors = set()
    discarded_factors = set()

    for factor in importance_df.index:
        if factor in discarded_factors:
            continue
        selected_factors.add(factor)
        high_correlation_factors = correlation_matrix_train.index[abs(correlation_matrix_train[factor])>correlation_threshold].tolist()
        for correlated_factor in high_correlation_factors:
            if correlated_factor != factor:
                discarded_factors.add(correlated_factor)
    selected_factors = list(selected_factors)

    factors_selected_by_causal_effect_k1 = list(importance_df[importance_df.index.isin(selected_factors)].index[:363])
    factors_info['select'] = 0
    factors_info.loc[factors_info['factor_name'].isin(factors_selected_by_causal_effect_k1), 'select'] = 1
    factors_info.loc[factors_info['factor_name'].isin(basic_factors), 'select'] = 1
    factors_info.to_excel('/data/user/023859/factor_framework_analysis/Europa/caif_k1_label_pct_graded_20160101_20191130.xlsx',index=False)