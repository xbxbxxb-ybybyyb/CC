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
POOL_PATH = "/data/user/000021/gjx/alphagen-change-reward存档8.7反正还没改feature，这个能跑但结果不太理想/path/for/checkpoints/new_100_2_20240814220302/36864_steps_pool.json"
target = Feature(TargetType.label)
# data, latest_date = load_recent_data(instrument='csi300', window_size=365, offset=1)
data = StockData(start_time='2018-03-05',
                       end_time='2018-12-31',
                       file_path='/data/user/015585/share_file/for_sxs/low_frequency_all.pkl',
                       target_path='./label.pkl')
latest_date = '2019-12-31'

calculator = QLibStockDataCalculator(data=data, target=target)
amt = Feature(FeatureType.amt)
close = Feature(FeatureType.close)
free_float_shares = Feature(FeatureType.free_float_shares)
high = Feature(FeatureType.high)
low = Feature(FeatureType.low)
mkt_cap_ard = Feature(FeatureType.mkt_cap_ard)
open_ = Feature(FeatureType.open)
# pct_chg = Feature(FeatureType.pct_chg)
pre_close = Feature(FeatureType.pre_close)
# total_shares = Feature(FeatureType.total_shares)
turn = Feature(FeatureType.turn)
volume = Feature(FeatureType.volume)
open = Feature(FeatureType.open)
vwap = Feature(FeatureType.vwap)
# exprs = [Less(Log(Corr(mkt_cap_ard,Std(PercentileRank(pre_close),10),20)),vwap)]
# exprs = [PercentileRank(Kurt(ZScore(pre_close,10),20))]
exprs = [# 动量反转
        # Ref(close,20),
        #  Div(close,Mean(close,10)),
        #  Sum(Div(Sub(close,open),open),10),
        #  Sum(close,10),
        #  Sum(close,20),
        #  Sum(close,30),
        #  Sub(Mean(Filter(Sub(high,low),10,'>ts_mean'),1),Mean(Filter(Sub(high,low),10,'<ts_mean'),1)),
        #  Sub(Mean(Filter(Sub(high,low),30,'>ts_mean'),1),Mean(Filter(Sub(high,low),30,'<ts_mean'),1)),
        #  Ref(close,20)/Sum(Abs(close),20),
        #  Mean(PercentileRank(close),20),
        #  Mean(Rank(close,20),20),
        #  # 波动
        #  Std(close,20),
        # Std(close,30),
        # Std(close,10),
        #  Std(Filter(close,20,'>const_0'),1),
        # Std(Filter(close,10,'>const_0'),1),
        # Std(Filter(close,20,'<const_0'),1),
        # Std(Filter(close,10,'<const_0'),1),
        # Mean(Div(high,low),20),
        # Std(Div(high,low),20),
        # Mean(Div(Sub(high, Greater(open,close)),high),20),
        # Std(Div(Sub(high,Greater(open,close)),high),20),
        # Mean(Div(Sub(Less(open,close),low),low),20),
        # Std(Div(Sub(Less(open,close),low),low),20),
        # Mean(Div(Sub(close,low),low),20),
        # Std(Div(Sub(close,low),low),20),
        # Mean(Div(Sub(high, close) ,high), 20),
        # Std(Div(Sub(high, close) ,high), 20),
        # # 换手率因子
        # Std(turn,20),
        # Mean(turn,20),
        # Div(Mean(amt,20),Std(close,20)),
        # Mean(Div(close,amt),20),
        # Std(Div(close,amt),20),
        # # 量价相关性
        # Corr(turn,close,20),
        # # Corr(turn,Ref(close,-1),20),
        # Corr(turn,Ref(close,1),20),
        # Corr(Delta(turn,1),close,20),
        # # Corr(Delta(turn,1),Ref(close,-1),20),
        # Corr(Delta(turn,1),Ref(close,1),20),
        # 振幅因子
        # Mean(Sub(high,low),30),
        # Std(Sub(high,low),30),
        # Mean(Sub(high,low),20),
        # Std(Sub(high,low),20),
        # Mean(Sub(high,low),10),
        # Std(Sub(high,low),10),

]


