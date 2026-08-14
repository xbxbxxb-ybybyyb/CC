import os
import pickle
import numpy as np
import pandas as pd
from math import isnan
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from alphagen_qlib.calculator import QLibStockDataCalculator
from alphagen_qlib.utils import load_alpha_pool_by_path, load_recent_data
from alphagen.data.expression import *
from alphagen_qlib.stock_data import StockData, FeatureType, TargetType
year = ['2018','2019']

for i in year:
    POOL_PATH = '/data/user/000021/gjx/alphagen-high时序也用filter版本/path/for/checkpoints/new_100_2_20240820005940/192512_steps_pool.json'
    # data, latest_date = load_recent_data(instrument='csi300', window_size=365, offset=1)

    target = Feature(TargetType.label)
    data1 = StockData(start_time=f'{i}-01-01',
                          end_time=f'{i}-12-31',
                          file_path='./high_data.pkl',
                          target_path='./label.pkl',
                          n_windows=72)

    calculator = QLibStockDataCalculator(data=data1, target=target)
    exprs = load_alpha_pool_by_path(POOL_PATH)

    # 这个里面还有计算因子收益率的感觉可以直接用
    ensemble_ric = calculator.calc_single_rIC(exprs)# 这个函数是为了这里计算每天每个因子定义的，前面alpha_pool那里要改掉【日频+高频】
    ensemble_alpha = calculator.calc_single_alpha(exprs)
    target_value = calculator.target_value
    df_alpha = data1.make_dataframe(ensemble_alpha)
    dates = sorted(list(set(df_alpha.index.get_level_values(0))))
    # df_target = pd.DataFrame(target_value.cpu().numpy(), index=dates
    #                          , columns=list(set(df_alpha.index.get_level_values(1))))
    # df = data1.load_exprs()
    # df['label'] = (df['next_close']-df['close'])/df['close']
    # df_target = df['label'].unstack(level=1)
    ensemble_ric = torch.stack(ensemble_ric).cpu().numpy()
    df_rIC = pd.DataFrame(ensemble_ric.T, index=dates, columns=exprs)
    df_alpha.columns = df_rIC.columns


output_dir = './result'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# df_alpha.to_pickle('./result/ensemble_alpha.pkl')  # 因子值
# df_rIC.to_pickle('./result/ensemble_ric.pkl')
# df_target.to_pickle('./result/df_target.pkl')
# exp = {f'factor{i}': exprs[i] for i in range(len(exprs))}
# with open('exprs.pkl', 'wb') as f:
#     pickle.dump(exp, f)

# df_alpha = pd.read_pickle('./result/ensemble_alpha.pkl')
# df_rIC = pd.read_pickle('./result/ensemble_ric.pkl')  # 加r！！

# df_target = pd.read_pickle('./result/df_target.pkl')
alpha_result = pd.DataFrame(index=df_alpha.columns, columns=['RankIC', 'RankICIR'])
alpha_result['RankIC'] = df_rIC.mean()
alpha_result['RankICIR'] = df_rIC.mean() / df_rIC.std()
alpha_result = alpha_result.reset_index()
alpha_result = alpha_result.iloc[:,[1,2,0]]
# alpha_result = alpha_result.sort_values(by=['RankIC'])
alpha_result = alpha_result.reindex(alpha_result['RankIC'].abs().sort_values(ascending=False).index)
alpha_result.to_csv('./result/alpha_result2019.csv')
