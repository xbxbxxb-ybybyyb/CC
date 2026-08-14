# coding: utf-8
# Author：fengchi863
# Date ：2020/12/15 19:41

import sys
import pandas as pd
sys.path.append('/data/group/800319')
from dataApi import getData

final_interface_path = '/data/group/800319/Afengchi/interface/final_interface_data/'

def get_active_stock_1concept(concept=None, start_date=20200101, end_date=20201201,
                        read_path=final_interface_path + 'active_concept_data.h5'):
    date_list = getData.get_date_range(start_date, end_date)
    start_date = date_list[0]
    end_date = date_list[-1]
    active_concept_stock = pd.read_hdf(read_path, key=concept)
    return active_concept_stock.loc[start_date:end_date]

def get_daily_active_concept(start_date=20200101, end_date=20201201,
                             read_path=final_interface_path + 'daily_active_concept.h5'):
    date_list = getData.get_date_range(start_date, end_date)
    start_date = date_list[0]
    end_date = date_list[-1]
    daily_active_concept = pd.read_hdf(read_path, key='daily_active_concept')
    return daily_active_concept.loc[start_date:end_date]

# 给鲁植宸
def get_daily_active_stock(start_date=20150601, end_date=20201201,
                           read_path=final_interface_path + 'daily_active_stock.pkl'):
    date_list = getData.get_date_range(start_date, end_date)
    start_date = date_list[0]
    end_date = date_list[-1]
    daily_active_stock = pd.read_pickle(read_path)
    return daily_active_stock.loc[start_date:end_date]

if __name__ == '__main__':
    # active_concept_stock = get_factor_1concept(concept='884702.WI', factor='板块活跃股票池')
    daily_active_concept = get_daily_active_concept(20140101, 20201231)
    daily_stock = get_daily_active_stock(20140101, 20201231)
#     pass
#