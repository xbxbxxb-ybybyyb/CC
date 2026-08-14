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

# POOL_PATH = '/DATA/xuehy/logs/kdd_csi300_20_4_20230410071036/301056_steps_pool.json'
# POOL_PATH = "/data/user/000021/gjx/alphagen-change-reward存档8.7反正还没改feature，这个能跑但结果不太理想/path/for/checkpoints/new_100_2_20240815165001/262144_steps_pool.json"
POOL_PATH = '/data/user/000021/gjx/alphagen-high时序也用filter版本/path/for/checkpoints/new_100_2_20240827010313/198656_steps_pool.json'
# data, latest_date = load_recent_data(instrument='csi300', window_size=365, offset=1)

target = Feature(TargetType.label)
data1 = StockData(start_time='2018-01-01',
                      end_time='2018-12-31',
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

output_dir = './result'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

df_alpha.to_pickle('./result/ensemble_alpha.pkl')  # 因子值
df_rIC.to_pickle('./result/ensemble_ric.pkl')
# df_target.to_pickle('./result/df_target.pkl')
exp = {f'factor{i}': exprs[i] for i in range(len(exprs))}
with open('exprs.pkl', 'wb') as f:
    pickle.dump(exp, f)

df_alpha = pd.read_pickle('./result/ensemble_alpha.pkl')
df_rIC = pd.read_pickle('./result/ensemble_ric.pkl')  # 加r！！
df_alpha.columns = df_rIC.columns
# df_target = pd.read_pickle('./result/df_target.pkl')
alpha_result = pd.DataFrame(index=df_alpha.columns, columns=['RankIC', 'RankICIR'])
alpha_result['RankIC'] = df_rIC.mean()
alpha_result['RankICIR'] = df_rIC.mean() / df_rIC.std()
alpha_result = alpha_result.reset_index()
alpha_result = alpha_result.iloc[:,[1,2,0]]
# alpha_result = alpha_result.sort_values(by=['RankIC'])
alpha_result = alpha_result.reindex(alpha_result['RankIC'].abs().sort_values(ascending=False).index)
alpha_result.to_csv('./result/alpha_result2018.csv')

print(alpha_result.index)
print(alpha_result.sort_values(by=['RankIC']))
dff = alpha_result.reset_index()
top5 = dff.nlargest(5,'RankIC')
print(top5.index)
list1 = top5.index.tolist()
i = list1[0]

# 假设df_alpha有100列
num_factors = df_alpha.shape[1]
group_size = 2  # 每张大图包含的子图数量

# 检查文件夹是否存在，如果不存在则创建
output_dir = './fig'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

df_rIC_cumsum = df_rIC.cumsum()

plt.figure(figsize=(10, 10))  # 设置大图尺寸
 # 实际的因子索引
plt.plot(df_rIC_cumsum.index, df_rIC_cumsum.iloc[:, i])
# ax.legend()
plt.title(f'factor{i}')
# ax.set_xticklabels(ax.get_xticks(), rotation=45)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()
plt.savefig(f'./fig/累积IC{i}')

'''
画分组收益率
'''
grouped_averages = pd.DataFrame(index=df_rIC.index, columns=[f'Group {i + 1}' for i in range(10)])
dff = df_alpha.iloc[:, i].unstack()
turn_group = []
pre_groups_idx = None

for date, row in dff.iterrows():
    label = df_target.loc[date]
    label1 = label.dropna(axis=0)
    # row1 = row[row!=0.]
    row1 = row[~row.isnan()]
    idx = label1.index.intersection(row1.index)
    row = row.loc[idx]
    label = label.loc[idx]
    # print(len(idx))
    sorted_indices = row.argsort()
    sorted_df2_row = label.iloc[sorted_indices]
    sorted_idx =  list(sorted_df2_row.index)

    groups = np.array_split(sorted_df2_row, 10)
    groups_idx = np.array_split(sorted_idx, 10)
    if pre_groups_idx is not None:
        list_groups_sets = [set(group) for group in pre_groups_idx]
        list1_groups_sets = [set(group1) for group1 in groups_idx]

        # 计算每一组的变化率
        diff_counts = np.array([len(group1 - group) for group, group1 in zip(list_groups_sets, list1_groups_sets)])
        group_lengths = np.array([len(group) for group in list_groups_sets])
        change_rates = diff_counts / group_lengths
        turn_group.append(change_rates)

    pre_groups_idx = groups_idx
    group_average = [group.mean() for group in groups]
    grouped_averages.loc[date] = group_average


turn_group = np.array(turn_group).mean(axis=0)
print('换手率',turn_group)

grouped_averages.iloc[0,:] = 0
grouped_averages += 1
dff_IC = grouped_averages.cumprod()
# 在最前面增加一行0
new_row = pd.DataFrame(np.zeros((1, len(dff_IC.columns))), index=[dff_IC.index.min() - pd.Timedelta(days=1)],
                       columns=dff_IC.columns)
dff_IC = pd.concat([new_row, dff_IC])
dff_IC['l-s'] = (dff_IC.iloc[:, -1] - dff_IC.iloc[:, 0]) * (1 if alpha_result.iloc[i, 1] > 0 else -1)

plt.figure(figsize=(10, 10))  # 设置大图尺寸
for col_index in range(len(dff_IC.columns)):
    if dff_IC.columns[col_index]!='l-s':
        plt.plot(dff_IC.index, dff_IC.iloc[:, col_index], label=dff_IC.columns[col_index])
    else:
        plt.plot(dff_IC.index, dff_IC.iloc[:, col_index], label=dff_IC.columns[col_index], color='black',linewidth=2)
plt.legend()
plt.title(f'factor{i}')
# ax.set_xticklabels(ax.get_xticks(), rotation=45)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()
plt.savefig(f'./fig/figure{i}')