# 这个里面还有计算因子收益率的感觉可以直接用
list_ic =[]
list_icir = []
for expr in exprs:
    expr = [expr]
    ensemble_alpha = calculator.calc_single_alpha_nonorm(expr)
    ensemble_ric = calculator.calc_single_rIC(expr)# 这个函数是为了这里计算每天每个因子定义的，前面alpha_pool那里要改掉【日频+高频】
    ensemble_ric = np.array([ic.item() for ic in ensemble_ric[0]])
    list_ic.append(np.mean(ensemble_ric))
    list_icir.append(np.mean(ensemble_ric)/np.std(ensemble_ric))
    print(expr)
    print(np.mean(ensemble_ric))
    print(np.mean(ensemble_ric)/np.std(ensemble_ric))

df = pd.DataFrame(index = exprs)
df['RankIC'] = list_ic
df['ICIR'] = list_icir
df['index'] = exprs
print(df)
df.to_csv('./人工日频2019.csv')
# df = pd.read_pickle('/data/user/015585/share_file/for_sxs/low_frequency_all.pkl')
# df['factor1_all'] = (df['low']-df['pre_close'])/df['pre_close']* np.log(df['volume']+1e-8)
# df = df[df.index.get_level_values(0)>='2019-01-02']
# print(df.loc[(slice(None),'000001.SZ'),:])
# print(df)
# target = pd.read_pickle('/data/user/000021/gjx/alphagen-change-reward存档8.7反正还没改feature，这个能跑但结果不太理想/label.pkl')
# target = target[target.index.get_level_values(0)>='2019-01-02']
# print(target)
# target = pd.DataFrame(target,columns=['label'])
# data = target.merge(df,left_index=True,right_index=True,how='left')
# print(data)

