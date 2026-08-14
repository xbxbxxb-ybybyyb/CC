# this file contains base path settings for fefactor framework

import os
from enum import Enum, unique


@unique
class RunMode(Enum):
    research = 0,
    factor_warehouse = 1,
    prod_prepare = 2,
    daily_update = 3


valid_strategy_names = ["saturn", "sell", "jupiter", 'europa', 'metis', 'mimas', "mercury","ceres", "neptune", "neptunelong"]

# TODO 生产数据默认路径
prod_data_dir = "/data/user/018107/"
prod_prep_date = ""

# TODO 每日更新默认路径
daily_update_dir = ""

# # TODO xdb数据根路径
# xdb_path = {
#     "jupiter": "/dfs/group/800463/data/xdb_data_lag3/europa_jupiter/",
#     "europa": "/dfs/group/800463/data/xdb_data_lag3/europa_jupiter/",
#     "saturn": "/dfs/group/800463/data/xdb_data_lag3/saturn_sell/",
#     "sell": "/dfs/group/800463/data/xdb_data_lag3/saturn_sell/",
#     "metis": "/dfs/group/800463/data/xdb_data_lag3/metis/",
#     "mimas": "/dfs/group/800463/data/xdb_data_lag3/mimas/",
#     "mercury": "",
#     "ceres": "",
# }

# 用于分段压缩测试
xdb_path_xdbformat = {
    "jupiter": "/dfs/group/800463/data/xdb_data_lag3_new/europa_jupiter/",
    "europa": "/dfs/group/800463/data/xdb_data_lag3_new/europa_jupiter/",
    "saturn": "/dfs/group/800463/data/xdb_data_lag3_new/saturn_sell/",
    "sell": "/dfs/group/800463/data/xdb_data_lag3_new/saturn_sell/",
    "metis": "/dfs/group/800463/data/xdb_data_lag3_new/metis/",
    "mimas": "/dfs/group/800463/data/xdb_data_lag3_new/mimas/",
    "mercury": "/dfs/group/800463/data/xdb_data_lag3_new/mercury/",
    "ceres": "",
    "neptune": "/dfs/group/800463/data/xdb_data_lag3_new/neptune/",
    "neptunelong": "/dfs/group/800463/data/xdb_data_lag3_new/neptunelong/",
}

xdb_bad_dates_set = {"20170612", "20170620", "20170622", "20171012", "20180123", "20180126", "20180323", "20180531",
                 "20190307", "20190603"}
xdb_check_range = ["20170611", "20190801"]
xdb_valid_dates_path = '/dfs/group/800463/public/xdb_data_lag3_new/valid_dates.pkl'

# 因子计算、检测、存储相关路径
saturn_s_xx = '931'
neptune_s_xx = '931'
neptunelong_s_xx = '931' # TODO
sell_key = 'normal931'
sell_scene = 'all_scene'
sell_s_xx = sell_key[-3:]

mimas_s_xx = '931'
ceres_s_xx = '931'

