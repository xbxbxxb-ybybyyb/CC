import platform
import os

def reversed_dict(x, bijection_check=False):
    assert isinstance(x, dict)
    if bijection_check:
        assert len(set(x.values())) == len(set(x.keys()))
    return {v: k for k, v in x.items()}

# retrieve universe items
universe_mapper = {'ZZ500': 'index_500',
                   'HS300': 'index_300',
                   'SZ50' : 'index_50',
                   'alpha_index'   : 'alpha_universe',
                   'alpha_universe': 'alpha_universe'}
reversed_universe_mapper = reversed_dict(universe_mapper)

# retrieve index prices
index_mapper = {'ZZ500': '000905.SH',
                'ZZ800': '000906.SH',
                'SZ50' : '000016.SH',
                'HS300': '000300.SH',
                'alpha_index': 'alpha_index'}
reversed_index_mapper = reversed_dict(index_mapper)

# retrieve single stock weights in benchmark
weight_mapper = {'ZZ500': 'index_weight_zz500',
                 'HS300': 'index_weight_hs300',
                 'SZ50' : 'index_weight_sh50'}
reversed_weight_mapper = reversed_dict(weight_mapper)

# misc
common_dummy_period = [20100101, 20200101]

# warehouse paths & runtime
if platform.system() == 'Windows':
    private_root = r'A:/'
    public_root = r'Z:/'
    private_python_path = 'python'
elif platform.system() == 'Linux':
    private_root = '/data/user/012245'
    public_root = '/data/group/800080'
    private_python_path = '/data/user/012245/anaconda3/bin/python'
else:
    raise NotImplementedError
private_warehouse = os.path.normpath(os.path.join(private_root, 'warehouse'))
public_warehouse = os.path.normpath(os.path.join(public_root, 'warehouse'))
private_code_path = os.path.normpath(os.path.join(private_root, 'projects/multifactor'))
private_log_path = os.path.normpath(os.path.join(private_warehouse, 'logs'))
# private tank
private_db_path = os.path.normpath(os.path.join(private_warehouse, 'db'))
private_cache_path = os.path.normpath(os.path.join(private_warehouse, 'cache'))
private_h5root = os.path.normpath(os.path.join(private_warehouse, 'prod'))
private_strategy_path = os.path.normpath(os.path.join(private_root, 'strategy'))
private_trade_path = os.path.normpath(os.path.join(private_root, 'trade'))
private_factor_root = os.path.normpath(os.path.join(private_root, 'factors/prod'))
private_factor_ts_root = os.path.normpath(os.path.join(private_root, 'factors_ts/prod'))
flag_root_path = os.path.normpath(os.path.join(private_warehouse, 'flags'))
private_minute_per_stock_path = os.path.normpath(os.path.join(private_h5root, 'market/minute'))
macro_factor_path = os.path.normpath(os.path.join(private_h5root, 'market/macro/macro.db'))
derived_macro_factor_path = os.path.normpath(os.path.join(private_h5root, 'market/macro/derived_macro.db'))
open_market_data_path = os.path.normpath(os.path.join(private_h5root, 'market/open'))
minute_covariance_path = os.path.normpath(os.path.join(private_h5root, 'COV'))
dtw_cluster_path = os.path.normpath(os.path.join(private_h5root, 'CLUSTER/DTW'))
# futures tank
futures_contract_info_path = os.path.normpath(os.path.join(private_h5root, 'ETC/CHINA_FUTURES/WIND/futures_info.h5'))
futures_universe_path = os.path.normpath(os.path.join(private_h5root, 'ETC/CHINA_FUTURES/WIND/futures_universe.csv'))
futures_minute_tdb_csv_path = os.path.normpath(os.path.join(private_h5root, 'LOCAL_DATA/CSV/futures/minute/tdb'))
futures_minute_wind_csv_path = os.path.normpath(os.path.join(private_h5root, 'LOCAL_DATA/CSV/futures/minute/wind'))
# public tank
public_h5root = os.path.normpath(os.path.join(public_warehouse, 'prod'))
public_flag_root_path = os.path.normpath(os.path.join(public_h5root, 'LOCAL_DATA/FLAG'))
listing_delisting_path = os.path.normpath(os.path.join(public_h5root, 'ETC/CHINA_STOCK/WIND/STOCK_LISTING_DELISTING_DATE.h5'))
minute_per_stock_path = os.path.normpath(os.path.join(public_h5root, 'LOCAL_DATA/CSV/WIND/MINUTE/stock'))
minute_per_index_path = os.path.normpath(os.path.join(public_h5root, 'LOCAL_DATA/CSV/WIND/MINUTE/index'))
minute_stock_per_date_path = os.path.normpath(os.path.join(public_h5root, 'LOCAL_DATA/CSV/WIND/MINUTE/stock_perdate'))
minute_index_per_date_path = os.path.normpath(os.path.join(public_h5root, 'LOCAL_DATA/CSV/WIND/MINUTE/index_perdate'))
wind_news_per_date_path = os.path.normpath(os.path.join(public_h5root, 'LOCAL_DATA/CSV/WIND/WIND_FinancialNews'))

