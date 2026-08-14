import pandas as pd
import xfactor.runner.BasicRunner as Runner
from settings import RunMode
import os

factor_list = [
    # f'factor_qyh_hotspot_20250313_{i}' for i in range(1,41)
    'factor_xbc_tra_20250408_17'
               ] # 不能带.py
# factor_list = os.listdir('/data/user/015585/fefactorframework-hotspot/factor/')
# factor_list = [x for x in factor_list if '.py' in x]
# factor_list = [x.replace('.py','') for x in factor_list]
# factor_list.sort()
strategy = 'hotspot'
output_dir = '/dfs/user/015585/00_hotspot/factor_value/'
res, check_res = Runner.run(factor_name_list=factor_list, start_date=20160101, end_date=20231231, strategy=strategy,
                 output_dir="/data/user/015585/factors_hotspot/pct35_20250618/", # 结果的输出路径，包括回测报告等
                 options={
                     "calc.num_cpus": 28,
                     "local_evaluator": "",
                     'precheck': True,
                     "factor_test": False,
                     'report':False,
                     'mode': RunMode.research,})
# for i in factor_list:
#     print(i)
#     print('IC:',check_res[i[7:] + '_' + strategy].result_dic['corr_sta'].loc['corr_tot', 'value'])
#     print('库内高相关因子：', check_res[i[7:] + '_' + strategy].result_dic['factor_corr_summary'])

# basic_file = pd.read_hdf('/dfs/user/020412/团队分享/for_qyh/hotspot/md2_20250414_20150901_20231231.h5')


# for i in res.keys():
#     print(i, abs(res[i]['factor_value']).max())

