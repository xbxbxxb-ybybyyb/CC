# python3 setup.py build_ext --inplace
import sys
# multifactor所在路径
sys.path.insert(4, '/dfs/user/015626/JupyterNotebooks/utils/')
# 回测框架所在路径
sys.path.insert(4, '/data/user/015626/data/share/Code/git_space/strategy_back_test/')
from back_test_tick_multisignal_order import TS_BACK_TEST as v_multipath
import pandas as pd
print('start')
back_test_sdate, back_test_edate =  20230601, 20240101

ticker = 'IF.CFE'
signal2 = pd.read_hdf('/data/user/020529/share/signal/shift/IF_CRN_Predict55_reindex.h5').to_frame(name = 'raw')
signal2['pos_cash'] = 2.5e8
# signal2.loc['20231101':, 'pos_cash'] = 5e8

pos_dict2 = {(0, 0.15): (0, 0),
             (0.15, 0.25): (0, 0.05),
             (0.25, 0.61): (0, 1.0/10),
             (0.61, 0.67): (0.025, 1.0/10),
             (0.67, 0.73): (0.05, 1.0/10),
             (0.73, 0.8): (0.075, 1.0/10),
             (0.8,  100): (0.1, 1.0/10)}

# pos_dict2 = {(0, 0.5): (0, 0),
#              (0.5, 0.8): (0, 1.0/10),
#              (0.8,  100): (0.1, 1.0/10)}

initial_cash1 = 5e8

signal_list = [{'signal':signal2,'pos_dict':pos_dict2,'cash':initial_cash1}]

factor_name = ticker + '_xquant'
name = f'{factor_name}_prod'
a1 = v_multipath(signal_list, ticker=ticker, start_date=back_test_sdate, end_date=back_test_edate, tickslippage = 1.2,
                 save_signal_list = False, save_path=f'/data/user/015626/data/share/LOCAL_DATA/Mobius/backtest_prod_alg/{ticker}/{back_test_sdate}_{back_test_edate}/{name}',
                 name_prefix=name, max_wait_tick_num = 2)
result = a1.back_test() # 测试全部