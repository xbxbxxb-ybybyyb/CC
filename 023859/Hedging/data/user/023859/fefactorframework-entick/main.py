import xfactor.runner.BasicRunner as Runner
from settings import RunMode
import os

factor_list = [
                'factor_tsq_neweuropa_20250123_5'
               ] # 不能带.py
strategy = 'europa'

# for i in os.listdir(os.path.join(os.getcwd(), "factor")):
#     if ".py" in i:
#         factor_list.append(i.split(".py")[0])
res, check_res = Runner.run(factor_name_list=factor_list, start_date=20160101, end_date=20191231, strategy=strategy,
                 output_dir="/data/user/023859/test/", # 结果的输出路径，包括回测报告等
                 options={
                     "calc.num_cpus": 10,
                     "local_evaluator": "",
                     'precheck': True,
                     "factor_test": True,
                     'report':False,
                     'mode': RunMode.research})
for i in factor_list:
    print(i)
    print('score:', check_res[i[7:] + '_' + strategy].result_dic['check_score_res'].loc['score','tot_score'])
    print('IC:',check_res[i[7:] + '_' + strategy].result_dic['corr_sta'].loc['corr_tot', 'value'])
    print('库内高相关因子：', check_res[i[7:] + '_' + strategy].result_dic['factor_corr_summary'])
# 因子预检测
import pandas as pd
# pre_check = pd.read_pickle('/data/user/015585/20240116_frame/precheck/saturn/result/qyh_mercury_test_zwh.pkl')
# result_dic = pd.read_pickle('/data/user/015585/20240116_frame/factor_test/europa/qyh_europa_20240822_3.pkl')
# print(pre_check)
# import pandas as pd
# pd.read_hdf('/data/user/015585/20240116_frame/factor_value/saturn/qyh_newsat_test0626_2.h5')


