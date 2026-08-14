# @Time : 2021/9/6 14:33
# @Author : Zhichen Lu
# @File : IndustryMatrix.py

import sys; print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend(['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python', '/data/user/015664/TriggeredTrading/StrongStockModel', '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master', '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/FactorCalculator_', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/training', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/preprocess', '/data/user/015664/TriggeredTrading'])

import pandas as pd
from dataApi.getData import get_daily_1factor,trans_windcode2int,trans_int2windcode
from MillenniumFalcon.IndustryMatrixDaily import get_historical_matrix
from dataApi.tradeDate import get_date_range, get_pre_trade_date, get_recent_trade_date
from dataApi.sendInfo import send_message
from dataApi.stockList import get_all_stock_ever_appear

sw = get_daily_1factor('SW1')


def out_matrix(today):
    _code_list = get_all_stock_ever_appear(today)
    relation_arr_dict = get_historical_matrix(sw.loc[[today], _code_list], return_type='df')
    relation_df = relation_arr_dict[today]
    relation_df.index = relation_df.index.map(trans_int2windcode)
    relation_df.columns = relation_df.columns.map(trans_int2windcode)
    from ExtraTools import get_path_conf
    path_conf = get_path_conf('/data/group/800319/strategy_local_path3/', create=True)
    # pd.to_pickle(pd.Series([]),path_conf['local_config_path']+f'morning_model/val_sign/{get_pre_trade_date(today,-1)}.pkl')
    pd.to_pickle({'sw1': relation_df}, path_conf['matrix_conf'] + f'{today}.pkl')
    send_message(['015664'], f'{today} 关系矩阵生成成功 {relation_df.shape}')
if __name__ == '__main__':
    today = get_recent_trade_date()
    out_matrix(today)
    # for date in get_date_range(20211117,20211124):
    #     out_matrix(date)






