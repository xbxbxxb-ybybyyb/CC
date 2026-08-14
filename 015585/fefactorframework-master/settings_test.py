# this file contains base path settings for fefactor framework

import os
from enum import Enum, unique

@unique
class RunMode(Enum):
    research = 0,
    remote_deploy = 1,
    prod_prepare = 2,

path_dict = {
    "saturn": {
         'TTransaction': '/data/group/800463/data/project2_prod/everyday_Data/transaction/',
         'TTickab': '/data/group/800463/data/project2_prod/everyday_Data/tick/',
         'TOrder': '/data/group/800463/data/project2_prod/everyday_Data/order_cs/',
         'T1mTransaction': '/data/group/800463/data/project2_prod/everyday_Data_931/transaction/',
         'T1mTickab': '/data/group/800463/data/project2_prod/everyday_Data_931/tick/',
         'T1mOrder': '/data/group/800463/data/project2_prod/everyday_Data_931/order_cs/',
         'T10mTransaction': '/data/group/800463/data/project2_prod/everyday_Data_940/transaction/',
         'T10mTickab': '/data/group/800463/data/project2_prod/everyday_Data_940/tick/',
         'TTransaction_cs': '/data/group/800463/data/project2_prod/everyday_Data/transaction_cs/',
         'TTickab_cs': '/data/group/800463/data/project2_prod/everyday_Data/tick_cs/',
         'TOrder_cs': '/data/group/800463/data/project2_prod/everyday_Data/order_cs/',
         'T1mTransaction_cs': '/data/group/800463/data/project2_prod/everyday_Data_931/transaction_cs/',
         'T1mTickab_cs': '/data/group/800463/data/project2_prod/everyday_Data_931/tick_cs/',
         'T1mOrder_cs': '/data/group/800463/data/project2_prod/everyday_Data_931/order_cs/',
         'T10mTransaction_cs': '/data/group/800463/data/project2_prod/everyday_Data_940/transaction_cs/',
         'T10mTickab_cs': '/data/group/800463/data/project2_prod/everyday_Data_940/tick_cs/',
         'Basic': '/data/group/800463/data/project2_public/factor_lib/Basic_closed_hf_finish_20160101_20191231.h5',
    },
    "sell": {
         'TTransaction': '/data/group/800463/data/project2_prod/everyday_Data/transaction/',
         'TTickab': '/data/group/800463/data/project2_prod/everyday_Data/tick/',
         'TOrder': '/data/group/800463/data/project2_prod/everyday_Data/order_cs/',
         'T1mTransaction': '/data/group/800463/data/project2_prod/everyday_Data_931/transaction/',
         'T1mTickab': '/data/group/800463/data/project2_prod/everyday_Data_931/tick/',
         'T1mOrder': '/data/group/800463/data/project2_prod/everyday_Data_931/order_cs/',
         'T10mTransaction': '/data/group/800463/data/project2_prod/everyday_Data_940/transaction/',
         'T10mTickab': '/data/group/800463/data/project2_prod/everyday_Data_940/tick/',
         'TTransaction_cs': '/data/group/800463/data/project2_prod/everyday_Data/transaction_cs/',
         'TTickab_cs': '/data/group/800463/data/project2_prod/everyday_Data/tick_cs/',
         'TOrder_cs': '/data/group/800463/data/project2_prod/everyday_Data/order_cs/',
         'T1mTransaction_cs': '/data/group/800463/data/project2_prod/everyday_Data_931/transaction_cs/',
         'T1mTickab_cs': '/data/group/800463/data/project2_prod/everyday_Data_931/tick_cs/',
         'T1mOrder_cs': '/data/group/800463/data/project2_prod/everyday_Data_931/order_cs/',
         'T10mTransaction_cs': '/data/group/800463/data/project2_prod/everyday_Data_940/transaction_cs/',
         'T10mTickab_cs': '/data/group/800463/data/project2_prod/everyday_Data_940/tick_cs/',
         'Basic': '/data/group/800463/data/projectS_public/factor_lib/Basic_closed_hf_finish_20160101_20191231.h5'
    },
    "jupiter": {
        'TTransaction': '/data/group/800463/data/project1_prod/transaction_zt_bs_ezt/',
        'TTickab': '/data/group/800463/data/project1_prod/tickab_zt/',
        'LastTouchTTick':'/data/group/800463/data/project1_prod/last_touch_t_tick/',
        'MarketTTick': '/data/group/800463/data/project1_prod/market_t_tick/',
        'Market1TTick': '/data/group/800463/data/project1_prod/market_t_tick/',
        'MarketIndTTick': '/data/group/800463/data/project1_prod/market_t_tick/',
        "Basic": '/data/group/800463/data/project1_public/factor_lib_v2/Basic_zt_20150901_20191231.h5',
    },
    "europa":  {'TTransaction': '/data/group/800463/data/project1_prod/transaction_europa/',
               'TTickab': '/data/group/800463/data/project1_prod/tick_europa/',
               'TOrder':'/data/group/800463/data/project1_prod/order_europa/',
               'LastTouchTTick':'/data/group/800463/data/project1_prod/last_touch_t_tick/',
               'MarketTTick':'/data/group/800463/data/project1_prod/market_t_tick/',
               'Market1TTick':'/data/group/800463/data/project1_prod/market_t_tick/',
               'MarketIndTTick':'/data/group/800463/data/project1_prod/market_t_tick/',
               "Basic": '/data/group/800463/data/project1_public/factor_lib_v3/Basic_zt_001_20150901_20191231.h5'}
}

