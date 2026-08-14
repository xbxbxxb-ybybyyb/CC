# @Time : 2021/7/19 14:27
# @Author : Zhichen Lu
# @File : label_generation.py
import numpy as np
from dataApi.getData import get_minute_1factor, get_daily_1factor
from dataApi.tradeDate import get_date_range
from dataApi.usefulTools import delay
import pandas as pd
from StrongStockModel.conf.path_config import root_path
from tqdm import tqdm
from dataApi.LoadingTool import trans_df2arr

out_path = '/data/'

bar_list = [1000,1030,1100,1300,1330,1400,1430]
start, end = 20140801, 20210718
close = get_minute_1factor('close_badj', start_datetime=start, end_datetime=end)
close = close.fillna(method='pad').swaplevel(0,1).loc[bar_list].swaplevel(0,1)
# vol = get_minute_1factor('vol', start_datetime=start, end_datetime=end)
adj_factor = get_daily_1factor('adjfactor', get_date_range(start, end))

index,columns = close.index,close.columns
shape = (close.shape[0]//len(bar_list),len(bar_list),close.shape[-1])
close = close.values.reshape(shape)
ret = {}
for window in tqdm(range(2,6)):
    temp_ret = close/delay(close,window) - 1
    temp_ret = temp_ret.reshape((len(index),len(columns)))
    ret[window] = pd.DataFrame(temp_ret,index=index,columns=columns).shift(-window*len(bar_list))

for window in ret:
    pd.to_pickle(ret[window],f'{root_path}labels/future_{int(window*240)}.pkl')

# formated = trans_df2arr(ret[2],start_date=ret[2].index[0][0],end_date=ret[2].index[-1][0],code_list=ret[2].columns.tolist())