path_dict = {
    "neptune": {
        "factor_value_path": '/data/user/023859/factor_zooZZ/all_factor/%s/' % neptune_s_xx,
        "factor_precheck_path": '/data/user/023859/factor_zooZZ/all_factor_check/%s/' % neptune_s_xx,
        "factor_cost_path": '/data/user/023859/factor_zooZZ/all_cost/%s/' % neptune_s_xx,
        "factor_test_path": '/data/user/023859/factor_zooZZ/all_factor_test/all_scene/%s/' % neptune_s_xx,

        'T1mTransaction': '/dfs/group/800463/data/projectZZ1000_prod/everyday_Data_931/transaction_cs/',
        'T1mTickab': '/dfs/group/800463/data/projectZZ1000_prod/everyday_Data_931/tick_cs/',
        'T1mTick1s': '/dfs/group/800463/data/projectZZ1000_prod/everyday_Data_931/tick1s_cs/',
        'T1mCancel': '/dfs/group/800463/data/projectZZ1000_prod/everyday_Data_931/cancelprice_cs/',
        'T1mTickfulladdorder': '/dfs/group/800463/data/projectZZ1000_prod/everyday_Data_931/tickfulladdorder_cs/',
        'T1mOrder': '/dfs/group/800463/data/projectZZ1000_prod/everyday_Data_931/order_cs/',

        'Basic': '/data/user/023859/factor_zooZZ/factor_lib/Basic_closed_hf_finish_20160101_20250630.h5',
        'FullBasic': '/data/user/023859/factor_zooZZ/factor_lib/Basic_closed_hf_finish_20160101_20250630.h5',
        "ProdPrepBasic": "",
        "DailyUpdateBasic": ""
    },
    "neptunelong": {
        "factor_value_path": '/data/user/023859/factor_zooZZmkt/all_factor/%s/' % neptunelong_s_xx,
        "factor_precheck_path": '/data/user/023859/factor_zooZZmkt/all_factor_check/%s/' % neptunelong_s_xx,
        "factor_cost_path": '/data/user/023859/factor_zooZZmkt/all_cost/%s/' % neptunelong_s_xx,
        "factor_test_path": '/data/user/023859/factor_zooZZmkt/all_factor_test/all_scene/%s/' % neptunelong_s_xx,

        'T1mTransaction': '/dfs/group/800463/data/projectZZmkt_prod/everyday_Data_931/transaction_cs/',
        'T1mTickab': '/dfs/group/800463/data/projectZZmkt_prod/everyday_Data_931/tick_cs/',
        'T1mTick1s': '/dfs/group/800463/data/projectZZmkt_prod/everyday_Data_931/tick1s_cs/',
        'T1mCancel': '/dfs/group/800463/data/projectZZmkt_prod/everyday_Data_931/cancelprice_cs/',
        'T1mTickfulladdorder': '/dfs/group/800463/data/projectZZmkt_prod/everyday_Data_931/tickfulladdorder_cs/',
        'T1mOrder': '/dfs/group/800463/data/projectZZmkt_prod/everyday_Data_931/order_cs/',

        'Basic': '/data/user/023859/factor_zooZZmkt/factor_lib/Basic_closed_hf_finish_20160101_20250630.h5',
        'FullBasic': '/data/user/023859/factor_zooZZmkt/factor_lib/Basic_closed_hf_finish_20160101_20250630.h5',
        "ProdPrepBasic": "",
        "DailyUpdateBasic": ""
    },


    "saturn": {
        "factor_value_path": '/dfs/user/018107/factor_zoo2/all_factor/%s/' % saturn_s_xx,
        "factor_precheck_path": '/dfs/user/018107/factor_zoo2/all_factor_check/%s/' % saturn_s_xx,
        "factor_cost_path": "/dfs/user/018107/factor_zoo2/all_cost/%s/" % saturn_s_xx,
        "factor_test_path": '/dfs/user/018107/factor_zoo2/all_factor_test/all_scene/%s/' % saturn_s_xx,

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

        'Basic': "/data/group/800463/project/project2_prod/daily_data/Basic/Basic_closed_hf_finish.h5",
        'FullBasic': "/data/group/800463/project/project2_prod/daily_data/Basic/Basic_closed_hf_finish.h5",
        "ProdPrepBasic": "/data/group/800463/project/project2_prod/daily_data/{}_v6/Basic_night_finish_{}_{}.h5",
        "DailyUpdateBasic": "/data/group/800463/project/project2_prod/daily_data/{}_v6/Basic_closed_hf_finish_{}_{}.h5"
    },
    "sell": {
        "factor_value_path": '/data/user/018107/factor_zooS/all_factor/%s/' % sell_s_xx,
        "factor_precheck_path": '/data/user/018107/factor_zooS/pre_check/%s/' % sell_s_xx,
        "factor_cost_path": "/data/user/018107/factor_zooS/all_cost/%s/" % sell_s_xx,
        "factor_test_path": '/data/user/018107/factor_zooS/all_factor_test/%s/%s/' % (sell_scene, sell_s_xx),

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

        'Basic': "/data/group/800463/project/project2_prod/daily_data/Basic/Basic_closed_hf_finish.h5",
        # 因子计算
        'FullBasic': "/data/group/800463/project/project2_prod/daily_data/Basic/Basic_closed_hf_finish.h5",
        # 为xdb数据提供全部股票池
        "ProdPrepBasic": "/data/group/800463/project/projectS_prod/daily_data/{}_v1/Basic_night_finish_{}_{}.h5",
        # 盘前准备basic
        "DailyUpdateBasic": "/data/group/800463/project/projectS_prod/daily_data/{}_v1/Basic_closed_hf_finish_{}_{}.h5"
        # 每日更新basic
    },
    "jupiter": {
        "factor_value_path": '/data/user/018107/factor_zoo1/all_factor/jupiter/',
        "factor_precheck_path": '/data/user/018107/factor_zoo1/all_precheck/jupiter/',
        "factor_cost_path": "/data/user/018107/factor_zoo1/all_cost/jupiter/",
        "factor_test_path": '/data/user/018107/factor_zoo1/all_factortest/jupiter/all/',

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

        "Basic": "/data/user/018107/factor_zoo1/left_v2310/Basic_zt/Basic_zt.h5",
        'FullBasic': "/data/user/018107/factor_zoo1/left_v2310/Basic_zt/Basic_zt.h5",
        "ProdPrepBasic": "/data/group/800463/project/project1_prod/left_v2212/daily_data/{}/BasicInf_zt_{}_{}.h5",
        "DailyUpdateBasic": "/data/group/800463/project/project1_prod/left_v2212/daily_data/{}/Basic_zt_{}_{}.h5"
    },
    "europa": {
        "factor_value_path": '/data/user/018107/factor_zoo1/all_factor/europa/',
        "factor_precheck_path": '/data/user/018107/factor_zoo1/all_precheck/europa/',
        "factor_cost_path": "/data/user/018107/factor_zoo1/all_cost/europa/",
        "factor_test_path": '/data/user/018107/factor_zoo1/all_factortest/europa/all/',

        'TTransaction': '/data/group/800463/data/project1_prod/transaction_europa/',
        'TTickab': '/data/group/800463/data/project1_prod/tick_europa/',
        'TTickfull':'/dfs/group/800463/data/project1_prod/tickfull_europa/',
        'TTickfulladdorder':'/dfs/group/800463/data/project1_prod/tickfulladdorder_europa/',
        'TTick1s':'/dfs/group/800463/data/project1_prod/tick1s_europa/',
        'TCancel':'/dfs/group/800463/data/project1_prod/cancel_europa/',
        'TCancelprice':'/dfs/group/800463/data/project1_prod/cancelprice_europa/',
        'TOrder': '/data/group/800463/data/project1_prod/order_europa/',
        'LastTouchTTick': '/data/group/800463/data/project1_prod/last_touch_t_tick/',
        'MarketTTick': '/dfs/group/800463/data/project1_prod/mkt_t_tick/',
        'Market1TTick': '/dfs/group/800463/data/project1_prod/mkt_t_tick/',
        'MarketIndTTick': '/dfs/group/800463/data/project1_prod/mkt_t_tick/',
        'MarketTTick_ALL': '/dfs/group/800463/data/project1_prod/mkt_t_tick_all/',

        "Basic": "/data/group/800463/project/project1_prod/left_v2310/Basic_zt_test/Basic_zt_001.h5",
        'FullBasic': "/data/group/800463/project/project1_prod/left_v2310/Basic_zt_test/Basic_zt_001.h5",
        "ProdPrepBasic": "/data/group/800463/project/project1_prod/left_v2310/daily_data/{}/BasicInf_zt_{}_{}.h5",
        "DailyUpdateBasic": "/data/group/800463/project/project1_prod/left_v2310/daily_data/{}/Basic_zt_001_{}_{}.h5"
    },
    "mimas": {  # TODO
        "factor_value_path": '/data/user/018107/factor_zoo2/next_all_factor/%s/'%(mimas_s_xx),
        "factor_precheck_path": '/data/user/018107/factor_zoo2/next_all_factor_check/%s/'%(mimas_s_xx),
        "factor_cost_path": '/data/user/018107/factor_zoo2/next_all_factor_cost/all_scene/%s/'%mimas_s_xx,
        "factor_test_path": '/data/user/018107/factor_zoo2/next_all_factor_test/all_scene/%s/'%mimas_s_xx,

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
        'MarketTTick_Ceres': '/dfs/group/800463/data/project3_prod/market_t_tick/',

        "Basic": "/data/user/018107/factor_zoo2/history/20160101_20230625/Basic_next_hf_finish_20160101_20230625.h5",
        'FullBasic': "/data/user/018107/factor_zoo2/history/20160101_20230625/Basic_next_hf_finish_20160101_20230625.h5",
        "ProdPrepBasic": "",
        "DailyUpdateBasic": ""
    },
    "metis": {  # TODO
        "factor_value_path": '/dfs/user/018107/factor_zoo1/all_factor/metis/',
        "factor_precheck_path": '/dfs/user/018107/factor_zoo1/all_precheck/metis/',
        "factor_cost_path": "/dfs/user/018107/factor_zoo1/all_cost/metis/",
        "factor_test_path": '/dfs/user/018107/factor_zoo1/all_factortest/metis/all/',

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

        "Basic": "/data/group/800463/project/project1_prod/left_v2212/Basic_metis/Basic_metis.h5",
        'FullBasic': "/data/group/800463/project/project1_prod/left_v2212/Basic_metis/Basic_metis.h5",
        "ProdPrepBasic": "/data/group/800463/project/project1_prod/left_v2212/daily_data/{}/BasicInf_zt_{}_{}.h5",
        "DailyUpdateBasic": "/data/group/800463/project/project1_prod/left_v2212/daily_data/{}/Basic_metis_{}_{}.h5"
    },

    "mercury": {  # TODO
        "factor_value_path": '',
        "factor_precheck_path": '',
        "factor_cost_path": "",
        "factor_test_path": '',

        'TTickab919': '/dfs/group/800463/data/mercury/everyday_Data/tick919/',
        'TTickab': '',
        'TOrder': '',
        'TTransaction_Metis': '',
        'TTickab_Metis': '',
        'TTransaction_MetisAll': '',
        'TTickab_MetisAll': '',
        "TOrder_MetisAll": '',
        'LastTouchTTick': '',
        "MarketTTick": '',
        "Market1TTick": '',
        "MarketIndTTick": '',

        "Basic": "",
        'FullBasic': "",
        "ProdPrepBasic": "",
        "DailyUpdateBasic": ""
    },

    "ceres": {
        "factor_value_path": '/data/user/018107/factor_zoo3/all_factor/%s/' % ceres_s_xx,
        "factor_precheck_path": '/data/user/018107/factor_zoo3/all_factor_check/%s/' % ceres_s_xx,
        "factor_cost_path": "/data/user/018107/factor_zoo3/all_cost/%s/" % ceres_s_xx,
        "factor_test_path": '/data/user/018107/factor_zoo3/all_factor_test/all/%s/' % ceres_s_xx,

        'TTransaction': '/data/group/800463/data/project3_prod/everyday_Data/transaction_cs/',
        'TTickab': '/data/group/800463/data/project3_prod/everyday_Data/tick_cs/',
        'TOrder':'/data/group/800463/data/project3_prod/everyday_Data/order_cs/',
        'T1mTransaction': '/data/group/800463/data/project3_prod/everyday_Data_931/transaction_cs/',
        'T1mTickab': '/data/group/800463/data/project3_prod/everyday_Data_931/tick_cs/',
        'T1mOrder': '/data/group/800463/data/project3_prod/everyday_Data_931/order_cs/',
        'TTransaction_cs': '/data/group/800463/data/project3_prod/everyday_Data/transaction_cs/',
        'TTickab_cs': '/data/group/800463/data/project3_prod/everyday_Data/tick_cs/',
        'TOrder_cs':'/data/group/800463/data/project3_prod/everyday_Data/order_cs/',
        'T1mTransaction_cs': '/data/group/800463/data/project3_prod/everyday_Data_931/transaction_cs/',
        'T1mTickab_cs': '/data/group/800463/data/project3_prod/everyday_Data_931/tick_cs/',
        'T1mOrder_cs': '/data/group/800463/data/project3_prod/everyday_Data_931/order_cs/',
        'MarketTTick_Ceres': '/dfs/group/800463/data/project3_prod/market_t_tick/',

        'Basic': "/data/user/018107/factor_zoo3/history/20160101_20240726/Basic_closed_hf_finish_20160101_20240726.h5",
        'FullBasic': "/data/user/018107/factor_zoo3/history/20160101_20240726/Basic_closed_hf_finish_20160101_20240726.h5",
        "ProdPrepBasic": "/data/group/800463/project/project3_prod/daily_data/{}_v3/Basic_night_finish_{}_{}.h5",
        "DailyUpdateBasic": "/data/group/800463/project/project3_prod/daily_data/{}_v3/Basic_closed_hf_finish_{}_{}.h5"
    },
}

