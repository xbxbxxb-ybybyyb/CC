# coding: utf-8
# Author：fengchi863
# Date ：2020/12/24 14:37

import h5py
import pandas as pd
from tqdm import tqdm
import warnings
from ShortTermTrading.dataApi.tradeDate import get_date_range, get_pre_trade_date
from datetime import datetime
warnings.filterwarnings("ignore")  # 减少NaturalNameWarning的输出

now_date = int(datetime.now().strftime('%Y%m%d'))
# end_date = now_date
end_date = get_pre_trade_date(now_date, 1)
start_date = get_pre_trade_date(end_date, 30)

interface_root_path = '/data/group/800319/fengchi/interface/active_concept_data/'
shouyinfanbao_root_path = '/data/user/fengchi/首阴反包/'
append_data_path = '/data/user/fengchi/首阴反包/append_data/'

append_hdf_name = 'Active_stock.h5' # 新的要补充的
f = h5py.File(append_data_path + append_hdf_name)
append_active_concept_list = list(f.keys())
print('append_data共有%d个活跃板块' % len(append_active_concept_list))

interface_hdf_name = 'active_concept_data.h5' # 旧的
f = h5py.File(interface_root_path + interface_hdf_name)
interface_active_concept_list = list(f.keys())
print('之前共有%d个活跃板块' % len(interface_active_concept_list))

# 用于储存接口数据
for concept_code in tqdm(append_active_concept_list):
    if concept_code in interface_active_concept_list:
        old_data = pd.read_hdf(interface_root_path + interface_hdf_name, key=concept_code, start=-1)
        last_date = old_data.index.tolist()[0]
        if last_date == end_date:
            print(concept_code, '历史数据存储已到', str(end_date))
            continue
        else:
            old_active_stock = pd.read_hdf(interface_root_path + interface_hdf_name, key=concept_code)
            need_date_list = get_date_range(get_pre_trade_date(last_date, -1), end_date)
            append_active_stock = pd.read_hdf(append_data_path + append_hdf_name, key=concept_code)
            print(concept_code, append_active_stock.sum().sum())
            append_active_stock = append_active_stock.loc[need_date_list]
            temp_active_stock = pd.concat([old_active_stock, append_active_stock], axis=0)
            temp_active_stock = temp_active_stock.fillna(False)
            temp_active_stock.to_hdf(interface_root_path + interface_hdf_name,
                                     key=concept_code, format='t')
            print(concept_code, '已更新到', str(end_date))
    else:
        active_stock = pd.read_hdf(append_data_path + append_hdf_name, key=concept_code)
        active_stock = active_stock.rolling(10).sum() > 0
        need_date_list = get_date_range(20150601, end_date)
        append_active_stock = active_stock
        append_active_stock = append_active_stock.reindex(index=need_date_list)
        append_active_stock = append_active_stock.fillna(False)
        append_active_stock.to_hdf(interface_root_path + interface_hdf_name,
                                 key=concept_code, format='t')
        print(concept_code, '原来没有该板块，已新加入', str(end_date))


# 储存处理后的Active_concept，这一步只是转移文件储存位置
interface_read_path = interface_root_path + 'daily_active_concept.h5'
interface_active_concept = pd.read_hdf(interface_read_path, key='daily_active_concept')
last_date = interface_active_concept.index.tolist()[-1]
if last_date == end_date:
    print('已完成')
else:
    need_date_list = get_date_range(get_pre_trade_date(last_date, -1), end_date)
    append_read_path = append_data_path + 'Active_concept.h5'
    append_active_concept = pd.read_hdf(append_read_path, 'Active_concept').loc[need_date_list]
    active_concept = pd.concat([interface_active_concept, append_active_concept], axis=0)
    active_concept = active_concept.fillna(False)
    active_concept.to_hdf(interface_root_path + 'daily_active_concept.h5', key='daily_active_concept', format='t')
    print('active_concept存储完成')

# 上一周刚活跃的板块，如果这一周没有活跃，则不会有它的columns，那么concat以后就是False