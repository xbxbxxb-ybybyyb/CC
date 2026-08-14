# coding: utf-8
# Author：fengchi863
# Date ：2020/12/25 13:10

from ShortTermTrading.interface.ActiveConceptApi import get_daily_active_stock,\
    get_active_stock_1concept, get_daily_active_concept
import h5py

interface_root_path = '/data/group/800319/fengchi/interface/active_concept_data/'
hdf_name = 'active_concept_data.h5'
f = h5py.File(interface_root_path + hdf_name)
active_concept_list = list(f.keys())
print('temp_data共有%d个活跃板块' % len(active_concept_list))

for concept_code in active_concept_list:
    active_concept_stock = get_active_stock_1concept(concept_code, start_date=20201222, end_date=20201224, \
                                                     read_path=interface_root_path + hdf_name)
    print(concept_code, str(active_concept_stock.sum().sum()))