# 预检测相关路径
precheck_path_dict = {
    "neptune": {

        "precheck_basic_path": '/data/user/023859/factor_zooZZ/factor_lib/sft_basic_formal_931_20160101_20241231.h5',
        "long_interval": ['20170110', '20211231'],
        "short_interval_list": ['20170110', '20170111', '20170112', '20170113', '20180601', '20180604', '20191227',
                                '20191230', '20191231', '20211230', '20211231'],
    },
    "neptunelong": {

        "precheck_basic_path": '/data/user/023859/factor_zooZZmkt/factor_lib/sft_basic_formal_931_20160101_20211231.h5',
        "long_interval": ['20170110', '20211231'],
        "short_interval_list": ['20170110', '20170111', '20170112', '20170113', '20180601', '20180604', '20191227',
                                '20191230', '20191231', '20211230', '20211231'],
    },
    "sell": {

        "precheck_basic_path": '/data/user/018107/factor_zooS/factor_lib_v2/931/sft_init_normal931_filter_20160101_20211231.h5',
        "long_interval": ['20160101', '20211231'],
        "short_interval_list": ['20160104', '20180601', '20180604', '20191230', '20191231', '20211230', '20211231'],
    },
    "saturn": {

        "precheck_basic_path": '/dfs/user/018107/factor_zoo2/factor_lib/sft_init_normal931_filter_20160101_20211231.h5',
        "long_interval": ['20160101', '20211231'],
        "short_interval_list": ['20160104', '20160105', '20160106', '20160107', '20180601', '20180604', '20191227',
                                '20191230',
                                '20191231', '20211230', '20211231'],
    },
    "jupiter": {

        "precheck_basic_path": '/data/user/018107/factor_zoo1/factor_lib_v3/filter_df_jupiter_20150901_20211231.pkl',
        "long_interval": ['20160101', '20211231'],
        "short_interval_list": ['20160104', '20160105', '20160106', '20160107', '20190925', '20190926', '20190927',
                                '20190930', '20190715', '20190716', '20190717', '20190718', '20190719', '20190722',
                                '20190723', '20190724', '20190725', '20190726', '20190729', '20190730', '20190731',
                                '20211227', '20211228', '20211229', '20211230', '20211231'],
    },
    "europa": {

        "precheck_basic_path": '/data/user/018107/factor_zoo1/factor_lib_v3/filter_df_europa_20150901_20211231.pkl',
        "long_interval": ['20160101', '20211231'],
        "short_interval_list": ['20160104', '20160105', '20160106', '20160107', '20190925', '20190926', '20190927',
                                '20190930', '20190715', '20190716', '20190717', '20190718', '20190719', '20190722',
                                '20190723', '20190724', '20190725', '20190726', '20190729', '20190730', '20190731',
                                '20211227', '20211228', '20211229', '20211230', '20211231'],
    },
    "mimas": {
        "precheck_basic_path": '/data/group/800463/data/project2_public/next_factor_lib/sft_basic_next_filter_20160101_20211231.h5',
        "long_interval": ['20160101', '20211231'],
        "short_interval_list": ['20160105', '20160106', '20160107', '20160108', '20180601', '20180604', '20191227',
                                '20191230', '20191231', '20211230', '20211231'],

    },
    "metis": {
        "precheck_basic_path": '/dfs/group/800463/data/project1_public/factor_lib_metis/filter_df_metis_20150901_20211231.pkl',
        "long_interval": ['20160101', '20211231'],
        "short_interval_list": ['20160104', '20160105', '20160106', '20160107', '20190925', '20190926', '20190927',
                                '20190930', '20190715', '20190716', '20190717', '20190718', '20190719', '20190722',
                                '20190723', '20190724', '20190725', '20190726', '20190729', '20190730', '20190731',
                                '20211227', '20211228', '20211229', '20211230', '20211231'],
    },
    "mercury": {
        "precheck_basic_path": '',
        "long_interval": ['20160101', '20211231'],
        "short_interval_list": [],
    },
    "ceres": {
        "precheck_basic_path": '',
        "long_interval": ['20160101', '20211231'],
        "short_interval_list": [],
    }

}

