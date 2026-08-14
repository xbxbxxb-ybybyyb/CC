# this file contains base path settings for fefactor framework

import os
from enum import Enum, unique


@unique
class RunMode(Enum):
    research = 0,
    factor_warehouse = 1,
    prod_prepare = 2,
    daily_update = 3


valid_strategy_names = ["saturn", "sell", "jupiter", 'europa', "metis", "mimas", "saturn/sell", "jupiter/europa",
                        "sell/saturn","mercury",
                        "europa/jupiter", 'hotspot']
valid_single_strategy_names = ["saturn", "sell", "jupiter", 'europa', "metis", "mimas","mercury" , 'hotspot']
# xdb根路径，目前废弃，使用xdb_path_xdbformat
xdb_path = {
    "jupiter": "/dfs/group/800463/data/xdb_data_lag3/europa_jupiter/",
    "europa": "/dfs/group/800463/data/xdb_data_lag3/europa_jupiter/",
    "saturn": "/dfs/group/800463/data/xdb_data_lag3/saturn_sell/",
    "sell": "/dfs/group/800463/data/xdb_data_lag3/saturn_sell/",
    "metis": "/dfs/group/800463/data/xdb_data_lag3/metis/",
    "mimas": "/dfs/group/800463/data/xdb_data_lag3/mimas/",
    "mercury": "/dfs/group/800463/data/xdb_data_lag3/mercury/",
}

# 用于分段压缩测试，后作为替代
xdb_path_xdbformat = {
    "jupiter": "/dfs/group/800463/data/xdb_data_lag3_new/europa_jupiter/",
    "europa": "/dfs/group/800463/data/xdb_data_lag3_new/europa_jupiter/",
    "saturn": "/dfs/group/800463/data/xdb_data_lag3_new/saturn_sell/",
    "sell": "/dfs/group/800463/data/xdb_data_lag3_new/saturn_sell/",
    "metis": "/dfs/group/800463/data/xdb_data_lag3_new/metis/",
    "mimas": "/dfs/group/800463/data/xdb_data_lag3_new/mimas/",
    "mercury": "/dfs/group/800463/data/xdb_data_lag3_new/mercury/",
    "hotspot": "/dfs/group/800463/data/xdb_data_lag3_new/hotspot/",
}

xdb_bad_dates_set = {"20170612", "20170620", "20170622", "20171012", "20180123", "20180126", "20180323", "20180531",
                     "20190307", "20190603"}
xdb_check_range = ["20170611", "20190801"]
xdb_valid_dates_path = '/dfs/group/800463/data/xdb_data_lag3_new/valid_dates.pkl'

# 因子计算、检测、存储相关路径
saturn_s_xx = '931'
sell_s_xx = '931'
mimas_s_xx = '931'
mercury_s_xx = '919'

