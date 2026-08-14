# @Time : 2021/7/19 16:32
# @Author : Zhichen Lu
# @File : LoadingTool.py
import numpy as np
from dataApi.tradeDate import get_date_range
import pandas as pd
from dataApi.tradeDate import trade_minutes,fix_minutes,get_date_range
import numpy as np
import itertools
from tqdm import tqdm
import os
from dataApi.usefulTools import delay
from dataApi.FixFactorRollPrepare import load_fix_data,feature_engineering

date_list = get_date_range(20140701,20210531)
fix_idx = [trade_minutes.index(x) for x in fix_minutes]


def trans_df2arr(df, start_date=None, end_date=None, code_list=None, freq=7, roll=False,address = '/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/'):
    print(f'transfer by format {address}')
    idx_date = np.load('%s/idx_date.npy' % address)
    idx_code = np.load('%s/idx_code.npy' % address)
    index = df.index.get_level_values(0).values[::freq]
    columns = df.columns.values
    df = df.values.reshape(-1, freq, df.shape[-1])
    if roll:
        index = index[1:]
        df1 = np.empty((len(index), 2 * freq - 1, len(columns)), dtype=df.dtype)
        df1[:, :freq - 1] = df[:-1, 1:]
        df1[:, freq - 1:] = df[1:]
        arr = df1.transpose(0, 2, 1).reshape(-1, 2 * freq - 1)
    else:
        arr = df.transpose(0, 2, 1).reshape(-1, freq)
    start_date = start_date if start_date else index[0]
    end_date = end_date if end_date else index[-1]
    date_list = get_date_range(start_date, end_date)
    choose = np.take(np.arange(len(date_list)), np.searchsorted(date_list, idx_date), mode='clip')
    choose = np.asanyarray(date_list)[choose] == idx_date
    if code_list:
        code_list.sort()
        choose1 = np.take(np.arange(len(code_list)), np.searchsorted(code_list, idx_code), mode='clip')
        choose1 = np.asanyarray(code_list)[choose1] == idx_code
        choose &= choose1
    idx_date = idx_date[choose]
    idx_code = idx_code[choose]

    x_index = np.argsort(index)
    sorted_y = np.searchsorted(index[x_index], idx_date)
    date_index = np.take(x_index, sorted_y, mode="clip")
    date_mask = index[date_index] != idx_date

    x_index = np.argsort(columns)
    sorted_y = np.searchsorted(columns[x_index], idx_code)
    code_index = np.take(x_index, sorted_y, mode="clip")
    code_mask = columns[code_index] != idx_code

    idx = date_index * len(columns) + code_index
    mask = date_mask | code_mask
    arr = arr[idx]
    arr[mask] = np.nan
    return arr

def load_cross_factor(factor_name,start,end,address,return_type='arr'):
    factor = np.load(f'{address}{factor_name}.npy')

    # if os.path.split('/'+address.strip('/'))[-1]=='daily2min':
    #     factor = delay(factor)
    code_list = np.load('/arch1/group/800442/800319/AAcross/basic/code_list.npy').tolist()

    factor = factor[date_list.index(start)-1:date_list.index(end)+1,fix_idx,:]
    factor = factor.reshape(factor.shape[0]*factor.shape[1],factor.shape[-1])
    factor[np.isnan(factor)] = 0
    datetime_list = list(itertools.product(date_list[date_list.index(start)-1:date_list.index(end)+1], fix_minutes))
    factor = pd.DataFrame(factor,index=pd.MultiIndex.from_tuples(datetime_list),columns=code_list)

    if return_type=='arr':
        target_arr = trans_df2arr(factor,start_date=start,end_date=end,roll=True)
        return target_arr
    elif return_type=='df':
        return factor
    else:
        raise Exception('Wrong return type')

def transform(each,out_path='/data/group/800442/800319/HFfactor/CrossFactor/data/'):
    if os.path.exists(f'{out_path}/{each}.npy'):
        print(each, 'exist')
        return
    author = list(filter(lambda x: os.path.exists(f'{cross_res_path}/{x}/{each}.npy'), os.listdir(cross_res_path)))
    if len(author) != 1:
        raise Exception(f'{each} in {author}')
    else:
        author = author[0]
    factor = load_cross_factor(each, 20140801, 20210531, address=f'{cross_res_path}/{author}/')
    factor = factor.astype('float32')
    factor = np.ascontiguousarray(factor)
    np.save(f'{out_path}/{each}.npy', factor)
    print(each)


from multiprocessing import Pool
if __name__ == '__main__':
    cross_res_path = '/arch1/group/800442/800319/AAcross/factor_result_rerun9/1min/20140701_20210531'
    cross_factor_list = []
    for each in os.listdir(cross_res_path):
        cross_factor_list += list(filter(lambda x : x.endswith('.npy'),os.listdir(f'{cross_res_path}/{each}')))
    cross_factor_list = [x.replace('.npy', '') for x in cross_factor_list]

    import gc
    for f_name in tqdm(cross_factor_list,'transforming...'):
        transform(f_name)
        gc.collect()


