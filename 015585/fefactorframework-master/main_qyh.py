import pandas as pd
import xfactor.runner.BasicRunner as Runner
from settings import RunMode
import os
import shutil
from h5data.IO import IO
factor_list = [
    # f'factor_qyh_neptune_shortterm_20250828_{i}' for i in range(1,12)

    'factor_qyh_neptunelong_longterm_20250925_othrcv_1',
    'factor_qyh_neptunelong_longterm_20250925_prepay_1',
    'factor_qyh_neptunelong_longterm_20250925_ta_1',
    'factor_qyh_neptunelong_longterm_20250925_ta_2',
    'factor_qyh_neptunelong_longterm_20250925_ta_3',
    'factor_qyh_neptunelong_longterm_20250925_tca_1',
    'factor_qyh_neptunelong_longterm_20250925_tnca_1',
    'factor_qyh_neptunelong_longterm_20250925_tnca_2',
    'factor_qyh_neptunelong_longterm_20250925_tnca_3'

# 'factor_demo_md',
#     'factor_qyh_mimas_test_1'
               ] # 不能带.py
# strategy = 'europa'
strategy = 'neptunelong' # neptune neptunelong
output_dir = '/data/user/015585/20240116_frame/'

if os.path.exists(f'{output_dir}precheck/{strategy}/same_test/'):
    list_file = os.listdir(f'{output_dir}precheck/{strategy}/same_test/')
    for i in list_file:
        for j in factor_list:
            if j.replace('factor_','') in i:
                os.remove(f'{output_dir}precheck/{strategy}/same_test/{i}')
                print('删除长短期检测文件，地址为:', f'{output_dir}precheck/{strategy}/same_test/{i}')

res, check_res = Runner.run(factor_name_list=factor_list, start_date=20170110, end_date=20201231, strategy=strategy,
                 output_dir=output_dir, # 结果的输出路径，包括回测报告等
                 options={
                     "calc.num_cpus": 30,
                     "local_evaluator": "",
                     'precheck': True,
                     "factor_test": True,
                     'report':False,
                     'mode': RunMode.research,})

for i in factor_list:
    print(i)
    print('score:', check_res[i[7:] + '_' + strategy]['check_score_res'].loc['score','tot_score'])
    print('IC:',check_res[i[7:] + '_' + strategy]['corr_sta'].loc['corr_tot', 'value'])
    print('库内高相关因子：', check_res[i[7:] + '_' + strategy]['factor_corr_summary'])

factor_df = pd.DataFrame()
# if strategy == 'neptune':
#     sft_basic_path = '/data/group/800463/data/projectZZ_public/factor_lib/sft_basic_formal_931_20160101_20191231.h5'
#     sft_basic_file = IO.read_data([20160101,20191231],alt = sft_basic_path).loc[
#          pd.to_datetime(str(int(20160101))):pd.to_datetime(str(int(20191231)))]
# else:
#     raise TypeError
for i in factor_list:
    factor_df[i[7:]] = res[i[7:] + f'_{strategy}']['factor_value'][i[7:]]
# factor_df = factor_df.reindex(sft_basic_file.index)
factor_corr = factor_df.corr(method = 'spearman')
print(factor_corr)

# 因子预检测
# import pandas as pd
# pre_check = pd.read_pickle('/data/user/015585/20240116_frame/precheck/neptunelong/result/qyh_neptunelong_longterm_20250904_yfzk1.pkl')
# print(pre_check)

# 因子值
factor_df = pd.read_hdf('/data/user/015585/20240116_frame/factor_value/neptunelong/qyh_neptunelong_longterm_20250911_yjl8.h5')
factor_df['2'] = pd.read_hdf('/data/user/015585/20240116_frame/factor_value/neptunelong/qyh_neptunelong_longterm_20250911_abnormal_yjl1.h5')['qyh_neptunelong_longterm_20250911_abnormal_yjl1']

# ============================长短周期==============================
# res_longshort = pd.DataFrame()
# for factor in factor_list:
#     result_dic_i = pd.read_pickle(f'{output_dir}factor_test/{strategy}/{factor.replace("factor_","")}.pkl')
#     res_longshort.loc[factor.replace("factor_",""), 'label'] = result_dic_i['corr_sta'].loc['corr_tot', 'value']
#     res_longshort.loc[factor.replace("factor_",""), 'label_t2o30d1'] = result_dic_i['factor_corr'].loc['label_t2o30d1','factor_corr']
#     res_longshort.loc[factor.replace("factor_",""), 'label_t6o30d1'] = result_dic_i['factor_corr'].loc['label_t6o30d1','factor_corr']
#     res_longshort.loc[factor.replace("factor_",""), 'label_t4o30d1'] = result_dic_i['factor_corr'].loc['label_t4o30d1','factor_corr']