path_dict = {
    "saturn": {
        'TTransaction': '/data/group/800463/data/project2_prod/everyday_Data/transaction/',
        'TTickab': '/data/group/800463/data/project2_prod/everyday_Data/tick/',
        'TOrder': '/data/group/800463/data/project2_prod/everyday_Data/order_cs/',
        'T1mTransaction': '/data/group/800463/data/project2_prod/everyday_Data_931/transaction/',
        'T1mTickab': '/data/group/800463/data/project2_prod/everyday_Data_931/tick/',
        'T1mTick1s':'/dfs/group/800463/data/project2_prod/everyday_Data_931/tick1s_cs/',
        'T1mCancel':'/dfs/group/800463/data/project2_prod/everyday_Data_931/cancelprice_cs/',
        'T1mTickfull': '/dfs/group/800463/data/project2_prod/everyday_Data_931/tickfull_cs/',
        'T1mTickfulladdorder': '/dfs/group/800463/data/project2_prod/everyday_Data_931/tickfulladdorder_cs/',
        'T1mOrder': '/data/group/800463/data/project2_prod/everyday_Data_931/order_cs/',
        'T10mTransaction': '/data/group/800463/data/project2_prod/everyday_Data_940/transaction/',
        'T10mTickab': '/data/group/800463/data/project2_prod/everyday_Data_940/tick/',
        'TTransaction_cs': '/data/group/800463/data/project2_prod/everyday_Data/transaction_cs/',
        'TTickab_cs': '/data/group/800463/data/project2_prod/everyday_Data/tick_cs/',
        'TOrder_cs': '/data/group/800463/data/project2_prod/everyday_Data/order_cs/',
        'T1mTransaction_cs': '/data/group/800463/data/project2_prod/everyday_Data_931/transaction_cs/',
        'T1mTickab_cs': '/data/group/800463/data/project2_prod/everyday_Data_931/tick_cs/',
        'T1mTick1s_cs': '/dfs/group/800463/data/project2_prod/everyday_Data_931/tick1s_cs/',
        'T1mCancel_cs': '/dfs/group/800463/data/project2_prod/everyday_Data_931/cancelprice_cs/',
        'T1mTickfull_cs': '/dfs/group/800463/data/project2_prod/everyday_Data_931/tickfull_cs/',
        'T1mTickfulladdorder_cs': '/dfs/group/800463/data/project2_prod/everyday_Data_931/tickfulladdorder_cs/',
        'T1mOrder_cs': '/data/group/800463/data/project2_prod/everyday_Data_931/order_cs/',
        'T10mTransaction_cs': '/data/group/800463/data/project2_prod/everyday_Data_940/transaction_cs/',
        'T10mTickab_cs': '/data/group/800463/data/project2_prod/everyday_Data_940/tick_cs/',
        'Basic': '/data/group/800463/data/project2_public/factor_lib/Basic_closed_hf_finish_20160101_20191231.h5',
    },
    # ToDo 生成低频策略的全部类型因子计算所需数据
'''
/dfs/user/015585/00_hotspot/basic_files/factor_files/
/dfs/user/020412/团队分享/for_qyh/hotspot
'''
    "sell": {
        'TTransaction': '/data/group/800463/data/project2_prod/everyday_Data/transaction/',
        'TTickab': '/data/group/800463/data/project2_prod/everyday_Data/tick/',
        'TOrder': '/data/group/800463/data/project2_prod/everyday_Data/order_cs/',
        'T1mTransaction': '/data/group/800463/data/project2_prod/everyday_Data_931/transaction/',
        'T1mTickab': '/data/group/800463/data/project2_prod/everyday_Data_931/tick/',
        'T1mTickfull':'/dfs/group/800463/data/project2_prod/everyday_Data_931/tickfull_cs/',
        'T1mTickfulladdorder':'/dfs/group/800463/data/project2_prod/everyday_Data_931/tickfulladdorder_cs/',
        'T1mTick1s': '/dfs/group/800463/data/project2_prod/everyday_Data_931/tick1s_cs/',
        'T1mCancel': '/dfs/group/800463/data/project2_prod/everyday_Data_931/cancelprice_cs/',
        'T1mOrder': '/data/group/800463/data/project2_prod/everyday_Data_931/order_cs/',
        'T10mTransaction': '/data/group/800463/data/project2_prod/everyday_Data_940/transaction/',
        'T10mTickab': '/data/group/800463/data/project2_prod/everyday_Data_940/tick/',
        'TTransaction_cs': '/data/group/800463/data/project2_prod/everyday_Data/transaction_cs/',
        'TTickab_cs': '/data/group/800463/data/project2_prod/everyday_Data/tick_cs/',
        'TOrder_cs': '/data/group/800463/data/project2_prod/everyday_Data/order_cs/',
        'T1mTransaction_cs': '/data/group/800463/data/project2_prod/everyday_Data_931/transaction_cs/',
        'T1mTickab_cs': '/data/group/800463/data/project2_prod/everyday_Data_931/tick_cs/',
        'T1mTick1s_cs': '/dfs/group/800463/data/project2_prod/everyday_Data_931/tick1s_cs/',
        'T1mCancel_cs': '/dfs/group/800463/data/project2_prod/everyday_Data_931/cancelprice_cs/',
        'T1mTickfull_cs': '/dfs/group/800463/data/project2_prod/everyday_Data_931/tickfull_cs/',
        'T1mTickfulladdorder_cs': '/dfs/group/800463/data/project2_prod/everyday_Data_931/tickfulladdorder_cs/',
        'T1mOrder_cs': '/data/group/800463/data/project2_prod/everyday_Data_931/order_cs/',
        'T10mTransaction_cs': '/data/group/800463/data/project2_prod/everyday_Data_940/transaction_cs/',
        'T10mTickab_cs': '/data/group/800463/data/project2_prod/everyday_Data_940/tick_cs/',
        'Basic': '/data/group/800463/data/projectS_public/factor_lib/Basic_closed_hf_finish_20160101_20191231.h5'
    },
    "jupiter": {
        'TTransaction': '/data/group/800463/data/project1_prod/transaction_zt_bs_ezt/',
        'TTickab': '/data/group/800463/data/project1_prod/tickab_zt/',
        'TTickfull': '/dfs/group/800463/data/project1_prod/tickfull_jupiter/',
        'TTickfulladdorder': '/dfs/group/800463/data/project1_prod/tickfulladdorder_jupiter/',
        'TTick1s':'/dfs/group/800463/data/project1_prod/tick1s_jupiter/',
        'TCancel':'/dfs/group/800463/data/project1_prod/cancel_jupiter/',
        'TCancelprice':'/dfs/group/800463/data/project1_prod/cancelprice_jupiter/',
        'LastTouchTTick': '/data/group/800463/data/project1_prod/last_touch_t_tick/',
        'MarketTTick': '/data/group/800463/data/project1_prod/market_t_tick/',
        'Market1TTick': '/data/group/800463/data/project1_prod/market_t_tick/',
        'MarketIndTTick': '/data/group/800463/data/project1_prod/market_t_tick/',
        "Basic": '/data/group/800463/data/project1_public/factor_lib_v2/Basic_zt_20150901_20191231.h5',
    },
    "europa": {
        'TTransaction': '/data/group/800463/data/project1_prod/transaction_europa/',
        'TTickab': '/data/group/800463/data/project1_prod/tick_europa/',
        'TTickfull':'/dfs/group/800463/data/project1_prod/tickfull_europa/',
        'TTickfulladdorder':'/dfs/group/800463/data/project1_prod/tickfulladdorder_europa/',
        'TTick1s':'/dfs/group/800463/data/project1_prod/tick1s_europa/',
        'TCancel':'/dfs/group/800463/data/project1_prod/cancel_europa/',
        'TCancelprice':'/dfs/group/800463/data/project1_prod/cancelprice_europa/',
        'TOrder': '/data/group/800463/data/project1_prod/order_europa/',
        'LastTouchTTick': '/data/group/800463/data/project1_prod/last_touch_t_tick/',
        'MarketTTick': '/data/group/800463/data/project1_prod/market_t_tick/',
        'Market1TTick': '/data/group/800463/data/project1_prod/market_t_tick/',
        'MarketIndTTick': '/data/group/800463/data/project1_prod/market_t_tick/',
        "Basic": '/data/group/800463/data/project1_public/factor_lib_v3/Basic_zt_001_20150901_20191231.h5'
    },
    "hotspot": {
        'TTransaction': '/dfs/user/015585/00_hotspot/TTransaction35/',
        'TTickab': '/dfs/user/015585/00_hotspot/TTickab35/',
        "Basic": '/dfs/user/015585/00_hotspot/basic_files/factor_files/pct35/md2_20250512_20150901_20231231.h5'
    },

    "mimas": {
        'NextTickab': '/data/group/800463/data/project2_prod/everyday_Data/next_tick_cs/',
        'NextTickab_cs': '/data/group/800463/data/project2_prod/everyday_Data/next_tick_cs/',
        'NextTransaction': '/data/group/800463/data/project2_prod/everyday_Data/next_transaction_cs/',
        'NextTransaction_cs': '/data/group/800463/data/project2_prod/everyday_Data/next_transaction_cs/',
        'Next1mTickab': '/data/group/800463/data/project2_prod/everyday_Data_931/next_tick_cs/',
        'Next1mTickab_cs': '/data/group/800463/data/project2_prod/everyday_Data_931/next_tick_cs/',
        'Next1mTransaction': '/data/group/800463/data/project2_prod/everyday_Data_931/next_transaction_cs/',
        "Next1mTransaction_cs": '/data/group/800463/data/project2_prod/everyday_Data_931/next_transaction_cs/',
        "Next1mTickfull":'/dfs/group/800463/data/project2_prod/everyday_Data_931/next_tickfull_cs/',
        "Next1mTickfulladdorder":'/dfs/group/800463/data/project2_prod/everyday_Data_931/next_tickfulladdorder_cs/',
        'Next1mTick1s':'/dfs/group/800463/data/project2_prod/everyday_Data_931/next_tick1s_cs/',
        'Next1mCancel': '/dfs/group/800463/data/project2_prod/everyday_Data_931/next_cancelprice_cs/',
        'Next1mTickfull_cs': '/dfs/group/800463/data/project2_prod/everyday_Data_931/next_tickfull_cs/',
        "Next1mTickfulladdorder_cs": '/dfs/group/800463/data/project2_prod/everyday_Data_931/next_tickfulladdorder_cs/',
        'Next1mTick1s_cs': '/dfs/group/800463/data/project2_prod/everyday_Data_931/next_tick1s_cs/',
        'Next1mCancel_cs': '/dfs/group/800463/data/project2_prod/everyday_Data_931/next_cancelprice_cs/',
        "Basic": '/data/group/800463/data/project2_public/next_factor_lib/Basic_next_hf_finish_20160101_20191231.h5',
    },
    "metis": {  # TODO
        'TTransaction': '/data/group/800463/data/project1_prod/transaction_jupiter/',
        'TTickab': '/data/group/800463/data/project1_prod/tick_jupiter/',
        'TOrder': '/data/group/800463/data/project1_prod/order_jupiter/',
        'TTransaction_Metis': '/data/group/800463/data/project1_prod/transaction_metis/',
        'TTickab_Metis': '/data/group/800463/data/project1_prod/tickab_metis/',
        'TTransaction_MetisAll': '/data/group/800463/data/project1_prod/transaction_metis_all/',
        'TTickab_MetisAll': '/data/group/800463/data/project1_prod/tickab_metis_all/',
        "TOrder_MetisAll": '/data/group/800463/data/project1_prod/order_metis_all/',
        'TTickfull_MetisAll':'/dfs/group/800463/data/project1_prod/tickfull_metis_all/',
        'TTickfulladdorder_MetisAll': '/dfs/group/800463/data/project1_prod/tickfulladdorder_metis_all/',
        'TTick1s_MetisAll': '/dfs/group/800463/data/project1_prod/tick1s_metis_all/',
        'TCancel_MetisAll': '/dfs/group/800463/data/project1_prod/cancel_metis_all/',
        'TCancelprice_MetisAll': '/dfs/group/800463/data/project1_prod/cancelprice_metis_all/',
        'LastTouchTTick': '/data/group/800463/data/project1_prod/last_touch_t_tick/',
        "MarketTTick": '/data/group/800463/data/project1_prod/market_t_tick/',
        "Market1TTick": '/data/group/800463/data/project1_prod/market_t_tick/',
        "MarketIndTTick": '/data/group/800463/data/project1_prod/market_t_tick/',

        "Basic": '/dfs/group/800463/data/project1_public/factor_lib_metis/Basic_metis_20160101_20191231.h5',
    },

    "mercury": {
        'TTickab919': '/dfs/group/800463/data/mercury/everyday_Data/tick919/',
        'Basic': '/dfs/group/800463/data/mercury/ff_data/Basic/basic_dt_new.h5',
    },
}

