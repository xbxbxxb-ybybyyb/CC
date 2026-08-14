# coding: utf-8
# Author：fengchi863
# Date ：2023/4/27 16:09

# coding: utf-8
# Author：fengchi863
# Date ：2023/3/22 10:40

from JupiterLocal.TestTool.test1_factor_demo import strongFactorTest
from JupiterLocal.TestTool.run_factor_demo import run_factor
import os
import pandas as pd
import datetime
import importlib
from tqdm import tqdm
from sendInfo import send_file
from sendInfo import send_message

DEBUG = 'Local' # 或者为空'' 或者Local
date = 20230614
# factor_type = 'T-1_factor'
# factor_type = 'TTransaction'
# factor_type = 'TOrder'
# factor_type = 'TTickab'
factor_name_list = list(map(lambda x: x[7: -3], os.listdir(f'/data/user/015614/fcfactor/Jupiter{DEBUG}/d{date}/')))
factor_name_list = list(filter(lambda x: x.startswith('fc_'), factor_name_list))
print(factor_name_list)
# factor_name_list = ['fc_order_last5order_qrr']
recalc_flag = False
basic_file_path = '/data/group/800463/data/project1_public/factor_lib_v2/Basic_zt_001.h5'
res_path = f'/data/user/015614/factor/{date}/'
os.makedirs(res_path, exist_ok=True)

bt_columns = ['nan_num', 'same_rate', 'value_diff_score', 'value_stability_score', 'mixed_diff_score',
              'mixed_stability_score', 'score', 'corr_tot', 'mic_tot', 'high_corr_factor', 'high_corr_factor_corr']
res_df = pd.DataFrame(columns=bt_columns)

def judge_factor_type(factor_name):
    if 'trans_order' in factor_name: return 'TTransaction_TOrder'
    if 'order' in factor_name: return 'TOrder'
    if 'trans' in factor_name: return 'TTransaction'

for factor_name in tqdm(factor_name_list):
    print(factor_name)
    factor_type = judge_factor_type(factor_name)
    # try:
    start_date, end_date = 20160101, 20191231

    if not recalc_flag and os.path.exists(res_path + f'{factor_name}.h5'):
        print(f'{factor_name}.h5已存在')
        factor_df = pd.read_hdf(res_path + f'{factor_name}.h5')
    else:
        mod_name = f'Jupiter{DEBUG}.d{date}.factor_{factor_name}'
        module = importlib.import_module(mod_name)
        func = getattr(module, f'factor_{factor_name}')
        factor_df = run_factor(func, factor_name, factor_type, start_date, end_date, basic_file_path, res_path, interval_res=False, param_tuple=(), multi=True)

    # 回测
    # sft = strongFactorTest(start_date, end_date)
    # quickrise子样本
    # filter_factor = pd.read_pickle('/data/group/800463/data/project1_public/factor_lib_v2/filter_quickrise.pkl')
    # sft = strongFactorTest(start_date, end_date, filter_factor=filter_factor, filter_name='quickrise')
    sft = strongFactorTest(start_date, end_date)
    res_dict = sft.factor_test(factor_df, result_path=res_path, factor_corr_test=True, generate_pdf=True)

    nan_num = res_dict['factor_information'].loc['Nan|Inf Count', 'Factor Info']
    same_rate = res_dict['other_sta'].loc['', 'same_rate']
    value_diff_score= res_dict['check_score_res'].loc['score', 'value_diff_score']
    value_stability_score= res_dict['check_score_res'].loc['score', 'value_stability_score']
    mixed_diff_score = res_dict['check_score_res'].loc['score', 'mixed_diff_score']
    mixed_stability_score = res_dict['check_score_res'].loc['score', 'mixed_stability_score']
    score = res_dict['check_score_res'].loc['score', 'tot_score']
    corr_tot = res_dict['corr_sta'].loc['corr_tot', 'value']
    mic_tot = res_dict['corr_sta'].loc['mic_tot', 'value']

    high_corr_s = res_dict['factor_corr'].query('factor_corr >= 0.7')
    if len(high_corr_s) == 0:
        high_corr_s = res_dict['factor_corr'].iloc[:2]
    else:
        high_corr_s = res_dict['factor_corr'].iloc[:len(high_corr_s) + 2]

    high_corr_factor_list_str = '，'.join(high_corr_s.index.tolist())
    high_corr_factor_corr_list_str = '，'.join(high_corr_s['factor_corr'].map(lambda x: round(x ,4)).map(str).tolist())

    res_df.loc[factor_name] = [nan_num, same_rate, value_diff_score, value_stability_score,
                               mixed_diff_score, mixed_stability_score, score, corr_tot, mic_tot, high_corr_factor_list_str, high_corr_factor_corr_list_str]
    # send_message(factor_name + '回测结果:\n ' + str(res_df.iloc[-1].to_dict()))    # 每回测完成一个因子，发送结果到link
    print(f'{factor_name}测试成功')
    # except Exception as e:
    #     print(e)
    #     print(factor_name, '测试失败！！！！！！！！！')

today_date = datetime.datetime.today().strftime('%Y%m%d')
res_df.to_excel(res_path + f'批量回测结果{today_date}.xlsx')
send_file(res_path + f'批量回测结果{today_date}.xlsx')

# res_df.to_excel(res_path + f'批量回测结果{today_date}_快速拉升.xlsx')
# send_file(res_path + f'批量回测结果{today_date}_快速拉升.xlsx')