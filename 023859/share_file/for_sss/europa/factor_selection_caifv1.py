import pandas as pd
import numpy as np
import psmatching.match as psm
import warnings
warnings.filterwarnings('ignore')

data = pd.read_pickle('/data/user/018107/share_file/for_tsq/europa/20240630/factor_df_all_20160101_20191130.pkl')
factors_info_all = pd.read_excel('/data/user/018107/share_file/for_tsq/europa/20240630/factor_bank_inf_all.xlsx')
factors_info = pd.read_excel('/data/user/018107/share_file/for_tsq/europa/20240630/factor_bank_inf_all_period.xlsx')
factors_all = list(factors_info[~factors_info['factor_type'].isin(['other', 'label'])].factor_name)

causal_effects_train = {}
for factor in factors_all:
    try:
        data_train_factor = data[[factor,'label_pct_graded','T_o2pre','ZT_Time','high_price','trigger_price','pre_close','list_len',
                                  'float_shares','Flag_SH_SZ','pre_float_shares','after_not_ul_len']]
        if data_train_factor[factor].corr(data_train_factor['label_pct_graded'],method='spearman')>0:
            data_train_factor['CASE'] = data_train_factor[factor] >= np.quantile(data_train_factor[factor],0.65)
        else:
            data_train_factor['CASE'] = data_train_factor[factor] <= np.quantile(data_train_factor[factor],0.35)
        if np.mean(data_train_factor['CASE']) > 0.5:
            data_train_factor['CASE'] = ~data_train_factor['CASE']
            data_train_factor = data_train_factor.reset_index(drop=True)
            data_train_factor['OPTUM_LAB_ID'] = data_train_factor.index
            data_train_factor.to_csv('/data/user/023859/factor_framework_analysis/Europa/psm_train_data_1.csv',index=False)
            path = '/data/user/023859/factor_framework_analysis/Europa/psm_train_data_1.csv'
            formu = 'CASE ~ T_o2pre+ZT_Time+high_price+trigger_price+pre_close+list_len+float_shares+Flag_SH_SZ+pre_float_shares+after_not_ul_len'
            k = '1'
            model = psm.PSMatch(path,formu,k)
            model.prepare_data()
            model.match(caliper=None,replace=False)
            matched_data = model.matched_data.reset_index()
            causal_effects_train[factor] = -1*matched_data.groupby('CASE').agg({'OPTUM_LAB_ID':np.size,'label_pct_graded':np.mean})['label_pct_graded'].diff().iloc[-1]
        else:
            data_train_factor = data_train_factor.reset_index(drop=True)
            data_train_factor['OPTUM_LAB_ID'] = data_train_factor.index
            data_train_factor.to_csv('/data/user/023859/factor_framework_analysis/Europa/psm_train_data_1.csv',index=False)
            path = '/data/user/023859/factor_framework_analysis/Europa/psm_train_data_1.csv'
            formu = 'CASE ~ T_o2pre+ZT_Time+high_price+trigger_price+pre_close+list_len+float_shares+Flag_SH_SZ+pre_float_shares+after_not_ul_len'
            k = '1'
            model = psm.PSMatch(path,formu,k)
            model.prepare_data()
            model.match(caliper=None,replace=False)
            matched_data = model.matched_data.reset_index()
            causal_effects_train[factor] = matched_data.groupby('CASE').agg({'OPTUM_LAB_ID':np.size,'label_pct_graded':np.mean})['label_pct_graded'].diff().iloc[-1]
    except:
        causal_effects_train[factor] = np.nan

correlation_matrix_train = data[factors_all].corr(method='spearman')
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