import pandas as pd
import os

strategy='neptune'
factor_version_date = 20250627
factor_check_path = '/data/group/800463/data/projectZZ_public/factor_lib/check_res_tot_neptune.xlsx'
t_factor_path = '/dfs/user/018107/share_file/for_tsq/20250626_zz1000_sa_factor_inf.xlsx'
result_path_local = os.path.join('/dfs/user/023859/neptune',str(factor_version_date))
os.makedirs(result_path_local,exist_ok=True)
result_path_public = f'/data/group/800463/tangsq/neptune/{factor_version_date}'
os.makedirs(result_path_public,exist_ok=True)

# 短周期标签去掉财务因子
factor_type_T_1 = ["['T-1_Factor']","['xdb_tick1m']","['xdb_order1m']"]

# factor_type_T_1 = ["['T-1_Factor']","['xdb_tick1m']","['xdb_order1m']","['xdb_balancesheet_cs']","['xdb_cashflow_cs']","['xdb_income_cs']","['xdb_balancesheet']", "['xdb_cashflow']", "['xdb_income']"]
# 下一个版本需要加因子, 考虑复合因子以及计算高耗时因子
# factor_type_T_1 += ["['T-1_Factor', 'xdb_balancesheet_cs']", "['T-1_Factor', 'xdb_cashflow_cs']", "['xdb_balancesheet_cs', 'xdb_income_cs']"]#, "['xdb_tickex']", "['xdb_trade']"
# 生成大家开发的可用因子列表
all_factor_inf = pd.read_excel('/data/user/023859/factor_zooZZ/all_factor_inf.xlsx')
factors_check_res = pd.read_excel(factor_check_path)
factors_available = factors_check_res[(factors_check_res['pre_check']=='pass')&(factors_check_res['factor_type'].isin(factor_type_T_1))&(factors_check_res['提交时间']<=20250515)]['factor_name'].to_list()

factor_bank_inf = all_factor_inf[all_factor_inf['factor_name'].isin(factors_available)]
factor_bank_inf = factor_bank_inf[['factor_name','factor_owner','factor_type','提交时间','emotion']]
factor_bank_inf['t'] = factor_bank_inf['factor_type'].apply(lambda x: 'T-1' if x in factor_type_T_1 else 'T')
T_1_factor_count = len(factor_bank_inf)
print(f'T-1日因子数：{T_1_factor_count}')

# 来自少森的T日因子
factor_bank_inf_t = pd.read_excel(t_factor_path)
if 't' not in factor_bank_inf_t.columns:
    factor_bank_inf_t['t'] = 'T'
T_factor_count = len(factor_bank_inf_t)
print(f'T日因子数：{T_factor_count}')

# 补充情绪因子
factor_bank_inf_emotion_sc = pd.read_excel('/data/user/023859/factor_zooZZ/emotion_factor_inf_sa.xlsx')
emotion_factor_count = len(factor_bank_inf_emotion_sc)
print(f'指数情绪因子数：{emotion_factor_count}')
# 补充分场景因子
factor_bank_inf_scene_sc = pd.read_excel('/data/user/023859/factor_zooZZ/scene_factor_inf_sa.xlsx')
scene_factor_count = len(factor_bank_inf_scene_sc)
print(f'分场景因子数：{scene_factor_count}')

factor_bank_inf_all = pd.concat([factor_bank_inf[['factor_name','factor_type','factor_owner','提交时间','emotion','t']],\
                                 factor_bank_inf_t[['factor_name','factor_type','factor_owner','提交时间','emotion','t']],\
                                 factor_bank_inf_emotion_sc[['factor_name','factor_type','factor_owner','提交时间','emotion','t']],\
                                 factor_bank_inf_scene_sc[['factor_name','factor_type','factor_owner','提交时间','emotion','t']]
                                 ]).reset_index(drop=True)

all_factor_count = len(factor_bank_inf_all)
print(f'总因子数：{all_factor_count}')

assert all_factor_count == (T_1_factor_count + T_factor_count + emotion_factor_count + scene_factor_count)

factor_bank_inf_all.to_excel(os.path.join(result_path_public,'factor_bank_inf_sa.xlsx'))
factor_bank_inf_all.to_excel(os.path.join(result_path_local,'factor_bank_inf_sa.xlsx'))