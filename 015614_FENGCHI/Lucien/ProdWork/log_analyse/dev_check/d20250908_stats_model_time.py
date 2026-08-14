# coding: utf-8
# Author：fengchi863
# Date ：2025/9/8 10:40

from dataApi.tradeDate import get_date_range
import gzip
import re
import pandas as pd
from tqdm import tqdm

def getValueByKeyFromLine2(line, by, form='(.*?)[,\\\\n\n}]'):
    """给cpp日志解析symbol时使用，有时symbol在最后需要解析\\n，但如果java用这个OrderType有时候会出问题"""
    if by not in line:
        return ''
    try:
        return re.findall(r"%s=%s" % (by, form), line)[0]
    except:
        return 'other'

date_list = get_date_range(20250801, 20250905)
# time_list = list()
# code_list = list()
# for _dat in tqdm(date_list):
#     _dat = str(_dat)
#     trade_date_str = _dat[:4] + '-' + _dat[4:6] + '-' + _dat[6:8]
#     sh_mimas_log_fpath = f'/data/group/800463/StrategyLog/prd/SHEX.MimasStrategy-{trade_date_str}.log.gz'
#     sz_mimas_log_fpath = f'/data/group/800463/StrategyLog/prd/SZEX.MimasStrategy-{trade_date_str}.log.gz'
#
#     sh_line = gzip.GzipFile(sh_mimas_log_fpath)
#     sz_line = gzip.GzipFile(sz_mimas_log_fpath)
#     sh_line = sh_line.readlines()
#     sz_line = sz_line.readlines()
#     total_line = sh_line + sz_line
#
#     model_line = list(filter(lambda x: f'model predict sum_signal' in str(x), total_line))
#     time_list += list(map(lambda x: x[:19], model_line))
#     code_list += list(map(lambda x: getValueByKeyFromLine2(str(x), 'symbol'), model_line))
#
# mimas_df = pd.Series(code_list, index=time_list)
# mimas_df = mimas_df.reset_index()
# mimas_df['diff'] = mimas_df['index'].apply(lambda x: int(bytes.decode(x, errors='ignore')[17:19])-30)
# mimas_df.to_excel('/data/user/015614/junkData/mimas.xlsx')
#
# ## Saturn
# time_list = list()
# code_list = list()
# for _dat in tqdm(date_list):
#     _dat = str(_dat)
#     trade_date_str = _dat[:4] + '-' + _dat[4:6] + '-' + _dat[6:8]
#     sh_saturn_log_fpath = f'/data/group/800463/StrategyLog/prd/SHEX.SaturnStrategy-{trade_date_str}.log.gz'
#     sz_saturn_log_fpath = f'/data/group/800463/StrategyLog/prd/SZEX.SaturnStrategy-{trade_date_str}.log.gz'
#
#     sh_line = gzip.GzipFile(sh_saturn_log_fpath)
#     sz_line = gzip.GzipFile(sz_saturn_log_fpath)
#     sh_line = sh_line.readlines()
#     sz_line = sz_line.readlines()
#     total_line = sh_line + sz_line
#
#     model_line = list(filter(lambda x: f'model predict sum_signal' in str(x), total_line))
#     time_list += list(map(lambda x: x[:19], model_line))
#     code_list += list(map(lambda x: getValueByKeyFromLine2(str(x), 'symbol'), model_line))
#
# saturn_df = pd.Series(code_list, index=time_list)
# saturn_df = saturn_df.reset_index()
# saturn_df['diff'] = saturn_df['index'].apply(lambda x: int(bytes.decode(x, errors='ignore')[17:19]))
# saturn_df.to_excel('/data/user/015614/junkData/saturn.xlsx')

#%% Ceres
time_list = list()
code_list = list()
for _dat in tqdm(date_list):
    _dat = str(_dat)
    trade_date_str = _dat[:4] + '-' + _dat[4:6] + '-' + _dat[6:8]
    sh_ceres_log_fpath = f'/data/group/800463/StrategyLog/prd/SHEX.CeresStrategy-{trade_date_str}.log.gz'
    sz_ceres_log_fpath = f'/data/group/800463/StrategyLog/prd/SZEX.CeresStrategy-{trade_date_str}.log.gz'

    sh_line = gzip.GzipFile(sh_ceres_log_fpath)
    sz_line = gzip.GzipFile(sz_ceres_log_fpath)
    sh_line = sh_line.readlines()
    sz_line = sz_line.readlines()
    total_line = sh_line + sz_line

    model_line = list(filter(lambda x: f'model predict sum_signal' in str(x), total_line))
    time_list += list(map(lambda x: x[:19], model_line))
    code_list += list(map(lambda x: getValueByKeyFromLine2(str(x), 'symbol'), model_line))

ceres_df = pd.Series(code_list, index=time_list)
ceres_df = ceres_df.reset_index()
ceres_df['diff'] = ceres_df['index'].apply(lambda x: int(bytes.decode(x, errors='ignore')[14:19].replace(':', ''))-3010)
p4_df = ceres_df.query('diff < 50')
ceres_df = ceres_df.query('diff > 50')
ceres_df['diff'] = ceres_df['index'].apply(lambda x: int(bytes.decode(x, errors='ignore')[14:19].replace(':', ''))-3100)

ceres_df.to_excel('/data/user/015614/junkData/ceres.xlsx')
p4_df.to_excel('/data/user/015614/junkData/p4.xlsx')

from xquant.marketdata import MarketData
md = MarketData()
order_df = md.get_data_by_date('Transaction', '603163.SH', 20250805)