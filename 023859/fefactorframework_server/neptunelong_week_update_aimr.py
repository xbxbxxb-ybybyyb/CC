import sys
sys.path.append("/data/user/023859/fefactorframework_server/")
import os
import pandas as pd
import xfactor.runner.BasicRunner as Runner
from xquant.compute.aimr import AIMR
from settings import RunMode

# param = AIMR.getParam() #TODO
# print(param)
# param_list=param.split(';')
# last_thursday=param_list[0]
# strategy=param_list[1]
# factor_name=param_list[2]
# dock_pool_num=int(param_list[3])

param = AIMR.getParam()
#param='20250325;neptune;factor_kline;1;sss_oc2p_250_mud-sss_c2hl_250_max'
print(param)
param_list=param.split(';')
last_thursday=param_list[0]
strategy=param_list[1]
dock_pool_num=int(param_list[2])
factor_name_list=param_list[3].split('-')

module_base_dir='factor_lib'
df = pd.read_excel('/data/user/023859/factor_zooZZmkt/all_factor_inf.xlsx')
# filtered_df = df[df['factor_name']==factor_name] #TODO
filtered_df = df[df['factor_name'].isin(factor_name_list)]


factor_list = []
for index, inf in filtered_df.iterrows():
    if strategy.lower() in ["saturn", "sell", "mimas", "neptune", "neptunelong"]:
        factor_name, factor_date = inf['factor_name'], inf['提交时间']
    elif strategy.lower() in ["europa", "jupiter", "metis"]:
        factor_name, factor_date = inf['factor_name'], inf['factor_date']
    else:
        raise Exception("策略名不在规定范围内！input_strategy={}".format(strategy))

    module_path = os.path.join(module_base_dir, strategy.lower(), 'factor_' + str(int(factor_date)))

    factor_list.append({
        "module_path": module_path,
        "factor_name": 'factor_' + factor_name
    })

# 入库
if len(factor_list) > 0:
    print(strategy, len(factor_list), factor_list)
    Runner.run(factor_name_list=factor_list, start_date=20170110, end_date=20211231,
               strategy=strategy.lower(), upload_date=last_thursday,
               mode=RunMode.factor_warehouse,
               options={
                   "calc.num_cpus": dock_pool_num,
                   'override': True,
                   'precheck': True,
                   'factor_test': True,
                   'report': False,
                   'warehouse': False
               })
    print('{}策略尝试入库{}个因子'.format(strategy, str(len(factor_list))))