# 预检测相关路径
precheck_path_dict = {
    "sell": {

        "precheck_basic_path": '/data/group/800463/data/projectS_public/factor_lib/sft_init_normal931_filter_20160101_20191231.h5',
        "long_interval": ['20160101', '20191231'],
        "short_interval_list": ['20160104', '20180601', '20180604', '20191230', '20191231'],
    },
    "saturn": {

        "precheck_basic_path": '/data/group/800463/data/project2_public/factor_lib/sft_init_normal931_filter_20160101_20191231.h5',
        "long_interval": ['20160101', '20191231'],
        "short_interval_list": ['20160104', '20160105', '20160106', '20160107', '20180601', '20180604', '20191227',
                                '20191230', '20191231'],
    },
    "mercury": {

        "precheck_basic_path": '/dfs/group/800463/data/mercury/ff_data/Basic/basic_dt_new.h5',
        "long_interval": ['20160101', '20201231'],
        "short_interval_list": ['20160104', '20160105', '20160106', '20160107', '20180601', '20180604', '20201229',
                                '20201230', '20201231'],
    },
    "jupiter": {

        "precheck_basic_path": '/data/group/800463/data/project1_public/factor_lib_v2/filter_df_jupiter_20150901_20191231.pkl',
        "long_interval": ["20160101", "20191231"],
        "short_interval_list": ['20160104', '20160105', '20160106', '20160107', '20180601', '20180604', '20191227',
                                '20191230', '20191231'],
    },
    "europa": {

        "precheck_basic_path": '/data/group/800463/data/project1_public/factor_lib_v3/filter_df_europa_20150901_20191231.pkl',
        "long_interval": ['20160101', '20191231'],
        "short_interval_list": ['20160104', '20160105', '20160106', '20160107', '20180601', '20180604', '20191227',
                                '20191230', '20191231'],
    },
    "mimas": {
        "precheck_basic_path": '/data/group/800463/data/project2_public/next_factor_lib/sft_basic_next_filter_20160101_20191231.h5',
        "long_interval": ['20160101', '20211231'],
        "short_interval_list": ['20160105', '20160106', '20160107', '20160108', '20180601', '20180604', '20191227',
                                '20191230', '20191231', '20211230', '20211231'],

    },
    "metis": {
        "precheck_basic_path": '/dfs/group/800463/data/project1_public/factor_lib_metis/filter_df_metis_20150901_20191231.pkl',
        "long_interval": ['20160101', '20211231'],
        "short_interval_list": ['20160104', '20160105', '20160106', '20160107', '20190925', '20190926', '20190927',
                                '20190930', '20190715', '20190716', '20190717', '20190718', '20190719', '20190722',
                                '20190723', '20190724', '20190725', '20190726', '20190729', '20190730', '20190731',
                                '20211227', '20211228', '20211229', '20211230', '20211231'],
    },
    "hotspot":{
        "precheck_basic_path": '/dfs/user/015585/00_hotspot/basic_files/factor_files/pct35/md2_20250512_20150901_20231231.pkl',
        "long_interval": ['20160101', '20191231'],
        "short_interval_list": ['20160104', '20160105', '20160106', '20160107', '20180601', '20180604', '20191227',
                                '20191230', '20191231'],
    }
}