# 把外面和里面的一步步比较
# data['factor1'] = (data['low']-data['pre_close'])/data['pre_close']* np.log(data['volume']+1e-8)
#
#
# data = data[data.index.get_level_values(0)>'2019-01-01']
# arr = data['factor1'].values.reshape(-1,500)
# print(arr)
# print(arr==ensemble_alpha[0].cpu().numpy())
# target_value = calculator.target_value
# df_alpha = data.make_dataframe(ensemble_alpha)
# dates = sorted(list(set(df_alpha.index.get_level_values(0))))
# # df_target = pd.DataFrame(target_value.cpu().numpy(), index=dates
# #                          , columns=list(set(df_alpha.index.get_level_values(1))))
# df = data.load_exprs()
# df['label'] = (df['next_close']-df['close'])/df['close']
# df_target = df['label'].unstack(level=1)
# ensemble_ric = torch.stack(ensemble_ric).cpu().numpy()
# df_rIC = pd.DataFrame(ensemble_ric.T, index=dates, columns=exprs)
#
# output_dir = './result'
# if not os.path.exists(output_dir):
#     os.makedirs(output_dir)
#
# df_alpha.to_pickle('./result/ensemble_alpha.pkl')  # 因子值
# df_rIC.to_pickle('./result/ensemble_ric.pkl')
# df_target.to_pickle('./result/df_target.pkl')
# exp = {f'factor{i}': exprs[i] for i in range(len(exprs))}
# with open('exprs.pkl', 'wb') as f:
#     pickle.dump(exp, f)
#
# df_alpha = pd.read_pickle('./result/ensemble_alpha.pkl')
# df_rIC = pd.read_pickle('./result/ensemble_ric.pkl')  # 加r！！
# df_alpha.columns = df_rIC.columns
# df_target = pd.read_pickle('./result/df_target.pkl')
# alpha_result = pd.DataFrame(index=df_alpha.columns, columns=['RankIC', 'RankICIR'])
# alpha_result['RankIC'] = df_rIC.mean()
# alpha_result['RankICIR'] = df_rIC.mean() / df_rIC.std()
# alpha_result.to_pickle('./result/alpha_result.pkl')
#
# print(alpha_result.index)
# print(alpha_result.sort_values(by=['RankIC']))
# dff = alpha_result.reset_index()
# top5 = dff.nlargest(5,'RankIC')
# print(top5.index)
# list1 = top5.index.tolist()
# i = list1[0]
#
# # 假设df_alpha有100列
# num_factors = df_alpha.shape[1]
# group_size = 2  # 每张大图包含的子图数量
#
# # 检查文件夹是否存在，如果不存在则创建
# output_dir = './fig'
# if not os.path.exists(output_dir):
#     os.makedirs(output_dir)
#
# df_rIC_cumsum = df_rIC.cumsum()
#
# plt.figure(figsize=(10, 10))  # 设置大图尺寸
#  # 实际的因子索引
# plt.plot(df_rIC_cumsum.index, df_rIC_cumsum.iloc[:, i])
# # ax.legend()
# plt.title(f'factor{i}')
# # ax.set_xticklabels(ax.get_xticks(), rotation=45)
# plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
# plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
# plt.xticks(rotation=45)
#
# plt.tight_layout()
# plt.show()
# plt.savefig(f'./fig/累积IC{i}')
#
# '''
# 画分组收益率
# '''
# grouped_averages = pd.DataFrame(index=df_rIC.index, columns=[f'Group {i + 1}' for i in range(10)])
# dff = df_alpha.iloc[:, i].unstack()
# turn_group = []
# pre_groups_idx = None
#
# for date, row in dff.iterrows():
#     label = df_target.loc[date]
#     label1 = label.dropna(axis=0)
#     # row1 = row[row!=0.]
#     row1 = row[~row.isnan()]
#     idx = label1.index.intersection(row1.index)
#     row = row.loc[idx]
#     label = label.loc[idx]
#     # print(len(idx))
#     sorted_indices = row.argsort()
#     sorted_df2_row = label.iloc[sorted_indices]
#     sorted_idx =  list(sorted_df2_row.index)
#
#     groups = np.array_split(sorted_df2_row, 10)
#     groups_idx = np.array_split(sorted_idx, 10)
#     if pre_groups_idx is not None:
#         list_groups_sets = [set(group) for group in pre_groups_idx]
#         list1_groups_sets = [set(group1) for group1 in groups_idx]
#
#         # 计算每一组的变化率
#         diff_counts = np.array([len(group1 - group) for group, group1 in zip(list_groups_sets, list1_groups_sets)])
#         group_lengths = np.array([len(group) for group in list_groups_sets])
#         change_rates = diff_counts / group_lengths
#         turn_group.append(change_rates)
#
#     pre_groups_idx = groups_idx
#     group_average = [group.mean() for group in groups]
#     grouped_averages.loc[date] = group_average
#
#
# turn_group = np.array(turn_group).mean(axis=0)
# print('换手率',turn_group)
#
# grouped_averages.iloc[0,:] = 0
# grouped_averages += 1
# dff_IC = grouped_averages.cumprod()
# # 在最前面增加一行0
# new_row = pd.DataFrame(np.zeros((1, len(dff_IC.columns))), index=[dff_IC.index.min() - pd.Timedelta(days=1)],
#                        columns=dff_IC.columns)
# dff_IC = pd.concat([new_row, dff_IC])
# dff_IC['l-s'] = (dff_IC.iloc[:, -1] - dff_IC.iloc[:, 0]) * (1 if alpha_result.iloc[i, 1] > 0 else -1)
#
# plt.figure(figsize=(10, 10))  # 设置大图尺寸
# for col_index in range(len(dff_IC.columns)):
#     if dff_IC.columns[col_index]!='l-s':
#         plt.plot(dff_IC.index, dff_IC.iloc[:, col_index], label=dff_IC.columns[col_index])
#     else:
#         plt.plot(dff_IC.index, dff_IC.iloc[:, col_index], label=dff_IC.columns[col_index], color='black',linewidth=2)
# plt.legend()
# plt.title(f'factor{i}')
# # ax.set_xticklabels(ax.get_xticks(), rotation=45)
# plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
# plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
# plt.xticks(rotation=45)
#
# plt.tight_layout()
# plt.show()
# plt.savefig(f'./fig/figure{i}')
#
#
