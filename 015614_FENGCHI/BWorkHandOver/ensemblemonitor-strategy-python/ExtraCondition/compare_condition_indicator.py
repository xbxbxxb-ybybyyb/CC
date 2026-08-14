# @Time : 2022/1/7 9:07
# @Author : Zhichen Lu
# @File : compare_condition_indicator.py
import pandas as pd
import numpy as np
from dataApi.tradeDate import get_date_range
from ExtraTools import get_path_conf
from dataApi.sendInfo import send_file

# tag = ''
# path_conf = get_path_conf(f'/data/group/800319/strategy_local_path3_ForExtra{tag}/')

def get_basic_indicator_compare(path_conf,file_name,date_list,out=None):
    local_config_path, holding_info_path, hyper_param_path, code_list_path, model_config_path, buy_time_info_path, \
    vol_info_path, init_conf_path, daily_out_path, ratio_path, matrix_conf, condition_path = \
        [path_conf[x] for x in
         ['local_config_path', 'holding_info_path', 'hyper_param_path', 'code_list_path', 'model_config_path', 'buy_time_info_path',
          'vol_info_path', 'init_conf_path', 'daily_out_path', 'ratio_path', 'matrix_conf', 'condition_path']]

    offline_indicator = pd.read_pickle(file_name)

    # date_list = [20220110,20220111]#get_date_range(20210913, 20210928)
    online_indicator = {}
    for date in date_list:
        temp = pd.read_pickle(f'{daily_out_path}/{date}.pkl')
        online_indicator.update({(date, x): temp['extra_condition_param'][x] for x in temp['extra_condition_param']})

    online_indicator = pd.DataFrame(online_indicator).T.drop(['CYBZ', 'HS300', 'SZ50', 'SZCZ', 'ZX100', 'ZZ1000', 'ZZ500', 'ZZ800', 'ZZQZ', 'ZZZZ'], axis=1)
    offline_indicator = pd.DataFrame(offline_indicator).T
    # offline_indicator['terminal_flag'] = offline_indicator['terminal_flag'].apply(lambda x: 1 - x)
    compare = pd.DataFrame({'线上': online_indicator.stack(), '线下': offline_indicator.stack()})
    compare = compare.stack().unstack(level=[-2, -1]).astype(float)
    check = compare.swaplevel(0,1,axis=1)
    diff = check['线上'].astype(float) - check['线下'].astype(float)
    diff.columns = pd.MultiIndex.from_tuples(diff.columns.map(lambda x:(x,'diff')))
    compare = pd.concat([compare,diff],axis=1).sort_index(axis=1,ascending=False)
    if out:
        # out_file = f'./{tag}_20220111参数比对_当天股票池.xlsx'
        compare.to_excel(out)
        send_file(['015664'], out)
    return compare
