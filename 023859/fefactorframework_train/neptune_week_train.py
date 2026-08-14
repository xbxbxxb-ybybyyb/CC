import os
import shutil
import datetime
import pandas as pd
from loguru import logger
from settings import RunMode
from xfactor.FactorUtil import get_factor_class
import xfactor.runner.BasicRunner as Runner
import json
from xquant.compute.aimr import AIMR


#参数设置
strategy='neptune'
factor_version_date = 20250428
start_date = 20240101
end_date = 20241231

path_factor_lib = '/data/user/023859/fefactorframework_train/factor/' # 框架的factor文件夹地址

factor_check_path = '/data/group/800463/data/projectZZ_public/factor_lib/check_res_tot_neptune.xlsx'
strategy_path = os.path.join('/dfs/user/023859/neptune',str(factor_version_date))

factor_type_T_1 = "['T-1_Factor']","['xdb_tick1m']","['xdb_order1m']","['xdb_balancesheet_cs']","['xdb_cashflow_cs']","['xdb_income_cs']","['xdb_balancesheet']", "['xdb_cashflow']", "['xdb_income']]"

# 生成可用因子列表
all_factor_inf = pd.read_excel('/data/user/023859/factor_zooZZ/all_factor_inf.xlsx')
factors_check_res = pd.read_excel(factor_check_path)
factors_available = factors_check_res[(factors_check_res['pre_check']=='pass')&(factors_check_res['factor_type'].isin(factor_type_T_1))&(factors_check_res['提交时间']<=factor_version_date)]['factor_name'].to_list()

factor_bank_inf = all_factor_inf[all_factor_inf['factor_name'].isin(factors_available)]
factor_bank_inf = factor_bank_inf[['factor_name','factor_owner','factor_type','提交时间','emotion']]
factor_bank_inf['t'] = factor_bank_inf['factor_type'].apply(lambda x: 'T-1' if x in factor_type_T_1 else 'T')
factor_bank_inf.to_excel(os.path.join(strategy_path,'factor_bank_inf.xlsx'), index=False)

# 筛选df后
count = factor_bank_inf['factor_name'].value_counts().head()
assert count.max() == 1
filtered_df = factor_bank_inf[factor_bank_inf['factor_type'].str.contains('\[')]#新平台框架的因子，factor_type中会带[]

# 根据情况考虑是否多核
print('当前版本可用因子数量：',len(filtered_df),list(filtered_df['factor_name']))

dock_num=100
dock_pool_num=1
factor_list=filtered_df['factor_name'].unique()

# # 因子数<=100
# parallel_list=['%s;%s;%s'%(strategy,factor_name,dock_pool_num) for factor_name in factor_list]
# dock_num = min(len(factor_list),dock_num)
#
# params = {"parallel_list": parallel_list,
#           "tag":"xquant", "cpu":dock_pool_num, "gpu":0, "memory":60*1024*dock_pool_num}
# AIMR.runTasks('neptune_week_update_aimr.py', json.dumps(params))

# 因子数超100
dock_num=min(dock_num,len(factor_list))
print('并行化：%s*%s'%(dock_num,dock_pool_num))
parallel_list=['%s;%s;%s;%s;%s'%(start_date,end_date,strategy,dock_pool_num,'-'.join(factor_list[i::dock_num])) for i in range(dock_num)]
print(parallel_list)
params = {"parallel_list": parallel_list,
          "tag":"xquant", "cpu":dock_pool_num, "gpu":0, "memory":dock_pool_num*60*1024}
AIMR.runTasks('neptune_week_update_aimr.py',json.dumps(params))