# 因子测试相关路径


# 入库相关路径

# 20200205之前的所有因子的因子值
all_factor_for_left = '/data/user/018107/factor_zoo1/factor_bank/europa/20231102/all_factor_df.pkl'

warehouse_settings_dict = {
    # europa settings
    "europa": {
        "in_interval": [20160101, 20191231],  # 样本内区间
        "out_interval": [20190101, 20201231],  # 样本外区间
        "max_corr": 0.7,  # 库内因子允许的最大相关性
        "all_factors_list": '/data/user/018107/factor_zoo1/alternate_factor_inf.xlsx',
        # excel形式存放所有因子的信息（名称、得分、IC、入库是否成功）等
        "all_factor_for_left": "/data/user/018107/factor_zoo1/factor_bank/europa/20231102/all_factor_df.pkl",
        "res_path": '/data/user/018107/factor_zoo1/factor_lib_v3/',  # 结果地址：库内的所有因子的因子值
        "res_public_path": '/data/group/800463/data/project1_public/factor_lib_v3/',  # 公共结果地址
    },
    # sell settings
    "sell": {

        "in_interval": [20160101, 20191231],  # 样本内区间
        "out_interval": [20190101, 20201231],  # 样本外区间
        "max_corr": 0.7,
        "basic_factor_path": '/data/user/018107/factor_zoo2/history/20160101_20211231/Basic_closed_hf_finish_20160101_20211231.h5',
        "all_factors_list": '/data/user/018107/factor_zooS/all_factor_inf.xlsx',
        "res_path": '/data/user/018107/factor_zooS/factor_lib_v2/%s/' % (sell_s_xx),
        "res_public_path": '/data/group/800463/data/project1_public/factor_lib_v3/',  # 公共结果地址
    },
    # saturn settings
    "saturn": {
        "in_interval": [20160101, 20191231],
        "out_interval": [20190101, 20201231],
        "max_corr": 0.7,
        "all_factors_list": '/dfs/user/018107/factor_zoo2/all_factor_inf.xlsx',
        "res_path": '/dfs/user/018107/factor_zoo2/factor_lib/',
        "res_public_path": '/dfs/group/800463/data/project2_public/factor_lib/',  # 公共结果地址
        "sft_basic_path": '/dfs/user/018107/factor_zoo2/history/20160101_20211231/sft_basic_origin_20160101_20211231.h5',
        # 初始地址
        "basic_factor_path": '/dfs/user/018107/factor_zoo2/history/20160101_20211231/Basic_closed_hf_finish_20160101_20211231.h5'
    },
    "mimas": {
        "in_interval": [20160101, 20191231],  # 样本内区间
        "out_interval": [20190101, 20201231],  # 样本外区间
        "max_corr": 0.7,  # 库内因子允许的最大相关性
        "all_factors_list": '/data/user/018107/factor_zoo2/next_all_factor/all_factor_inf.xlsx',
        # excel形式存放所有因子的信息（名称、得分、IC、入库是否成功）等
        "all_factor_for_left": '/data/user/018107/factor_zoo2/history/20160101_20230625/sft_all_next_20160101_20230625.pkl',
        "res_path": '/data/user/018107/factor_zoo2/next_factor_lib/',  # 结果地址：库内的所有因子的因子值
        "res_public_path": '/data/group/800463/data/project2_public/next_factor_lib/',  # 公共结果地址
        "sft_basic_path": '/data/user/018107/factor_zoo2/history/20160101_20230625/sft_basic_next_20160101_20230625.h5',
        # 初始地址
        "basic_factor_path": '/dfs/user/018107/factor_zoo2/history/20160101_20211231/Basic_closed_hf_finish_20160101_20211231.h5'
    },
    "metis": {
        "in_interval": [20160101, 20191231],  # 样本内区间
        "out_interval": [20190101, 20201231],  # 样本外区间
        "max_corr": 0.7,  # 库内因子允许的最大相关性
        "jupiter_cutdate": 20231219,
        "jupiter_all_factors_list": '/dfs/user/018107/factor_zoo1/alternate_factor_inf.xlsx',
        "all_factors_list": '/dfs/user/018107/factor_zoo1/metis_alternate_factor_inf.xlsx',
        # excel形式存放所有因子的信息（名称、得分、IC、入库是否成功）等
        "all_factor_for_left": '/data/user/018107/factor_zoo1/factor_bank/jupiter/20231219/all_factor_df.pkl',
        "res_path": '/dfs/user/018107/factor_zoo1/factor_lib_metis/',  # 结果地址：库内的所有因子的因子值
        "res_public_path": '/dfs/group/800463/data/project1_public/factor_lib_metis/',  # 公共结果地址
        # 初始地址
        "basic_factor_path": '/dfs/user/018107/factor_zoo2/history/20160101_20211231/Basic_closed_hf_finish_20160101_20211231.h5'
    },
    # neptune settings
    "neptune": {
        "in_interval": [20170110, 20201231],
        "out_interval": [20210101, 20211231],
        "max_corr": 0.7,
        "all_factors_list": '/data/user/023859/factor_zooZZ/all_factor_inf.xlsx',
        "res_path": '/data/user/023859/factor_zooZZ/factor_lib/',
        "res_public_path": '/dfs/group/800463/public/projectZZ_public/factor_lib/',  # 公共结果地址
        "sft_basic_path": '/data/user/023859/factor_zooZZ/factor_lib/sft_basic_formal_931_20160101_20241231.h5',
        # 初始地址
        "basic_factor_path": '/data/user/023859/factor_zooZZ/factor_lib/Basic_closed_hf_finish_20160101_20250630.h5'
    },
    "neptunelong": {
        "in_interval": [20170110, 20201231],
        "out_interval": [20210101, 20211231],
        "max_corr": 0.7,
        "all_factors_list": '/data/user/023859/factor_zooZZmkt/all_factor_inf.xlsx',
        "res_path": '/data/user/023859/factor_zooZZmkt/factor_lib/',
        "res_public_path": '/dfs/group/800463/public/projectZZmkt_public/factor_lib/',  # 公共结果地址
        "sft_basic_path": '/data/user/023859/factor_zooZZmkt/factor_lib/sft_basic_formal_931_20160101_20211231.h5',
        # 初始地址
        "basic_factor_path": '/data/user/023859/factor_zooZZmkt/factor_lib/Basic_closed_hf_finish_20160101_20201231.h5'
    },
}

warehouse_daily_data_checker = {}
invalid_li = ["factor_value_path", "factor_precheck_path", "factor_cost_path", "factor_test_path",
              'Basic', 'FullBasic', "ProdPrepBasic", "DailyUpdateBasic"]
for k, v in path_dict.items():
    warehouse_daily_data_checker[k] = []
    for k1 in v.keys():
        if k1 in invalid_li:
            continue
        warehouse_daily_data_checker[k].append(k1)


# europa
# 初始地址：策略首次入库时，只保存的基础因子文件，基础因子永远在库中
warehouse_settings_dict["europa"]["sft_basic_path"] = '%s/sft_init_europa.h5' % (
    warehouse_settings_dict["europa"]["res_path"])

# sell
warehouse_settings_dict["sell"]["sft_basic_path"] = '%s/sft_init_%s_filter.h5' % (
    warehouse_settings_dict["sell"]["res_path"], sell_s_xx)

# metis
warehouse_settings_dict["metis"]["sft_basic_path"] = '%s/sft_init_metis.h5' % (
    warehouse_settings_dict["metis"]["res_path"])
