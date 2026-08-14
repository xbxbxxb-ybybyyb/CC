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
factor_version_date = 20250720

start_date = 20210101
end_date = 20231231

strategy_path = os.path.join('/dfs/user/023859/neptune',str(factor_version_date))

filtered_df = pd.read_excel('/data/user/023859/factor_zooZZ/all_factor_inf.xlsx')
filtered_df=filtered_df[~filtered_df['factor_type'].str.contains('T1mTransaction|T1mTickab|T1mTick1s|T1mCancel|T1mTickfulladdorder|T1mOrder|xdb_trade|xdb_tickex|xdb_order')]
filtered_df = filtered_df[filtered_df['提交时间'] <= factor_version_date]
factors_check_res = pd.read_excel('/dfs/group/800463/public/projectZZ_public/factor_lib/check_res_tot_neptune.xlsx')
factors_pass = factors_check_res[(factors_check_res['pre_check']=='pass')]['factor_name'].to_list()

factor_list = filtered_df[filtered_df['factor_name'].isin(factors_pass)]['factor_name'].to_list()

paths = '/dfs/user/023859/neptune/20250720/20210101_20231231/factor_value/neptune'
h5_files = [f.split('.')[0] for f in os.listdir(paths) if f.endswith('.h5')]
factor_list = list(set(factor_list) - set(h5_files))


# factor_bank_inf = pd.read_excel(os.path.join(strategy_path,'factor_bank_inf_s1.xlsx'))
# factor_bank_inf = factor_bank_inf.sort_values(by='factor_type')
# count = factor_bank_inf['factor_name'].value_counts().head()
# assert count.max() == 1
# filtered_df = factor_bank_inf[factor_bank_inf['factor_type'].str.contains('\[')]#新平台框架的因子，factor_type中会带[]

# 根据情况考虑是否多核
print('当前版本可用因子数量：',len(factor_list))

dock_num=100
dock_pool_num=1
# factor_list=list(filtered_df['factor_name'].unique())

# factor_list.remove('tsq_newneptune_20250417_19')
# print('请单独运行高耗时因子：tsq_newneptune_20250417_19')

# # 因子数<=100
# parallel_list=['%s;%s;%s'%(strategy,factor_name,dock_pool_num) for factor_name in factor_list]
# dock_num = min(len(factor_list),dock_num)
#
# params = {"parallel_list": parallel_list,
#           "tag":"xquant", "cpu":dock_pool_num, "gpu":0, "memory":60*1024*dock_pool_num}
# AIMR.runTasks('neptune_train_aimr.py', json.dumps(params))

# 因子数超100
dock_num=min(dock_num,len(factor_list))
print('并行化：%s*%s'%(dock_num,dock_pool_num))
parallel_list=['%s;%s;%s;%s;%s;%s'%(factor_version_date,start_date,end_date,strategy,dock_pool_num,'-'.join(factor_list[i::dock_num])) for i in range(dock_num)]
print(parallel_list)
params = {"parallel_list": parallel_list,
          "tag":"xquant", "cpu":dock_pool_num, "gpu":0, "memory":70*1024}
AIMR.runTasks('neptune_train_aimr.py', json.dumps(params))