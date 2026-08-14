import pandas as pd
import numpy as np
import NeptuneFinanceFactorTest
from tqdm import tqdm
from multiprocessing import Pool

all_factor_inf = pd.read_excel('/data/user/023859/factor_zooZZ/all_factor_inf.xlsx')
all_factor_inf = all_factor_inf[all_factor_inf['factor_type'].str.contains('xdb_balancesheet|xdb_cashflow|xdb_income')]

factors = list(all_factor_inf['factor_name'])

def calc_IC_score(factor):
    res_df = pd.DataFrame(index=['IC', 'score'], columns=[factor])
    factor_df = pd.read_hdf(f'/data/user/023859/factor_zooZZ/all_factor/931/{factor}/{factor}.h5')
    FT = NeptuneFinanceFactorTest.FactorTest(20170110, 20201231)
    res = FT.factor_test(factor_df, [np.nan], '/data/user/023859/factor_test_research/factor_test/')
    score = res['check_score_res'].loc['score', 'tot_score']
    res_df.loc['score', factor] = score
    IC = res['corr_sta'].loc['corr_tot', 'value']
    res_df.loc['IC', factor] = IC
    return res_df

with Pool(processes=24) as pool:
    results = pool.starmap(calc_IC_score,[(factor,) for factor in factors])

result_df = pd.concat(results,axis=1)
print(result_df.loc['score'].mean())
print(result_df.loc['IC'].abs().mean())
print(results)
# df_in = pd.read_pickle('/dfs/user/023859/neptune/sft_finance.pkl').loc[:pd.Timestamp('20201231')]
# df_out = pd.read_pickle('/dfs/user/023859/neptune/sft_finance.pkl').loc[pd.Timestamp('20210101'):]
#
# df_factors_in = df_in.drop(columns=['list_len','STPT','Circu_Mkt','last_close_is_zt','last_close_is_dt','label_s1_short','label_s1_mid','label_s1_long','first_after_financedate'])
# df_factors_out = df_out.drop(columns=['list_len','STPT','Circu_Mkt','last_close_is_zt','last_close_is_dt','label_s1_short','label_s1_mid','label_s1_long','first_after_financedate'])
#
# df_in_ = df_in[df_in['first_after_financedate'] == 1]
# df_out_ = df_out[df_out['first_after_financedate'] == 1]
#
# res_in = df_factors_in.rank().corrwith(df_in['label_s1_short'].rank())
# res_in_ = df_factors_in.rank().corrwith(df_in_['label_s1_short'].rank())
# res_out = df_factors_out.rank().corrwith(df_out['label_s1_short'].rank())
# res_out_ = df_factors_out.rank().corrwith(df_out_['label_s1_short'].rank())
#
# print(res_in.abs().mean())
# print(res_in_.abs().mean())
# print(res_out.abs().mean())
# print(res_out_.abs().mean())